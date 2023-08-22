import requests
import os
from dotenv import load_dotenv


def init_session():

    """Initialize a session to get login cookies."""

    load_dotenv()

    headers = {
        'cookie': os.environ.get('COOKIE')
    }
    session = requests.session()
    session.headers.update(headers)

    return session