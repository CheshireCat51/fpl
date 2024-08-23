from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text, Connection
import mysql.connector
from utils import except_future_gw
from bootstrap import Bootstrap
import pandas as pd


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_23/24')
prev_cnx = engine.connect()

engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_24/25')
current_cnx = engine.connect()

write_conn = mysql.connector.connect(host='localhost', user='app', password=os.environ.get('DB_PASS'), database='fpl_model_24/25')

# Weights
last_6_weight = 0.7
older_weight = 0.3

# Load maps
player_map = pd.read_csv('player_map.csv')
squad_map = pd.read_csv('squad_map.csv')


def read_defence_strength(squad_id: int, gw_id: int):

    """Returns goals conceded against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    return execute_from_str(f'SELECT defence_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}', current_cnx).fetchone()[0]


def read_attack_strength(squad_id: int, gw_id: int):

    """Returns goals scored against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    return execute_from_str(f'SELECT attack_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}', current_cnx).fetchone()[0]


def read_mean_strengths(gw_id: int):

    """Returns goals conceded against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    results = execute_from_str(f'SELECT AVG(attack_strength), AVG(defence_strength) FROM squad_gameweek WHERE gameweek_id = {gw_id}', current_cnx).fetchall()[0]

    return (float(results[0]), float(results[1]))


def read_expected_mins(current_player_id: int, prev_player_id: int | None, gw_id: int):

    """Returns mean mins played given that the player started and the std of these values.
        Previous 6 gameweeks are weighted at 70% and all gameweeks prior to that at 30%."""

    current_condition = f'pgw.gameweek_id >= ({gw_id}-6)'
    query = f'SELECT \
                SUM(CASE WHEN {current_condition} THEN pgw.minutes_played * {last_6_weight} ELSE pgw.minutes_played * {older_weight} END)/SUM(CASE WHEN {current_condition} THEN {last_6_weight} ELSE {older_weight} END), \
                STD(pgw.minutes_played) \
            FROM player_gameweek pgw \
            WHERE pgw.player_id = {current_player_id} AND pgw.started = 1 AND pgw.gameweek_id < {gw_id}'
    current_results = execute_from_str(query, current_cnx).fetchall()[0]
    
    if prev_player_id is not None:
        prev_condition = f'pgw.gameweek_id >= {gw_id+1}'
        query = f'SELECT \
                    AVG(pgw.minutes_played), \
                    STD(pgw.minutes_played) \
                FROM player_gameweek pgw \
                WHERE pgw.player_id = {prev_player_id} AND pgw.started = 1 AND {prev_condition}'
        prev_results = execute_from_str(query, prev_cnx).fetchall()[0]
        return (weighted_average(float(prev_results[0]), float(current_results[0])), weighted_average(float(prev_results[1]), float(current_results[1])))
    
    else:
        return (float(current_results[0]), float(current_results[1]))


def read_start_proportion(current_player_id: int, prev_player_id: int | None, gw_id: int):

    """Returns proportion that player started when they played."""

    current_condition = f'pgw.gameweek_id >= ({gw_id}-6)'
    query = f'SELECT \
                SUM(CASE WHEN {current_condition} THEN pgw.started * {last_6_weight} ELSE pgw.started * {older_weight} END)/SUM(CASE WHEN {current_condition} THEN {last_6_weight} ELSE {older_weight} END) \
            FROM player_gameweek pgw \
            WHERE pgw.player_id = {current_player_id} AND pgw.started IS NOT NULL AND pgw.gameweek_id < {gw_id}'
    current_results = execute_from_str(query, current_cnx).fetchall()[0]

    if prev_player_id is not None:
        prev_condition = f'pgw.gameweek_id >= {gw_id+1}'
        query = f'SELECT \
                    AVG(pgw.started) \
                FROM player_gameweek pgw \
                WHERE pgw.player_id = {prev_player_id} AND pgw.started IS NOT NULL AND {prev_condition}'
        prev_results = execute_from_str(query, prev_cnx).fetchall()[0]
        return weighted_average(float(prev_results[0]), float(current_results[0]))
    
    else:
        return float(current_results[0])


def read_attacking_stats_per_90(current_player_id: int, prev_player_id: int | None):

    """Returns attacking stats per 90."""

    current_season = execute_from_str(f'SELECT p.npxG_per_90, p.xA_per_90 \
                                        FROM player p \
                                        WHERE p.id = {current_player_id}', current_cnx).fetchall()[0]

    if prev_player_id is not None:
        prev_season = execute_from_str(f'SELECT p.npxG_per_90, p.xA_per_90 \
                                        FROM player p \
                                        WHERE p.id = {prev_player_id}', prev_cnx).fetchall()[0]
        return weighted_average(prev_season[0], current_season[0]), weighted_average(prev_season[1], current_season[1])
    
    else:
        return (float(current_season[0]), float(current_season[1]))


def read_penalty_stats_per_90(current_squad_id: int, prev_squad_id: int | None):

    """Returns penalty attempts per 90 for given squad."""

    current_season = float(execute_from_str(f'SELECT AVG(pgw.penalty_attempts) \
                                                FROM player p \
                                                JOIN player_gameweek pgw ON p.id = pgw.player_id \
                                                WHERE p.squad_id = {current_squad_id}', current_cnx).fetchone()[0])

    if prev_squad_id is not None:
        prev_season = float(execute_from_str(f'SELECT AVG(pgw.penalty_attempts) \
                                                FROM player p \
                                                JOIN player_gameweek pgw ON p.id = pgw.player_id \
                                                WHERE p.squad_id = {prev_squad_id}', prev_cnx).fetchone()[0])
    
        return weighted_average(prev_season, current_season)

    else:
        return current_season


def read_all_player_ids():

    """Returns all player ids."""

    results = execute_from_str('SELECT id FROM player', current_cnx).fetchall()

    return [i[0] for i in results]


# def read_player_gameweek_ids(gameweek_id: int, player_id: int):

#     """Returns player gameweek ids for given player on given gameweek."""

#     results = execute_from_str(f'SELECT id from player_gameweek WHERE gameweek_id = {gameweek_id} AND player_id = {player_id}')

#     return [i[0] for i in results]


def read_squad_gameweek_id(squad_id: int, gameweek_id: int, opposition_id: int):

    """Returns player gameweek ids for given player on given gameweek."""

    return int(execute_from_str(f'SELECT id FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gameweek_id} AND opposition_id = {opposition_id}', current_cnx).fetchone()[0])


def read_prev_player_id(player_name: str):

    """Get player id from previous season."""

    player_name = player_map[player_map['API'] == player_name]['FBRef'].values[0]
        
    query = f'SELECT id FROM player WHERE name = "{player_name}"'

    try:
        prev_id = int(execute_from_str(query, prev_cnx).fetchone()[0])
    except Exception as e:
        print(f'{player_name} was not in prem last season.')
        return None
    else:
        return prev_id


def read_prev_squad_id(squad_name: str):

    """Get squad id from previous season."""

    squad_name = squad_map[squad_map['API'] == squad_name]['FBRef'].values[0]

    query = f'SELECT id FROM squad WHERE name = "{squad_name}"'

    try:
        prev_id = int(execute_from_str(query, prev_cnx).fetchone()[0])
    except Exception as e:
        print(f'{squad_name} were not in prem last season.')
        return None
    else:
        return prev_id


def weighted_average(prev_val: float, current_val: float):

    """Weighted average between previous and current season."""

    prev_weight = 0.9
    current_weight = 0.1

    weighted_average = (prev_weight*prev_val + current_weight*current_val)/(prev_weight+current_weight)

    return weighted_average


def execute_from_str(query_str: str, cnx: Connection):

    """Execute query from string."""

    return cnx.execute(text(query_str))


def execute_from_file(query_file_path: str, args: tuple):

    """Read SQL file, insert args and execute."""
    
    with write_conn.cursor() as cursor:
        with open(f'./sql/{query_file_path}', 'r') as query_file:
            query = query_file.read()

        filled_query = query % args
        # print(filled_query)
        cursor.execute(filled_query)
    
    write_conn.commit()