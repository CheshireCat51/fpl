import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd
from manager import Manager


def write_to_db():

    """Writing to fpl_model database."""

    load_dotenv()

    me = Manager(os.environ.get('ME'))
    print([(i.ownership, i.second_name) for i in me.current_team.get_players()])

    # cnx = mysql.connector.MySQLConnection(user='app',
    #                                     password=os.environ.get('DB_PASS'),
    #                                     host='localhost',
    #                                     database='fpl_model')

    # cnx.close()


if __name__ == '__main__':
    write_to_db()