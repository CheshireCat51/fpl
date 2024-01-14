from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from bootstrap import Bootstrap


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model')
cnx = engine.connect()


def read_defence_strength(squad_id: int, gw_id: int = Bootstrap.get_current_gw_id() + 1):

    """Returns goals conceded against average prem opponent for given squad."""

    return cnx.execute(text(f'SELECT defence_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}')).fetchone()[0]


def read_attack_strength(squad_id: int, gw_id: int = Bootstrap.get_current_gw_id() + 1):

    """Returns goals scored against average prem opponent for given squad."""

    return cnx.execute(text(f'SELECT attack_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}')).fetchone()[0]


def read_expected_mins(player_id: int):

    """Returns mean mins played given that the player started and the std of these values."""

    results = cnx.execute(text(f'SELECT AVG(pgw.minutes_played), STD(pgw.minutes_played), p.chance_of_playing_next_gw \
                                FROM player_gameweek pgw \
                                JOIN player p ON pgw.player_id = p.id \
                                WHERE pgw.started = 1 AND p.id = {player_id}')).fetchall()[0]
    
    if results[2] == None:
        chance_of_playing = 100
    else:
        chance_of_playing = results[2]
    
    return (float(results[0]), float(results[1]), float(chance_of_playing))


def read_attacking_stats_per_90(player_id: int):

    """Returns attacking stats per 90."""

    return cnx.execute(text(f'SELECT p.npxG_per_90, p.xA_per_90 \
                                FROM player p \
                                WHERE p.id = {player_id}')).fetchall()[0]


def read_current_gw_id():

    """Returns current gw id."""

    return cnx.execute(text(f'SELECT gw.id \
                            FROM gameweek gw \
                            WHERE gw.is_current = 1')).fetchone()[0]


if __name__ == '__main__':
    print(read_expected_mins(36))