import requests
import os
from dotenv import load_dotenv


def init_session():

    """Initialize a session to get login cookies."""

    load_dotenv()

    url = 'https://users.premierleague.com/accounts/login/'

    payload = {
        'password': os.environ.get('FPL_PWD'),
        'login': 'georgejpowell51@gmail.com',
        'redirect_uri': 'https://fantasy.premierleague.com/a/login',
        'app': 'plfpl-web'
    }

    session = requests.session()
    session.post(url, data=payload)

    # headers = {
    #     'cookie': os.environ.get('COOKIE')
    # }
    
    # session.headers.update(headers)

    return session


fpl_points_system = {
    'GKP': {
        'Clean Sheet': 4,
        'Goal Scored': 6,
        'Save (per 3 saves)': 1,
        'Penalty Save': 5,
        '2 Goals Conceded': -1,
    },
    'DEF': {
        'Clean Sheet': 4,
        'Goal Scored': 6,
        '2 Goals Conceded': -1,
    },
    'MID': {
        'Goal Scored': 5,
        'Clean Sheet': 1
    },
    'FWD': {
        'Goal Scored': 4,
    },
    'Other': {
        '< 60 mins': 1,
        '>= 60 mins': 2,
        'Assist': 3,
        'Yellow Card': -1,
        'Red Card': -3,
        'Own Goal': -2,
        'Penalty Miss': -2
    }
}