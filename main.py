import requests
from dotenv import load_dotenv
import os


manager_id = 4361245


def main():

    """Entrypoint for FPL tracker."""

    session = init_session()

    current_team = session.get(f'https://fantasy.premierleague.com/api/my-team/{manager_id}/')
    print(current_team.json())


def init_session():

    """Initialize a session to get login cookies."""

    load_dotenv()

    # initialize session
    session = requests.session()

    url = 'https://users.premierleague.com/accounts/login/'
    payload = {
        'login': os.environ.get('FPL_USR'),
        'password': os.environ.get('FPL_PSW'),
        'redirect_uri': 'https://fantasy.premierleague.com/',
        'app': 'plfpl-web'
    }
    r = session.post(url, data=payload)
    print(r.status_code)

    return session


if __name__ == '__main__':
    main()