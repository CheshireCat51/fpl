from dotenv import load_dotenv
import os
import pandas as pd
from manager import Manager
import sqlalchemy


def write_to_db():

    """Writing to fpl_model database."""

    load_dotenv()

    # me = Manager(os.environ.get('ME'))
    # print([(i.ownership, i.second_name) for i in me.current_team.get_players()])

    engine = sqlalchemy.create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model')
    conn = engine.connect()

    squad_df = pd.read_csv('team_strengths.csv', sep=',', header=0)
    squad_df.to_sql('squad_gameweek', con=conn, if_exists='append', index=False)

    conn.close()


if __name__ == '__main__':
    write_to_db()