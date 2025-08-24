from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text, Connection, CursorResult
import mysql.connector
from utils import except_future_gw
from bootstrap import Bootstrap
import pandas as pd


load_dotenv()

prev_engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_2425')
current_engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_2526')

write_conn = mysql.connector.connect(host='localhost', user='app', password=os.environ.get('DB_PASS'), database='fpl_model_2526')

# Weights (a 50-50 weighting assumes there is no such thing as "form")
last_6_weight = 0.50
older_weight = 0.50

# Minutes are weighted towards the last 6 as short-term minutes variance tends to be low
# E.g. if Saka gets injured, Nwaneri is likely to play more minutes until Saka recovers despite Nwaneri having low minutes historically. 
# We therefore need to quickly boost Nwaneri's xMins by weighting his recent minutes more highly.
last_6_mins_weight = 0.7
older_mins_weight = 0.3

# Load maps
player_map = pd.read_csv('player_map.csv')
squad_map = pd.read_csv('squad_map.csv')


def init_cnx(engine: str = 'current'):

    """Connect to the database."""

    try:
        if engine == 'current':
            cnx = current_engine.connect()
        elif engine == 'previous':
            cnx = prev_engine.connect()
        else:
            raise ValueError('Engine must be either "current" or "previous".')
    except mysql.connector.Error as err:
        print(f'Error: {err}')
    else:
        return cnx


def read_defence_strength(squad_id: int, gw_id: int, current_cnx: Connection = init_cnx()):

    """Returns goals conceded against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    return execute_from_str(f'SELECT defence_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}', current_cnx)[0]


def read_attack_strength(squad_id: int, gw_id: int, current_cnx: Connection = init_cnx()):

    """Returns goals scored against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    return execute_from_str(f'SELECT attack_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}', current_cnx)[0]


def read_mean_strengths(gw_id: int, current_cnx: Connection = init_cnx()):

    """Returns average team attack and defence strengths in order to adjust probability of goals for/against."""

    gw_id = except_future_gw(gw_id)

    results = execute_from_str(f'SELECT AVG(attack_strength), AVG(defence_strength) FROM squad_gameweek WHERE gameweek_id = {gw_id}', current_cnx)

    return float(results[0]), float(results[1])


def read_expected_mins(current_player_id: int, prev_player_id: int | None, gw_id: int, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns mean mins played given that the player started and the std of these values.
        Previous 6 gameweeks are weighted at 70% and all gameweeks prior to that at 30%."""
    
    gw_id = except_future_gw(gw_id)

    current_condition = f'pgw.gameweek_id >= ({gw_id}-6)'
    query = f'SELECT \
                SUM(CASE WHEN {current_condition} THEN pgw.minutes_played * {last_6_mins_weight} ELSE pgw.minutes_played * {older_mins_weight} END)/SUM(CASE WHEN {current_condition} THEN {last_6_mins_weight} ELSE {older_mins_weight} END), \
                STD(pgw.minutes_played) \
            FROM player_gameweek pgw \
            WHERE pgw.player_id = {current_player_id} AND pgw.started = 1 AND pgw.gameweek_id < {gw_id}'
    current_results = execute_from_str(query, current_cnx)
    
    if prev_player_id is not None:
        query = f'SELECT \
                    AVG(pgw.minutes_played), \
                    STD(pgw.minutes_played) \
                FROM player_gameweek pgw \
                WHERE pgw.player_id = {prev_player_id} AND pgw.started = 1'
        prev_results = execute_from_str(query, prev_cnx)
        return weighted_average(prev_results[0], current_results[0], 'mins'), weighted_average(prev_results[1], current_results[1], 'mins')
    
    else:
        return float(current_results[0]), float(current_results[1])


def read_start_proportion(current_player_id: int, prev_player_id: int | None, gw_id: int, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns proportion of games that player started when they played."""

    gw_id = except_future_gw(gw_id)

    current_condition = f'pgw.gameweek_id >= ({gw_id}-6)'
    query = f'SELECT \
                SUM(CASE WHEN {current_condition} THEN pgw.started * {last_6_mins_weight} ELSE pgw.started * {older_mins_weight} END)/SUM(CASE WHEN {current_condition} THEN {last_6_mins_weight} ELSE {older_mins_weight} END) \
            FROM player_gameweek pgw \
            WHERE pgw.player_id = {current_player_id} AND pgw.started IS NOT NULL'
    current_results = execute_from_str(query, current_cnx)

    if prev_player_id is not None:
        query = f'SELECT \
                    AVG(pgw.started) \
                FROM player_gameweek pgw \
                WHERE pgw.player_id = {prev_player_id} AND pgw.started IS NOT NULL'
        prev_results = execute_from_str(query, prev_cnx)
        return weighted_average(prev_results[0], current_results[0], 'mins')
    
    else:
        return float(current_results[0])


def read_attacking_stats_per_90(current_player_id: int, prev_player_id: int | None, gw_id: int, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns attacking stats per 90. Uses 38-match sample as FPLReview suggests 40 matches is optimal but difficult to integrate here.
    https://fplreview.com/how-accurately-does-xg-data-indicate-player-goalscoring-potential/."""

    gw_id = except_future_gw(gw_id)
    
    current_condition = f'pgw.gameweek_id >= ({gw_id}-6)'
    current_season = execute_from_str(f'SELECT \
                                            SUM(CASE WHEN {current_condition} THEN ((pgw.npxG/pgw.minutes_played)*90*{last_6_weight}) ELSE ((pgw.npxG/pgw.minutes_played)*90*{older_weight}) END)/SUM(CASE WHEN {current_condition} THEN {last_6_weight} ELSE {older_weight} END), \
                                            SUM(CASE WHEN {current_condition} THEN ((pgw.xA/pgw.minutes_played)*90*{last_6_weight}) ELSE ((pgw.xA/pgw.minutes_played)*90*{older_weight}) END)/SUM(CASE WHEN {current_condition} THEN {last_6_weight} ELSE {older_weight} END) \
                                        FROM player_gameweek pgw \
                                        WHERE pgw.player_id = {current_player_id}', current_cnx)

    if prev_player_id is not None:
        prev_condition = f'pgw.gameweek_id >= {gw_id+1}'
        prev_season = execute_from_str(f'SELECT (SUM(pgw.npxG)/SUM(pgw.minutes_played))*90, (SUM(pgw.xA)/SUM(pgw.minutes_played))*90 \
                                        FROM player_gameweek pgw \
                                        WHERE pgw.player_id = {prev_player_id} AND {prev_condition}', prev_cnx)
        return weighted_average(prev_season[0], current_season[0], 'x'), weighted_average(prev_season[1], current_season[1], 'x')
    
    else:
        return float(current_season[0]), float(current_season[1])
    

def read_attacking_stats_share(current_player_id: int, prev_player_id: int | None, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Read player's share of squad's attacking data in order to adjust correctly."""

    current_season = execute_from_str(f'SELECT (p.npxG/s.npxG), (p.xA/s.xA) \
                                        FROM player p \
                                        JOIN squad s ON p.squad_id = s.id \
                                        WHERE p.id = {current_player_id}', current_cnx)

    if prev_player_id is not None:
        prev_season = execute_from_str(f'SELECT (p.npxG/s.npxG), (p.xA/s.xA) \
                                        FROM player p \
                                        JOIN squad s ON p.squad_id = s.id \
                                        WHERE p.id = {prev_player_id}', prev_cnx)
        return weighted_average(prev_season[0], current_season[0], 'x'), weighted_average(prev_season[1], current_season[1], 'x')
    
    else:
        return float(current_season[0]), float(current_season[1])


def read_squad_pen_attempts_per_90(current_squad_id: int, prev_squad_id: int | None, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns penalty attempts per 90 for given squad."""

    current_season = execute_from_str(f'SELECT (s.penalty_attempts/s.matches_played) \
                                                FROM squad s \
                                                WHERE s.id = {current_squad_id}', current_cnx)[0]
    
    if prev_squad_id is not None:
        prev_season = execute_from_str(f'SELECT (s.penalty_attempts/s.matches_played) \
                                                FROM squad s \
                                                WHERE s.id = {prev_squad_id}', prev_cnx)[0]
    
        return weighted_average(prev_season, current_season, 'x')

    else:
        return current_season
    

def read_pen_attempts_per_90(current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns mean penalty attempts per 90 across all squads."""

    query = 'SELECT AVG(s.penalty_attempts/s.matches_played) FROM squad s'

    current_season = float(execute_from_str(query, current_cnx)[0])
    prev_season = float(execute_from_str(query, prev_cnx)[0])
    
    return weighted_average(prev_season, current_season, 'x')


def read_cbit_per_90(current_player_id: int, prev_player_id: int | None, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns clearances, blocks, interceptions and tackles per 90."""

    current_season = execute_from_str(f'SELECT AVG(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.tackles), STD(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.tackles) FROM player_gameweek pgw WHERE pgw.player_id = {current_player_id}', current_cnx)

    if prev_player_id is not None:
        prev_season = execute_from_str(f'SELECT AVG(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.tackles), STD(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.tackles) FROM player_gameweek pgw WHERE pgw.player_id = {prev_player_id}', prev_cnx)
        return weighted_average(prev_season[0], current_season[0], 'x'), weighted_average(prev_season[1], current_season[1], 'x')
    
    else:
        return float(current_season[0]), float(current_season[1])
    

def read_cbirt_per_90(current_player_id: int, prev_player_id: int | None, current_cnx: Connection = init_cnx(), prev_cnx: Connection = init_cnx('previous')):

    """Returns clearances, blocks, interceptions, recoveries andtackles per 90."""

    current_season = execute_from_str(f'SELECT AVG(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.recoveries + pgw.tackles), STD(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.recoveries + pgw.tackles) FROM player_gameweek pgw WHERE pgw.player_id = {current_player_id}', current_cnx)

    if prev_player_id is not None:
        prev_season = execute_from_str(f'SELECT AVG(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.recoveries + pgw.tackles), STD(pgw.clearances + pgw.blocks + pgw.interceptions + pgw.recoveries + pgw.tackles) FROM player_gameweek pgw WHERE pgw.player_id = {prev_player_id}', prev_cnx)
        return weighted_average(prev_season[0], current_season[0], 'x'), weighted_average(prev_season[1], current_season[1], 'x')
    
    else:
        return float(current_season[0]), float(current_season[1])


def read_all_player_ids(current_cnx: Connection = init_cnx()):

    """Returns all player ids."""

    results = execute_from_str('SELECT id FROM player', current_cnx, stat_query=False, fetchall=True)

    return [i[0] for i in results]


def read_all_player_names(current_cnx: Connection = init_cnx()):

    """Returns all player names."""

    results = execute_from_str('SELECT name FROM player', current_cnx, stat_query=False, fetchall=True)

    return [i[0] for i in results]


# def read_player_gameweek_ids(gameweek_id: int, player_id: int):

#     """Returns player gameweek ids for given player on given gameweek."""

#     results = execute_from_str(f'SELECT id from player_gameweek WHERE gameweek_id = {gameweek_id} AND player_id = {player_id}')

#     return [i[0] for i in results]


def read_squad_gameweek_id(squad_id: int, opposition_id: int, venue: str, current_cnx: Connection = init_cnx()):

    """Returns player gameweek ids for given player on given gameweek."""

    query = f'SELECT id FROM squad_gameweek WHERE squad_id = {squad_id} AND opposition_id = {opposition_id} AND venue = "{venue}"'
    try:
        squad_gameweek_id = int(execute_from_str(query, current_cnx, stat_query=False)[0])
        return squad_gameweek_id
    except TypeError:
        return None


def read_prev_player_id(player_name: str, prev_cnx: Connection = init_cnx('previous')):

    """Get player id from previous season."""

    try:
        player_name = player_map[player_map['API'] == player_name]['FBRef'].values[0]
    except IndexError:
        return None
        
    query = f'SELECT id FROM player WHERE name = "{player_name}"'

    try:
        prev_id = int(execute_from_str(query, prev_cnx, stat_query=False)[0])
    except Exception as e:
        print(f'{player_name} was not in prem last season.')
        return None
    else:
        return prev_id


def read_prev_squad_id(squad_name: str, prev_cnx: Connection = init_cnx('previous')):

    """Get squad id from previous season."""

    squad_name = squad_map[squad_map['API'] == squad_name]['FBRef'].values[0]

    query = f'SELECT id FROM squad WHERE name = "{squad_name}"'

    try:
        prev_id = int(execute_from_str(query, prev_cnx, stat_query=False)[0])
    except Exception as e:
        print(f'{squad_name} were not in prem last season.')
        return None
    else:
        return prev_id


def weighted_average(prev_val: float, current_val: float, weights: str):

    """Weighted average between previous and current season. See weight progression graphs in ./weight_prog."""

    current_gw_id = Bootstrap.get_current_gw_id()
    next_gw_id = current_gw_id + 1

    if weights == 'x':
        prev_weight = -(5/32)*(next_gw_id - 38)
        current_weight = next_gw_id - 1
    elif weights == 'mins':
        prev_weight = (38/next_gw_id) - 1
        current_weight = 38 - (38/next_gw_id)

    # Ensure types can be multiplied
    current_val = float(current_val)
    if prev_val is None:
        prev_val = 0
        prev_weight = 0
    else:
        prev_val = float(prev_val)

    weighted_average = (prev_weight*prev_val + current_weight*current_val)/(prev_weight+current_weight)

    return weighted_average


def execute_from_str(query_str: str, cnx: Connection, stat_query: bool = True, fetchall: bool = False) -> CursorResult:

    """Execute query from string. Stat_query is used to dictate whether the query returns an empty result or a zero."""

    if fetchall:
        result = cnx.execute(text(query_str)).fetchall()
    else:
        result = cnx.execute(text(query_str)).fetchone()

    if stat_query and all(i is None for i in result):
        result = tuple(0 for _ in result)
    
    return result


def execute_from_file(query_file_path: str, args: tuple):

    """Read SQL file, insert args and execute."""
    
    with write_conn.cursor() as cursor:
        with open(f'./sql/{query_file_path}', 'r') as query_file:
            query = query_file.read()

        filled_query = query % args
        # print(filled_query)
        cursor.execute(filled_query)
    
    write_conn.commit()