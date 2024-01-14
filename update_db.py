import pandas as pd
import requests
from bs4 import BeautifulSoup, element
import time
from io import StringIO
from bootstrap import Bootstrap
from manager import Manager
from dotenv import load_dotenv
import os
from utils import format_deadline_str
from player import Player
from crud import cnx, engine


fbref_host = 'https://fbref.com'

squad_column_map = {
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

squad_gw_column_map = {
    'Round': 'gameweek_id',
    'Opponent': 'name',
    'Venue': 'venue',
    'xG': 'xG',
    'xGA': 'xGC'
}

team_strength_column_map = {
    '   Attack Strength': 'attack_strength',
    '+/-': 'attack_strength_change',
    ' Defence Strength': 'defence_strength',
    '+/-.1': 'defence_strength_change',
    ' Overall Strength': 'overall_strength',
    '+/-.2': 'overall_strength_change',  
}

player_column_map = {
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

player_gw_column_map = {
    'Round': 'gameweek_id',
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


def bulk_update():

    gw_id = Bootstrap.get_current_gw_id()

    # Load environment vars
    load_dotenv()

    # Create client manager object
    me = Manager(os.environ.get('ME'))

    # Create/update gameweek table
    gameweeks_df = get_gameweek_data(me)

    # Update my_team table
    #my_team_df = get_my_team_data(me)

    # # Write squads to excel
    # squads_url = '/en/comps/9/Premier-League-Stats'
    # squads_soup = scrape_html(squads_url, 'stats_squads_standard_for')
    # squads_df = get_df_from_soup(squads_soup)
    # squad_rows = get_next_level_rows(squads_soup, 'th', 'team')
    # squads_df = trim_df(squad_column_map, squads_df)
    # squads_df['id'] = squads_df.apply(get_squad_id, axis=1)

    # team_strengths_df = get_elevenify_data()
    # # Add squad ids to team strength df
    # team_strengths_df.insert(0, 'squad_id', list(range(1, len(team_strengths_df.index)+1)))
    # # Add next gw id (team strengths will be valid for upcoming gameweek)
    # team_strengths_df.insert(0, 'gameweek_id', gw_id+1)

    # squad_gameweeks_df = pd.DataFrame()
    # players_df = pd.DataFrame()
    # player_gameweeks_df = pd.DataFrame()    

    # for squad in squad_rows:
    #     print(squad.text)
    #     squad_id = squads_df.loc[squads_df['name'] == squad.text, 'id'].item()

    #     # Write squad gameweek breakdown to df
    #     squad_gameweek_soup = scrape_html(squad, 'matchlogs_for')
    #     squad_gameweek_df = get_df_from_soup(squad_gameweek_soup, header=0)
    #     squad_gameweek_df = squad_gameweek_df[squad_gameweek_df['Comp'] == 'Premier League']
    #     squad_gameweek_df = trim_df(squad_gw_column_map, squad_gameweek_df)
    #     squad_gameweek_df.insert(0, 'squad_id', squad_id)
    #     squad_gameweek_df['opposition_id'] = squad_gameweek_df.apply(get_squad_id, axis=1)
    #     squad_gameweek_df['gameweek_id'] = squad_gameweek_df.apply(get_gameweek_id, axis=1)
    #     squad_gameweek_df = squad_gameweek_df.drop('name', axis=1)

    #     # Get relevant rows to current squad from team strength df
    #     team_strength_df = team_strengths_df.loc[team_strengths_df['squad_id'] == squad_id]
    #     # Reset index such that strengths can be found by index
    #     team_strength_df = team_strength_df.reset_index()
    #     for strength_col in team_strength_column_map.values():
    #         squad_gameweek_df.loc[squad_gameweek_df['gameweek_id'] == gw_id, strength_col] = team_strength_df.loc[0, strength_col]

    #     squad_gameweeks_df = pd.concat([squad_gameweeks_df, squad_gameweek_df], axis=0)

    #     time.sleep(5)

    #     # Write players from squad to df
    #     player_soup = scrape_html(squad, 'stats_standard_9')
    #     player_df = get_df_from_soup(player_soup) 
    #     player_rows = get_next_level_rows(player_soup, tag_type='th', data_stat='player')
    #     matches_rows = get_next_level_rows(player_soup, tag_type='td', data_stat='matches')
    #     assert len(player_rows) == len(matches_rows)
    #     # Remove bottom two rows of player df (these are summary rows)
    #     player_df = player_df.iloc[:-2]
    #     player_df = trim_df(player_column_map, player_df)
    #     player_df.insert(0, 'squad_id', squad_id)
    #     player_df['id'] = player_df.apply(get_player_id, axis=1)
    #     # Drop rows where id is null
    #     player_df = player_df.dropna(subset='id')
    #     # Change id column to integer type
    #     player_df['id'] = player_df['id'].astype('int')
    #     player_df['position'] = player_df.apply(lambda row: Player(row['id']).position, axis=1)
    #     player_df['ownership'] = player_df.apply(lambda row: Player(row['id']).ownership, axis=1)
    #     player_df['current_price'] = player_df.apply(lambda row: Player(row['id']).current_price, axis=1)
    #     player_df['chance_of_playing_next_gw'] = player_df.apply(lambda row: Player(row['id']).player_summary['chance_of_playing_next_round'], axis=1)

    #     players_df = pd.concat([players_df, player_df], axis=0)
    #     players_df = players_df.reset_index(drop=True)
    #     players_df = remove_duplicate_players(players_df)

    #     for j in range(len(player_rows)):
    #         player = player_rows[j]
    #         matches = matches_rows[j]

    #         print(player.text)

    #         # Write player's last 5 games to excel
    #         try:
    #             fpl_player = Player(player_df.loc[player_df['name'] == player.text, 'id'].item())
    #         except:
    #             continue

    #         if fpl_player.position != 'GKP':
    #             player_gameweek_soup = scrape_html(matches, 'matchlogs_all')
    #             if player_gameweek_soup != None:
    #                 player_gameweek_df = get_df_from_soup(player_gameweek_soup)
    #                 # Filter out non-prem games
    #                 player_gameweek_df = player_gameweek_df[player_gameweek_df['Comp'] == 'Premier League']
    #                 if player_gameweek_df.empty == False:
    #                     player_gameweek_df = trim_df(player_gw_column_map, player_gameweek_df)
    #                     # Remove rows where player was an unused substitute
    #                     player_gameweek_df = player_gameweek_df.loc[player_gameweek_df['minutes_played'] != 'On matchday squad, but did not play']
    #                     player_gameweek_df.insert(0, 'player_id', fpl_player.player_id)
    #                     player_gameweek_df['started'] = player_gameweek_df.apply(format_started_col, axis=1)
    #                     player_gameweek_df['gameweek_id'] = player_gameweek_df.apply(get_gameweek_id, axis=1)
    #                     player_gameweek_df['projected_points'] = player_gameweek_df.apply(lambda row: get_projected_points(row, fpl_player), axis=1)
    #                     player_gameweek_df['points_scored'] = player_gameweek_df.apply(lambda row: fpl_player.get_points_scored(row['gameweek_id']), axis=1)
    #                     player_gameweeks_df = pd.concat([player_gameweeks_df, player_gameweek_df], axis=0)

    #             time.sleep(5)

    gameweeks_df.to_excel('gameweeks.xlsx')
    #my_team_df.to_excel('my_team.xlsx')
    #squads_df.to_excel('squads.xlsx')
    #squad_gameweeks_df.to_excel('squad_gameweeks.xlsx')
    #players_df.to_excel('players.xlsx')
    #player_gameweeks_df.to_excel('player_gameweeks.xlsx')

    gameweeks_df.to_sql('gameweek', con=engine, if_exists='append', index=False)
    #squads_df.to_sql('squad', con=cnx, if_exists='append', index=False)
    #squad_gameweeks_df.to_sql('squad_gameweek', con=cnx, if_exists='append', index=False)
    #players_df.to_sql('player', con=cnx, if_exists='append', index=False)
    #player_gameweeks_df.to_sql('player_gameweek', con=cnx, if_exists='append', index=False)

    return gameweeks_df


def trim_df(column_map, df: pd.DataFrame):

    """Returns df w/ only desired columns and renamed to match db schema."""

    selected_columns = [i for i in column_map.keys()]
    df = df[selected_columns]
    df = df.rename(columns=column_map)

    return df


def remove_duplicate_players(players_df: pd.DataFrame):

    """Returns player df with duplicates removed."""

    for index, is_duplicate in players_df.duplicated(subset='id', keep=False).items():
        player_id = int(players_df.loc[index, 'id'])
        squad_id = int(players_df.loc[index, 'squad_id'])
        if is_duplicate == True:
            fpl_player = Player(player_id)
            if squad_id != fpl_player.prem_team_id:
                players_df = players_df.drop(index)

    return players_df


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

    fpl_player = find_player(row['name'])

    if fpl_player != None:
        return fpl_player.player_id


def find_player(player_name) -> Player:

    """Find player in FPL API."""

    player = Bootstrap.get_player_by_name(player_name)

    if player == None:
        return None
    else:
        return Player(player['id'])


def get_gameweek_id(row):

    """Returns gameweek id from FBRef table."""

    round = row['gameweek_id']

    return int(round.split(' ')[1])


def get_projected_points(row, fpl_player: Player):

    """Returns projected points for upcoming gameweek."""

    gw_id = row['gameweek_id']

    if gw_id == Bootstrap.get_current_gw_id():
        return fpl_player.get_projected_points(gw_id)
    else:
        return None


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
    team_strength_df = trim_df(team_strength_column_map, team_strength_df)

    return team_strength_df


def scrape_html(tag: str | element.Tag, table_id: str):

    """Returns a dataframe containing data from table with given table id and a soup objecting containing relevant rows from next table."""

    try:
        # If url passed in as HTML tag
        url = get_url_from_anchor(tag)
    except:
        # If url passed in as string
        url = tag

    try:
        # Obtain HTML to be soupified
        r = requests.get(fbref_host + url)

        # Create Soup object
        soup = BeautifulSoup(r.content, 'lxml')

        # Find appropriate table
        table = soup.find('table', {'id': table_id})
    except:
        return None
    else:
        return table
    

def get_df_from_soup(soup_table, header: int = 1):

    """Returns df from soup table."""

    # Transform HTML table to pandas Dataframe
    table_df = pd.read_html(StringIO(str(soup_table)), header=header)[0]

    return table_df


def get_next_level_rows(soup_table, tag_type: str, data_stat: str):

    """Returns required rows from given soup table."""

    # Get appropriate rows from next table
    tbody = soup_table.find('tbody')
    rows = tbody.find_all(tag_type, {'data-stat': data_stat})
    return rows
    

def get_gameweek_data(me: Manager):

    """Returns gameweek df assembled from FPL API data."""

    data = []
    for event in Bootstrap.summary['events']:
        is_current = 0
        projected_points = None
        points_scored = None

        if event['is_current']:
            is_current = 1
            points_scored = me.manager_summary['summary_event_points']
            projected_points = me.current_team.get_projected_points()

        # if event['is_next']:
        #     projected_points = me.current_team.get_projected_points()

        data.append([event['id'], format_deadline_str(event['deadline_time']), is_current, projected_points, points_scored, event['average_entry_score']])
    
    gameweeks_df = pd.DataFrame(
        columns=['id', 'deadline', 'is_current', 'my_projected_points', 'my_points_scored', 'mean_points_scored'],
        data=data
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
            is_captain,
            is_vice_captain,
            None,
            None
        ])

    my_team_df = pd.DataFrame(
        columns=['player_id', 'is_captain', 'is_vice_captain', 'purchase_price', 'selling_price'],
        data=data
    )

    return my_team_df


if __name__ == '__main__':
    bulk_update()