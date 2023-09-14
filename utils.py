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