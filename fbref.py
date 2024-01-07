import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import StringIO
from database import init_cnx


host = 'https://fbref.com'

squad_columns_map = {
    'Squad': 'name',
    'MP': 'matches_played',
    'Gls': 'goals',
    'Ast': 'assists',
    'PK': 'penalty_goals',
    'PKatt': 'penalty_attempts',
    'CrdY': 'yellow_cards',
    'CrdR': 'red_cards',
    'xG': 'xG',
    'xAG': 'xA',
    'npxG': 'npxG',
    'PrgC': 'progressive_carries',
    'PrgP': 'progressive_passes',
    'Gls.1': 'goals_per_90',
    'Ast.1': 'assists_per_90',
    'xG.1': 'xG_per_90',
    'xAG.1': 'xA_per_90',
    'npxG.1': 'npxG_per_90'
}

team_strength_columns_map = {
    'Team': 'abbreviation',
    '   Attack Strength': 'attack_strength',
    ' Defence Strength': 'defence_strength',
    ' Overall Strength': 'overall_strength'  
}


## METHOD ONE ##

def main():

    cnx = init_cnx()

    players_df = pd.read_sql_table('player', cnx)
    player_gameweeks_df = pd.read_sql_table('player_gameweek', cnx)

    # Write squads to excel
    squads_url = '/en/comps/9/Premier-League-Stats'
    squads_df, squad_rows = get_fbref_data(squads_url, 'stats_squads_standard_for', 'team')
    selected_columns = [i for i in squad_columns_map.keys()]
    squads_df = squads_df[selected_columns]
    squads_df = squads_df.rename(columns=squad_columns_map)

    # for squad in squad_rows:
    #     # Write players from squad to excel
    #     print(squad.text)
    #     squad_url = get_url_from_anchor(squad)
    #     player_df, player_rows = get_fbref_data(squad_url, 'stats_standard_9', 'player')
    #     # Remove bottom two rows of player df
    #     player_df = player_df.iloc[:-2]
    #     players_df = pd.concat([players_df, player_df], axis=0)

    #     for player in player_rows:
    #         # Write player's last 5 games to excel
    #         print(player.text)
    #         player_url = get_url_from_anchor(player)
    #         player_gameweek_df, player_gameweek_rows = get_fbref_data(player_url, 'last_5_matchlogs')
    #         player_gameweek_df.insert(0, 'name', player.text)
    #         player_gameweeks_df = pd.concat([player_gameweeks_df, player_gameweek_df], axis=0)

    #         if player.text == 'Ben White':
    #             break

    #         time.sleep(10)

    #     break

    # print(players_df)
    # print(player_gameweeks_df)

    team_strengths_df = get_elevenify_data()
    squads_df = squads_df.join(team_strengths_df)
    print(squads_df)

    squads_df.to_excel('squads.xlsx', header=0)
    squads_df.to_sql('squad', con=cnx, if_exists='replace', index=False)

    players_df.to_excel('players.xlsx', header=0)
    players_df.to_sql('player', con=cnx, if_exists='replace', index=False)

    player_gameweeks_df.to_excel('player_gameweeks.xlsx', header=0)
    player_gameweeks_df.to_sql('player_gameweek', con=cnx, if_exists='append', index=False)


def get_url_from_anchor(element):

    """Returns url that anchor HTML elements point to."""

    return element.find('a').get('href')


def get_elevenify_data():

    """Returns dataframe of team strengths from Elevenify."""

    team_strength_df = pd.read_csv('UVKbs.csv', sep=',', header=0)
    selected_columns = [i for i in team_strength_columns_map.keys()]
    team_strength_df = team_strength_df[selected_columns]
    team_strength_df = team_strength_df.rename(columns=team_strength_columns_map)

    return team_strength_df
        

def get_fbref_data(url: str, table_id: str, data_stat: str | None = None):

    """Returns a dataframe containing data from table with given table id and a soup objecting containing relevant rows from next table."""

    # Obtain HTML to be soupified
    r = requests.get(host + url)

    # Create Soup object
    soup = BeautifulSoup(r.content, 'lxml')

    try:
        # Find appropriate table
        table = soup.find('table', {'id': table_id})

        # Transform HTML table to pandas Dataframe and write to excel
        table_df = pd.read_html(StringIO(str(table)), header=1)[0]

    except ValueError as e:
        print(e)
        return None, None

    else:
        # Get appropriate rows from next table
        tbody = table.find('tbody')
        rows = tbody.find_all('th', {'scope': 'row', 'data-stat': data_stat})
        return table_df, rows


if __name__ == '__main__':
    #get_elevenify_data()
    main()


player_columns = ['name',
                'squad_id',
                'squad_abbreviation',
                'position',
                'matches_played',
                'minutes_played',
                'goals',
                'assists',
                'penalty_goals',
                'penalty_attempts',
                'yellow_cards',
                'red_cards',
                'xG',
                'npxG',
                'xA',
                'progressive_carries',
                'progressive_passes',
                'goals_per_90',
                'assists_per_90',
                'xG_per_90',
                'xA_per_90',
                'effective_ownership',
                'next_opponent_id',
                'next_opponent_abbreviation',
                'chance_of_playing_this_gameweek',
                'projected_points']

player_gameweek_columns=['player_id',
                         'gameweek_id',
                         'opponent_id',
                         'started',
                         'minutes_played',
                         'goals',
                         'assists',
                         'penalty_goals',
                         'penalty_attempts',
                         'yellow_cards',
                         'red_cards',
                         'xG',
                         'npxG',
                         'xA',
                         'progressive_carries',
                         'progressive_passes',
                         'projected_points',
                         'points']