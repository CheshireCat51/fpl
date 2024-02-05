from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
import mysql.connector
from utils import except_future_gw


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_23/24')
cnx = engine.connect()

write_conn = mysql.connector.connect(host='localhost', user='app', password=os.environ.get('DB_PASS'), database='fpl_model_23/24')


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

    # results = execute_from_str(f'SELECT AVG(pgw.minutes_played), STD(pgw.minutes_played), p.chance_of_playing_next_gw \
    #                             FROM player_gameweek pgw \
    #                             JOIN player p ON pgw.player_id = p.id \
    #                             WHERE pgw.started = 1 AND pgw.gameweek_id < {gw_id} AND p.id = {player_id}').fetchall()[0]
    
    results = execute_from_str(f'SELECT \
                                    SUM(CASE WHEN ({gw_id}-6) <= pgw.gameweek_id THEN pgw.minutes_played * 0.7 ELSE pgw.minutes_played * 0.3 END)/SUM(CASE WHEN (23-6) <= pgw.gameweek_id THEN 0.7 ELSE 0.3 END), \
                                    STD(pgw.minutes_played), \
                                    p.chance_of_playing_next_gw \
                                FROM player_gameweek pgw \
                                JOIN player p ON pgw.player_id = p.id \
                                WHERE pgw.player_id = {player_id} AND pgw.started = 1 AND pgw.gameweek_id < {gw_id}').fetchall()[0]
    
    if results[2] == None:
        chance_of_playing = 100
    else:
        chance_of_playing = results[2]
    
    return (float(results[0]), float(results[1]), float(chance_of_playing))


def read_start_proportion(player_id: int, gw_id: int):

    """Returns proportion that player started when they played."""

    return float(execute_from_str(f'SELECT AVG(pgw.started) \
                                    FROM player_gameweek pgw \
                                    WHERE pgw.player_id = {player_id} AND pgw.gameweek_id < {gw_id}').fetchone()[0])


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


def execute_from_str(query_str: str):

    """Execute query from string."""

    return cnx.execute(text(query_str))


def update_from_file(query_file_path: str, args: tuple):

    """Read SQL file, insert args and execute."""
    
    with write_conn.cursor() as cursor:
        with open(f'./sql/{query_file_path}', 'r') as query_file:
            query = query_file.read()

        filled_query = query % args
        print(filled_query)
        cursor.execute(filled_query)
    
    write_conn.commit()