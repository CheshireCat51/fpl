from dotenv import load_dotenv
import os
import pandas as pd
from manager import Manager
import sqlalchemy


def init_cnx():

    """Initialize database connection."""

    load_dotenv()
    engine = sqlalchemy.create_engine(f'mysql://app:{os.environ.get('DB_PASS')}@localhost/fpl_model')
    cnx = engine.connect()

    return cnx


# def write_to_db():

#     """Writing to fpl_model database."""

#     # me = Manager(os.environ.get('ME'))
#     # print([(i.ownership, i.second_name) for i in me.current_team.get_players()])

#     squad_df = pd.read_csv('team_strengths.csv', sep=',', header=0)
#     squad_df.to_sql('squad_gameweek', con=cnx, if_exists='append', index=False)

#     cnx.close()


# if __name__ == '__main__':
#     write_to_db()