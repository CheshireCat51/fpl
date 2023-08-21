import requests


def get_bootstrap_summary():

    return requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()