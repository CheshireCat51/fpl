import requests
from dotenv import load_dotenv
import os
from team import Team


manager_id = 4361245
finn_id = 4160523


def main():

    """Entrypoint for FPL tracker."""

    session = init_session()

    my_team = Team(session, manager_id)
    # my_team = Team(session, finn_id, gw_id=2)
    print([i.prem_team for i in my_team.players])


def init_session():

    """Initialize a session to get login cookies."""

    load_dotenv()

    headers = {
        'cookie': os.environ.get('COOKIE')
    }
    session = requests.session()
    session.headers.update(headers)

    return session


if __name__ == '__main__':
    main()