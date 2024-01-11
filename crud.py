from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from bootstrap import Bootstrap


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model')
cnx = engine.connect()


def read_defence_strength(squad_id: int, gw_id: int = Bootstrap.get_current_gw_id()):

    """Returns goals conceded against average prem opponent for given squad."""

    return cnx.execute(text(f'SELECT defence_strength FROM squad_gameweek WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}')).fetchone()[0]


def read_attack_strength(squad_id: int, gw_id: int = Bootstrap.get_current_gw_id()):

    """Returns goals scored against average prem opponent for given squad."""

    return cnx.execute(text(f'SELECT attack_strength FROM squad WHERE squad_id = {squad_id} AND gameweek_id = {gw_id}')).fetchone()[0]


# if __name__ == '__main__':
#     bulk_update()