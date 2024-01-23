from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from bootstrap import Bootstrap
import mysql.connector


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model_23/24')
cnx = engine.connect()

write_conn = mysql.connector.connect(host='localhost', user='app', password=os.environ.get('DB_PASS'), database='fpl_model_23/24')


def read_defence_strength(squad_id: int, gw_id: int = Bootstrap.get_current_gw_id() + 1):

    """Returns goals conceded against average prem opponent for given squad."""

    return execute_from_str(f'SELECT defence_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}').fetchone()[0]


def read_attack_strength(squad_id: int, gw_id: int = Bootstrap.get_current_gw_id() + 1):

    """Returns goals scored against average prem opponent for given squad."""

    return execute_from_str(f'SELECT attack_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}').fetchone()[0]


def read_mean_strengths(gw_id: int = Bootstrap.get_current_gw_id() + 1):

    """Returns goals conceded against average prem opponent for given squad."""

    results = execute_from_str(f'SELECT AVG(attack_strength), AVG(defence_strength) FROM squad_gameweek WHERE gameweek_id = {gw_id}').fetchall()[0]

    return (float(results[0]), float(results[1]))


def read_expected_mins(player_id: int):

    """Returns mean mins played given that the player started and the std of these values."""

    results = execute_from_str(f'SELECT AVG(pgw.minutes_played), STD(pgw.minutes_played), p.chance_of_playing_next_gw \
                                FROM player_gameweek pgw \
                                JOIN player p ON pgw.player_id = p.id \
                                WHERE pgw.started = 1 AND p.id = {player_id}').fetchall()[0]
    
    if results[2] == None:
        chance_of_playing = 100
    else:
        chance_of_playing = results[2]
    
    return (float(results[0]), float(results[1]), float(chance_of_playing))


def read_attacking_stats_per_90(player_id: int):

    """Returns attacking stats per 90."""

    return execute_from_str(f'SELECT p.npxG_per_90, p.xA_per_90 \
                                FROM player p \
                                WHERE p.id = {player_id}').fetchall()[0]


def read_penalty_stats_per_90(squad_id: int):

    """Returns mean and std of penalty attempts."""

    return execute_from_str(f'SELECT AVG(pgw.penalty_attempts), STD(pgw.penalty_attempts) \
                                FROM player p \
                                JOIN player_gameweek pgw ON p.id = pgw.player_id \
                                WHERE p.squad_id = {squad_id}').fetchall()[0]


def execute_from_str(query_str: str):

    """Execute query from string."""

    return cnx.execute(text(query_str))


def update_from_file(query_file_path: str, args: tuple):

    """Read SQL file, insert args and execute."""
    
    with write_conn.cursor() as cursor:
        with open(f'./sql/{query_file_path}', 'r') as query_file:
            query = query_file.read()

        cursor.execute(query, args)


def insert_player():

    """Insert player into database."""