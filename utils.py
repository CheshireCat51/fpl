import requests
import os
from dotenv import load_dotenv
import math
from scipy.integrate import quad
import pandas as pd


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


def poisson_distribution(k: int, lam: float):

    """Returns probability of k events taking place according to Poisson distribution with mean lam."""

    return ((lam**k)*math.e**(-lam))/math.factorial(k)


def normal_distribution(mu: float, sigma: float, limits: tuple):

    """Returns probability of event outcome falling within given limits according to Normal distribution with mean mu and std sigma."""

    normal_prob_density = lambda x: (1/(sigma*math.sqrt(2*math.pi)))*math.e**(-(1/2)*((x-mu)/sigma)**2)

    return quad(normal_prob_density, limits[0], limits[1])[0]


def format_deadline_str(deadline: str):

    """Returns str in MySQL datetime format."""

    deadline_str = deadline.replace('Z', '').replace('T', ' ')

    return deadline_str


def format_null_args(args: list):

    """Replace nan args with NULL such they are readable by MySQL."""

    return ['NULL' if pd.isna(i) else i for i in args]


fpl_points_system = {
    'GKP': {
        'Clean Sheet': 4,
        'Goal Scored': 6,
        '3 Saves': 1,
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