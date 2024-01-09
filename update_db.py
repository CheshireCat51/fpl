import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import StringIO
from bootstrap import Bootstrap
from manager import Manager
from dotenv import load_dotenv
import os
from utils import format_deadline_str
from player import Player


fbref_host = 'https://fbref.com'

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

player_columns_map = {
    'Player': 'name',
    'Pos': 'position',
    'MP': 'matches_played',
    'Min': 'minutes_played',
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

player_gameweek_columns_map = {
    'Round': 'gameweek_id',
    #'Venue': 'venue',
    'Start': 'started',
    'Min': 'minutes_played',
    'Gls': 'goals',
    'Ast': 'assists',
    'PK': 'penalty_goals',
    'PKatt': 'penalty_attempts',
    'CrdY': 'yellow_cards',
    'CrdR': 'red_cards',
    'xG': 'xG',
    'xAG': 'xA',
    'npxG': 'npxG',
}


def main():

    load_dotenv()
    me = Manager(os.environ.get('ME'))
    gameweeks_df = get_gameweek_data(me)
    #print(gameweeks_df)
    my_team_df = get_my_team_data(me)
    #print(my_team_df)

    # Write squads to excel
    squads_url = '/en/comps/9/Premier-League-Stats'
    squads_df, squad_rows = scrape_html(squads_url, 'stats_squads_standard_for', 'team')
    squads_df = trim_df(squad_columns_map, squads_df)
    squads_df['id'] = squads_df.apply(get_squad_id, axis=1)
    #print(squads_df)

    # Join elevenify data to fbref squad data
    team_strengths_df = get_elevenify_data()
    squads_df = squads_df.join(team_strengths_df)

    squad_gameweeks_df = pd.DataFrame()
    players_df = pd.DataFrame()
    player_gameweeks_df = pd.DataFrame()    

    i = 0
    for squad in squad_rows:
        squad_id = squads_df.loc[i]['id']
        # Write players from squad to excel
        player_df, player_rows = scrape_html(squad, 'stats_standard_9', 'player')
        # Remove bottom two rows of player df
        player_df = player_df.iloc[:-2]
        player_df = trim_df(player_columns_map, player_df)
        player_df.insert(0, 'squad_id', squad_id)
        player_df['id'] = player_df.apply(get_player_id, axis=1)
        player_df['position'] = player_df.apply(get_player_position, axis=1)
        players_df = pd.concat([players_df, player_df], axis=0)

        j = 0
        for player in player_rows:
            # Write player's last 5 games to excel
            fpl_player = Player(get_player_id(player_df.loc[j]))
            if fpl_player.position != 'GKP':
                player_gameweek_df, player_gameweek_rows = scrape_html(player, 'last_5_matchlogs')
                player_gameweek_df = trim_df(player_gameweek_columns_map, player_gameweek_df)
                player_gameweek_df.insert(0, 'player_id', fpl_player.player_id)
                player_gameweek_df['started'] = player_gameweek_df.apply(format_started_col, axis=1)
                player_gameweek_df['gameweek_id'] = player_gameweek_df.apply(get_gameweek_id, axis=1)
                #player_gameweek_df['opponent_id'] = player_gameweek_df.apply(lambda row: fpl_player.get_fixture(row['gameweek_id'])['id'], axis=1)
                player_gameweek_df['projected_points'] = player_gameweek_df.apply(lambda row: fpl_player.get_expected_points(row['gameweek_id']), axis=1)
                player_gameweek_df['points_scored'] = player_gameweek_df.apply(lambda row: fpl_player.get_points_scored(row['gameweek_id']), axis=1)
                player_gameweeks_df = pd.concat([player_gameweeks_df, player_gameweek_df], axis=0)

            # if player.text == 'Ben White':
            #     break

            j += 1

            time.sleep(5)

        i += 1
        #break

    # print(squad_gameweeks_df)
    # print(players_df)
    # print(player_gameweeks_df)

    gameweeks_df.to_excel('gameweeks.xlsx')
    my_team_df.to_excel('my_team.xlsx')
    squads_df.to_excel('squads.xlsx')
    squad_gameweeks_df.to_excel('squad_gameweeks.xlsx')
    players_df.to_excel('players.xlsx')
    player_gameweeks_df.to_excel('player_gameweeks.xlsx')

    return gameweeks_df, my_team_df, squads_df, squad_gameweeks_df, players_df, player_gameweeks_df


def trim_df(column_map, df: pd.DataFrame):

    """Returns df w/ only desired columns and renamed to match db schema."""

    selected_columns = [i for i in column_map.keys()]
    df = df[selected_columns]
    df = df.rename(columns=column_map)

    return df


def get_squad_id(row):

    """Returns squad id from FPL API for given row."""

    if row['name'] == 'Luton Town':
        name = 'Luton'
    elif row['name'] == 'Manchester City':
        name = 'Man City'
    elif row['name'] == 'Manchester Utd':
        name = 'Man Utd'
    elif row['name'] == 'Newcastle Utd':
        name = 'Newcastle'
    elif row['name'] == "Nott'ham Forest":
        name = "Nott'm Forest"
    elif row['name'] == 'Tottenham':
        name = 'Spurs'
    else:
        name = row['name']

    return Bootstrap.get_prem_team_by_name(name)['id']


def get_player_id(row):

    """Returns player id from FPL API for given row."""

    try:
        return find_player(row).player_id
    except AttributeError:
        return None
    

def get_player_position(row):

    """Returns player position from FPL API for given row."""

    try:
        return find_player(row).position
    except:
        return None


def find_player(row) -> Player:

    """Find player in FPL API."""

    player = Bootstrap.get_player_by_name(row['name'])

    if player == None:
        return None
    else:
        return Player(player['id'])


def get_gameweek_id(row):

    """Returns gameweek id from FBRef table."""

    round_str = row['gameweek_id']

    return round_str.split(' ')[1]


def format_started_col(row):

    """Returns correctly formated started column for DB."""

    if 'Y' in row['started']:
        return 1
    else:
        return 0


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
        

def scrape_html(tag, table_id: str, data_stat: str | None = None):

    """Returns a dataframe containing data from table with given table id and a soup objecting containing relevant rows from next table."""

    try:
        # If url passed in as HTML tag
        print(tag.text)
        url = get_url_from_anchor(tag)
    except:
        # If url passed in as string
        url = tag

    # Obtain HTML to be soupified
    r = requests.get(fbref_host + url)

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
    

def get_gameweek_data(me: Manager):

    """Returns gameweek df assembled from FPL API data."""

    for event in Bootstrap.summary['events']:
        if event['is_previous']:
            previous_gw = event
        elif event['is_current']:
            current_gw = event
        elif event['is_next']:
            next_gw = event
    
    gameweeks_df = pd.DataFrame(
        columns=['id', 'deadline', 'is_current', 'my_projected_points', 'my_points_scored', 'mean_points_scored'],
        data=[
            [previous_gw['id'], format_deadline_str(previous_gw['deadline_time']), 0, None, None, previous_gw['average_entry_score']],
            [current_gw['id'], format_deadline_str(current_gw['deadline_time']), 1, None, me.manager_summary['summary_event_points'], current_gw['average_entry_score']],
            [next_gw['id'], format_deadline_str(next_gw['deadline_time']), 0, me.current_team.get_expected_points(next_gw['id']), None, None]
        ]
    )
    
    return gameweeks_df


def get_my_team_data(me: Manager):

    """Returns my team df assembled from FPL API."""

    players = me.current_team.get_players()
    data = []
    for player in players:
        player_name = player.first_name + ' ' + player.second_name
        is_captain = False
        is_vice_captain = False
        if player.player_id == me.current_team.get_captain().player_id:
            is_captain = True
        if player.player_id == me.current_team.get_vice_captain().player_id:
            is_vice_captain = True
            
        data.append([
            Bootstrap.get_player_by_name(player_name)['id'],
            player_name,
            player.position,
            player.prem_team_id,
            player.get_fixture(Bootstrap.get_current_gw_id()+1)['id'],
            is_captain,
            is_vice_captain,
            None,
            player.current_price,
            None,
            player.get_expected_points()
        ])

    my_team_df = pd.DataFrame(
        columns=['player_id', 'player_name', 'position', 'squad_id', 'opponent_id', 'is_captain', 'is_vice_captain', 'purchase_price', 'current_price', 'selling_price', 'projected_points'],
        data=data
    )

    return my_team_df


if __name__ == '__main__':
    main()