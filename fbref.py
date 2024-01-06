import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import StringIO


host = 'https://fbref.com'


## METHOD ONE ##

def main():

    squads_url = '/en/comps/9/Premier-League-Stats'

    players_df = pd.DataFrame()
    player_gameweeks_df = pd.DataFrame()

    # Write squads to excel
    squads_df, squad_rows = extract_data_from_fbref(squads_url, 'stats_squads_standard_for', 'team')

    for squad in squad_rows:
        # Write players from squad to excel
        print(squad.text)
        squad_url = get_url_from_anchor(squad)
        player_df, player_rows = extract_data_from_fbref(squad_url, 'stats_standard_9', 'player')
        players_df = pd.concat([players_df, player_df], axis=0)

        for player in player_rows:
            # Write player's last 5 games to excel
            print(player.text)
            player_url = get_url_from_anchor(player)
            player_gameweek_df, player_gameweek_rows = extract_data_from_fbref(player_url, 'last_5_matchlogs')
            player_gameweeks_df = pd.concat([player_gameweeks_df, player_gameweek_df], axis=0)

            time.sleep(10)

    print(squads_df)
    print(players_df)
    print(player_gameweeks_df)

    squads_df.to_excel('squads.xlsx', header=[0,1])
    players_df.to_excel('players.xlsx', header=[0,1])
    player_gameweeks_df.to_excel('player_gameweeks.xlsx', header=[0,1])


def get_url_from_anchor(element):

    """Returns url that anchor HTML elements point to."""

    return element.find('a').get('href')
        

def extract_data_from_fbref(url: str, table_id: str, data_stat: str | None = None):

    """Returns a dataframe containing data from table with given table id and a soup objecting containing relevant rows from next table."""

    # Obtain HTML to be soupified
    r = requests.get(host + url)

    # Create Soup object
    soup = BeautifulSoup(r.content, 'lxml')

    try:
        # Find appropriate table
        table = soup.find('table', {'id': table_id})

        # Transform HTML table to pandas Dataframe and write to excel
        table_df = pd.read_html(StringIO(str(table)), header=[0,1])[0]

    except ValueError as e:
        print(e)
        return None, None

    else:
        # Get appropriate rows from next table
        tbody = table.find('tbody')
        rows = tbody.find_all('th', {'scope': 'row', 'data-stat': data_stat})
        return table_df, rows


if __name__ == '__main__':
    main()