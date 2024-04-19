from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import mysql.connector
from utils import except_future_gw


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_23/24')
cnx = engine.connect()

write_conn = mysql.connector.connect(host='localhost', user='app', password=os.environ.get('DB_PASS'), database='fpl_model_23/24')

# Weights
last_6_weight = 0.7
older_weight = 0.3


def read_defence_strength(squad_id: int, gw_id: int):

    """Returns goals conceded against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    return execute_from_str(f'SELECT defence_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}').fetchone()[0]


def read_attack_strength(squad_id: int, gw_id: int):

    """Returns goals scored against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    return execute_from_str(f'SELECT attack_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}').fetchone()[0]


def read_mean_strengths(gw_id: int):

    """Returns goals conceded against average prem opponent for given squad."""

    gw_id = except_future_gw(gw_id)

    results = execute_from_str(f'SELECT AVG(attack_strength), AVG(defence_strength) FROM squad_gameweek WHERE gameweek_id = {gw_id}').fetchall()[0]

    return (float(results[0]), float(results[1]))


def read_expected_mins(player_id: int, gw_id: int):

    """Returns mean mins played given that the player started and the std of these values.
        Previous 6 gameweeks are weighted at 70% and all gameweeks prior to that at 30%."""

    condition = f'pgw.gameweek_id >= ({gw_id}-6)'
    
    results = execute_from_str(f'SELECT \
                                    SUM(CASE WHEN {condition} THEN pgw.minutes_played * {last_6_weight} ELSE pgw.minutes_played * {older_weight} END)/SUM(CASE WHEN {condition} THEN {last_6_weight} ELSE {older_weight} END), \
                                    STD(pgw.minutes_played) \
                                FROM player_gameweek pgw \
                                WHERE pgw.player_id = {player_id} AND pgw.started = 1 AND pgw.gameweek_id < {gw_id}').fetchall()[0]
    
    return (float(results[0]), float(results[1]))


def read_start_proportion(player_id: int, gw_id: int):

    """Returns proportion that player started when they played."""

    condition = f'pgw.gameweek_id >= ({gw_id}-6)'

    return float(execute_from_str(f'SELECT \
                                        SUM(CASE WHEN {condition} THEN pgw.started * {last_6_weight} ELSE pgw.started * {older_weight} END)/SUM(CASE WHEN {condition} THEN {last_6_weight} ELSE {older_weight} END) \
                                    FROM player_gameweek pgw \
                                    WHERE pgw.player_id = {player_id} AND pgw.started IS NOT NULL AND pgw.gameweek_id < {gw_id}').fetchone()[0])


def read_attacking_stats_per_90(player_id: int):

    """Returns attacking stats per 90."""

    return execute_from_str(f'SELECT p.npxG_per_90, p.xA_per_90 \
                                FROM player p \
                                WHERE p.id = {player_id}').fetchall()[0]


def read_penalty_stats_per_90(squad_id: int):

    """Returns penalty attempts per 90 for given squad."""

    return float(execute_from_str(f'SELECT AVG(pgw.penalty_attempts) \
                                    FROM player p \
                                    JOIN player_gameweek pgw ON p.id = pgw.player_id \
                                    WHERE p.squad_id = {squad_id}').fetchone()[0])


def read_all_player_ids():

    """Returns all player ids."""

    results = execute_from_str('SELECT id FROM player').fetchall()

    return [i[0] for i in results]


# def read_player_gameweek_ids(gameweek_id: int, player_id: int):

#     """Returns player gameweek ids for given player on given gameweek."""

#     results = execute_from_str(f'SELECT id from player_gameweek WHERE gameweek_id = {gameweek_id} AND player_id = {player_id}')

#     return [i[0] for i in results]


def read_squad_gameweek_id(squad_id: int, gameweek_id: int, opposition_id: int):

    """Returns player gameweek ids for given player on given gameweek."""

    return int(execute_from_str(f'SELECT id from squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gameweek_id} AND opposition_id = {opposition_id}').fetchone()[0])


def execute_from_str(query_str: str):

    """Execute query from string."""

    return cnx.execute(text(query_str))


def execute_from_file(query_file_path: str, args: tuple):

    """Read SQL file, insert args and execute."""
    
    with write_conn.cursor() as cursor:
        with open(f'./sql/{query_file_path}', 'r') as query_file:
            query = query_file.read()

        filled_query = query % args
        print(filled_query)
        cursor.execute(filled_query)
    
    write_conn.commit()