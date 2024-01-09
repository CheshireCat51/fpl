from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text


load_dotenv()
engine = create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model')
cnx = engine.connect()


def read_defence_strength(squad_id: int):

    """Returns goals conceded against average prem opponent for given squad."""

    return cnx.execute(text(f'SELECT defence_strength FROM squad WHERE id = {squad_id}')).fetchone()[0]


def read_attack_strength(squad_id: int):

    """Returns goals scored against average prem opponent for given squad."""

    return cnx.execute(text(f'SELECT attack_strength FROM squad WHERE id = {squad_id}')).fetchone()[0]


# if __name__ == '__main__':
#     write_to_db()