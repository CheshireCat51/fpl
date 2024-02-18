import pandas as pd
import requests
from bs4 import BeautifulSoup, element
from io import StringIO
from bootstrap import Bootstrap
from manager import Manager
from user import User
from dotenv import load_dotenv
import os
from utils import format_deadline_str, format_null_args
from player import Player
from crud import cnx, execute_from_file, read_all_player_ids
import time
from datetime import datetime


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
    'Date': 'date',
    'Round': 'gameweek_id',
    'Opponent': 'name',
    'Venue': 'venue',
    'xG': 'xG',
    'xGA': 'xGC'
}

team_strength_column_map = {
    '   Attack Strength': 'attack_strength',
    ' Defence Strength': 'defence_strength',
    ' Overall Strength': 'overall_strength'
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
    'npxG': 'npxG',
    'xAG': 'xA',
    'PrgC': 'progressive_carries',
    'PrgP': 'progressive_passes',
    'Gls.1': 'goals_per_90',
    'Ast.1': 'assists_per_90',
    'xG.1': 'xG_per_90',
    'xAG.1': 'xA_per_90',
    'npxG.1': 'npxG_per_90'
}

player_gw_column_map = {
    'Date': 'date',
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
    # me = Manager(os.environ.get('ME'))

    # # Create/update gameweek table
    # gameweeks_df = get_gameweek_data(me)

    # # Update my_team table
    # my_team_df = get_my_team_data(me)

    # Write squads to excel
    squads_url = '/en/comps/9/Premier-League-Stats'
    squads_soup = scrape_html(squads_url, 'stats_squads_standard_for')
    squads_df = get_df_from_soup(squads_soup)
    squad_rows = get_next_level_rows(squads_soup, 'th', 'team')
    squads_df = trim_df(squad_column_map, squads_df)
    squads_df['id'] = squads_df.apply(get_squad_id, axis=1)

    team_strengths_df = get_elevenify_data()
    # Add squad ids to team strength df
    team_strengths_df.insert(0, 'squad_id', list(range(1, len(team_strengths_df.index)+1)))
    # Add next gw id (team strengths will be valid for upcoming gameweek)
    team_strengths_df.insert(0, 'gameweek_id', gw_id+1)

    squad_gameweeks_df = pd.DataFrame()
    players_df = pd.DataFrame()
    player_gameweeks_df = pd.DataFrame()

    for squad in squad_rows:
        print(squad.text)
        squad_id = squads_df.loc[squads_df['name'] == squad.text, 'id'].item()

        # Write squad gameweek breakdown to df
        squad_gameweek_soup = scrape_html(squad, 'matchlogs_for')
        squad_gameweek_df = get_df_from_soup(squad_gameweek_soup, header=0)
        squad_gameweek_df = squad_gameweek_df[squad_gameweek_df['Comp'] == 'Premier League']
        squad_gameweek_df = trim_df(squad_gw_column_map, squad_gameweek_df)
        squad_gameweek_df.insert(0, 'squad_id', squad_id)
        squad_gameweek_df['opposition_id'] = squad_gameweek_df.apply(get_squad_id, axis=1)
        squad_gameweek_df['gameweek_id'] = squad_gameweek_df.apply(lambda row: get_gameweek_id(row, squad_gameweek_df), axis=1)
        squad_gameweek_df = squad_gameweek_df.drop('name', axis=1)
        squad_gameweek_df = squad_gameweek_df.drop('date', axis=1)

        # Get relevant rows to current squad from team strength df
        team_strength_df = team_strengths_df.loc[team_strengths_df['squad_id'] == squad_id]
        # Reset index such that strengths can be found by index
        team_strength_df = team_strength_df.reset_index()
        for strength_col in team_strength_column_map.values():
            squad_gameweek_df.loc[squad_gameweek_df['gameweek_id'] == gw_id+1, strength_col] = team_strength_df.loc[0, strength_col]

        squad_gameweeks_df = pd.concat([squad_gameweeks_df, squad_gameweek_df], axis=0)

        # Write players from squad to df
        player_soup = scrape_html(squad, 'stats_standard_9')
        player_df = get_df_from_soup(player_soup) 
        player_rows = get_next_level_rows(player_soup, tag_type='th', data_stat='player')
        matches_rows = get_next_level_rows(player_soup, tag_type='td', data_stat='matches')
        assert len(player_rows) == len(matches_rows)
        # Remove bottom two rows of player df (these are summary rows)
        player_df = player_df.iloc[:-2]
        player_df = trim_df(player_column_map, player_df)
        player_df.insert(0, 'squad_id', squad_id)
        player_df['id'] = player_df.apply(get_player_id, axis=1)
        # Drop rows where id is null
        player_df = player_df.dropna(subset='id')
        # Change id column to integer type
        player_df['id'] = player_df['id'].astype('int')
        player_df['position'] = player_df.apply(lambda row: Player(row['id']).position, axis=1)
        player_df['ownership'] = player_df.apply(lambda row: Player(row['id']).ownership, axis=1)
        player_df['current_price'] = player_df.apply(lambda row: Player(row['id']).current_price, axis=1)
        player_df['chance_of_playing_next_gw'] = player_df.apply(lambda row: Player(row['id']).player_summary['chance_of_playing_next_round'], axis=1)

        players_df = pd.concat([players_df, player_df], axis=0)
        players_df = players_df.reset_index(drop=True)
        players_df = remove_duplicate_players(players_df)

        for j in range(len(player_rows)):
            player = player_rows[j]
            matches = matches_rows[j]

            print(player.text)

            # Write player's last 5 games to excel
            try:
                fpl_player = Player(player_df.loc[player_df['name'] == player.text, 'id'].item())
            except:
                continue

            if fpl_player.position != 'GKP':
                player_gameweek_soup = scrape_html(matches, 'matchlogs_all')
                if player_gameweek_soup != None:
                    player_gameweek_df = get_df_from_soup(player_gameweek_soup)
                    # Filter out non-prem games
                    player_gameweek_df = player_gameweek_df[player_gameweek_df['Comp'] == 'Premier League']
                    if player_gameweek_df.empty == False:
                        player_gameweek_df = trim_df(player_gw_column_map, player_gameweek_df)
                        # Remove rows where player was an unused substitute
                        player_gameweek_df = player_gameweek_df.loc[player_gameweek_df['minutes_played'] != 'On matchday squad, but did not play']
                        player_gameweek_df.insert(0, 'player_id', fpl_player.player_id)
                        player_gameweek_df['started'] = player_gameweek_df.apply(format_started_col, axis=1)
                        player_gameweek_df['gameweek_id'] = player_gameweek_df.apply(lambda row: get_gameweek_id(row, player_gameweek_df), axis=1)
                        player_gameweek_df.insert(0, 'projected_points', None)
                        #player_gameweek_df['projected_points'] = player_gameweek_df.apply(lambda row: get_projected_points(row, fpl_player), axis=1)
                        player_gameweek_df['points_scored'] = player_gameweek_df.apply(lambda row: fpl_player.get_points_scored(row['gameweek_id']), axis=1)
                        player_gameweek_df = player_gameweek_df.drop('date', axis=1)
                        player_gameweeks_df = pd.concat([player_gameweeks_df, player_gameweek_df], axis=0)
                        

            time.sleep(3.5)

    #gameweeks_df.to_excel('gameweeks.xlsx')
    #my_team_df.to_excel('my_team.xlsx')
    #squads_df.to_excel('squads.xlsx')
    #squad_gameweeks_df.to_excel('squad_gameweeks.xlsx')
    #players_df.to_excel('players.xlsx')
    #player_gameweeks_df.to_excel('player_gameweeks.xlsx')

    #gameweeks_df.to_sql('gameweek', con=engine, if_exists='append', index=False)
    #my_team_df.to_sql('my_team', con=cnx, if_exists='append', index=False)
    #squads_df.to_sql('squad', con=cnx, if_exists='append', index=False)
    #squad_gameweeks_df.to_sql('squad_gameweek', con=cnx, if_exists='append', index=False)
    #players_df.to_sql('player', con=cnx, if_exists='append', index=False)
    #player_gameweeks_df.to_sql('player_gameweek', con=cnx, if_exists='append', index=False)
                
    return squads_df, players_df, squad_gameweeks_df, player_gameweeks_df


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


def get_gameweek_id(row, df):

    """Returns gameweek id from FBRef table. WIP identifying B/DGW."""

    # Reset index so that all rows are numbered consecutively
    df = df.reset_index()

    round = int(row['gameweek_id'].split(' ')[1])
    date = row['date']

    row_index = df[df['gameweek_id'] == row['gameweek_id']].index[0]

    try:
        preceeding_gw = df.iloc[row_index-1]
    
    except IndexError:
        print('Preceeding gw not found.')
        return round
    
    else:
        preceeding_round = int(preceeding_gw['gameweek_id'].split(' ')[1])
        preceeding_date = preceeding_gw['date']

        # Dealing with B/DGWs
        # If match occurs after preceeding gameweek but its gw id is smaller than the preceeding gameweek then return gameweek id of preceeding gameweek
        if date > preceeding_date and round < preceeding_round:
            print(preceeding_round)
            return preceeding_round
        else:
            return round


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

    team_strength_df = pd.read_csv(f'./elevenify/UVKbs_{Bootstrap.get_current_gw_id()+1}.csv', sep=',', header=0)
    team_strength_df = trim_df(team_strength_column_map, team_strength_df)
    strength_columns = team_strength_column_map.values()
    for col in strength_columns:
        team_strength_df[col] = team_strength_df.apply(lambda row: format_elevenify_data(row, col), axis=1)

    return team_strength_df


def format_elevenify_data(row, col):

    """Returns corrected float values."""

    formatted_element = row[col]

    if type(formatted_element) == str:
        formatted_element = formatted_element.replace('+', '')
        formatted_element = formatted_element.replace('-', '')
        formatted_element = formatted_element.replace(' ', '')

    return float(formatted_element)


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
    

def get_gameweek_data(me: User):

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


def get_my_team_data(me: User):

    """Returns my team df assembled from FPL API."""

    players = me.current_team.get_players()
    bench = [i['element'] for i in me.current_team.team_summary['picks'] if i['multiplier'] == 0]
    prices = me.optim_data['picks']
    data = []
    for player in players:
        is_captain = False
        is_vice_captain = False
        is_benched = False

        asset = [i for i in prices if i['element'] == player.player_id][0]       

        if player.player_id == me.current_team.get_captain().player_id:
            is_captain = True
        elif player.player_id == me.current_team.get_vice_captain().player_id:
            is_vice_captain = True

        if player.player_id in bench:
            is_benched = True
            
        data.append([
            player.player_id,
            is_captain,
            is_vice_captain,
            is_benched,
            asset['purchase_price'],
            asset['selling_price']
        ])

    my_team_df = pd.DataFrame(
        columns=['player_id', 'is_captain', 'is_vice_captain', 'is_benched', 'purchase_price', 'selling_price'],
        data=data
    )

    return my_team_df


def post_gameweek_update():

    """Update db immediately after gameweek ends."""

    squads_df, players_df, squad_gameweeks_df, player_gameweeks_df = bulk_update()

    update_squad(squads_df)
    update_player(players_df)
    update_squad_gameweek(squad_gameweeks_df)
    update_player_gameweek(player_gameweeks_df)
    insert_player_gameweek()
    update_gameweek()
    update_my_team()


def update_squad(squads_df: pd.DataFrame):
    
    """Update squad table."""

    for index, row in squads_df.iterrows():
        args = [row[i] for i in squad_column_map.values() if i != 'name']
        args.append(row['id'])
        args = format_null_args(args)
        execute_from_file('update_squad.sql', tuple(args))


def update_player(players_df: pd.DataFrame):
    
    """Update player table."""

    for index, row in players_df.iterrows():
        args = [row[i] for i in player_column_map.values() if i != 'name']
        args.pop(0)
        args.append(row['ownership'])
        args.append(row['current_price'])
        args.append(row['chance_of_playing_next_gw'])
        args.append(row['id'])
        args = format_null_args(args)
        execute_from_file('update_player.sql', tuple(args))


def update_squad_gameweek(squad_gameweeks_df: pd.DataFrame):

    """Update squad gameweek table."""

    current_gw_id = Bootstrap.get_current_gw_id()

    # For each squad...
    for i in range(1, 21):
        trimmed_df = squad_gameweeks_df[(squad_gameweeks_df['squad_id'] == i) & ((squad_gameweeks_df['gameweek_id'] == current_gw_id) | (squad_gameweeks_df['gameweek_id'] == current_gw_id+1))]
        print(trimmed_df)

        # For each gameweek in current and next...
        for index, row in trimmed_df.iterrows():
            if row['gameweek_id'] == current_gw_id:
                current_gw_args = [row['xG'], row['xGC'], row['squad_id'], row['gameweek_id']]
                current_gw_args = format_null_args(current_gw_args)
                execute_from_file('update_current_squad_gameweek.sql', tuple(current_gw_args))
            elif row['gameweek_id'] == current_gw_id+1:
                next_gw_args = [row['overall_strength'],
                                row['attack_strength'],
                                row['defence_strength'],
                                row['squad_id'],
                                row['gameweek_id']]
                next_gw_args = format_null_args(next_gw_args)
                execute_from_file('update_next_squad_gameweek.sql', tuple(next_gw_args))


def insert_player_gameweek():

    """Insert player gameweek row for next gameweek."""

    current_gw_id = Bootstrap.get_current_gw_id()
    all_player_ids = read_all_player_ids()

    for player_id in all_player_ids:
        print(player_id)
        args = [int(player_id), int(current_gw_id+1)]
        try:
            args.append(Player(player_id).get_projected_points(current_gw_id+1))
        except:
            print(f'Missing player_gameweek data for player {player_id}')
            args.append(None)
        args = format_null_args(args)
        execute_from_file('insert_player_gameweek.sql', tuple(args))


def update_player_gameweek(player_gameweeks_df: pd.DataFrame):

    """Update player gameweek row for gameweek just gone."""

    current_gw_id = Bootstrap.get_current_gw_id()

    trimmed_df = player_gameweeks_df[player_gameweeks_df['gameweek_id'] == current_gw_id]
    for index, row in trimmed_df.iterrows():
        args = [row['started'],
                row['minutes_played'],
                row['goals'],
                row['assists'],
                row['penalty_goals'],
                row['penalty_attempts'],
                row['yellow_cards'],
                row['red_cards'],
                row['xG'],
                row['npxG'],
                row['xA'],
                row['points_scored'],
                row['player_id'],
                row['gameweek_id']]
        args = format_null_args(args)
        # try:
        #    projected_points = Player(row['player_id']).get_projected_points(current_gw_id)
        # except:
        #     print(f'Missing player_gameweek data for player {row['player_id']}')
        #     projected_points = 'NULL'
        # execute_from_file('insert_player_gameweek.sql', (row['player_id'], row['gameweek_id'], projected_points)) # TEMPORARY FIX! REMOVE BEFORE NEXT GAMEWEEK IF FIXED
        execute_from_file('update_player_gameweek.sql', tuple(args))

    # Delete duplicate entries (often caused by players on loan from one squad to another e.g. Cole Palmer in 23/24)
    execute_from_file('delete_duplicates_player_gameweek.sql', tuple())


def update_projected_points(gw_id: int):

    """Update projected points after changes to model."""

    all_player_ids = read_all_player_ids()

    for player_id in all_player_ids:
        args = []
        try:
            args.append(Player(player_id).get_projected_points(gw_id))
        except:
            args.append(None)
        args.extend([player_id, gw_id])
        args = format_null_args(args)
        execute_from_file('update_projected_points.sql', tuple(args))


def update_gameweek():

    """Update gameweek table."""

    me = User(os.environ.get('ME'))
    current_gw = [i for i in Bootstrap.all_events if i['id'] == Bootstrap.get_current_gw_id()][0]
    gw_id = current_gw['id']

    current_gw_args = (me.manager_summary['summary_event_points'], 
                        current_gw['average_entry_score'],
                        gw_id)
    next_gw_args = (me.current_team.get_projected_points(),
                    gw_id+1)
    
    execute_from_file('update_previous_gameweek.sql', (gw_id, gw_id))
    execute_from_file('update_current_gameweek.sql', current_gw_args)
    execute_from_file('update_next_gameweek.sql', next_gw_args)


def update_my_team():
    
    """Update my team table."""

    my_team_df = get_my_team_data(User(os.environ.get('ME')))
    i = 1
    for index, row in my_team_df.iterrows():
        args = [
            row['player_id'],
            row['is_captain'],
            row['is_vice_captain'],
            row['is_benched'],
            row['purchase_price'],
            row['selling_price'],
            i
        ]
        args = format_null_args(args)

        execute_from_file('update_my_team.sql', tuple(args))

        i += 1


if __name__ == '__main__':
    #post_gameweek_update()
    #update_projected_points(25)
    update_my_team()
    #bulk_update()