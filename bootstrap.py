import requests
from requests import Session
import time
from unidecode import unidecode


# Most of these functions can now be replaced by DB queries in crud.py

class Bootstrap:

    session = requests.session()
    summary = session.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    all_prem_teams = summary['teams']
    all_players = summary['elements']
    all_events = summary['events']


    def get_current_gw_id() -> int:

        """Returns id of current GW."""

        current_gw_id = 0

        for event in Bootstrap.all_events:
            current_gw_id = event['id']
            if event['is_current'] == True:
                break
                
        return current_gw_id
    

    def get_prem_team_by_id(search_id: int):

        """Returns prem team details from FPL API for given team id."""

        selected_prem_team = None

        for prem_team in Bootstrap.all_prem_teams:
            if prem_team['id'] == search_id:
                selected_prem_team = prem_team
                break

        return selected_prem_team
    

    def get_prem_team_by_name(search_name: str):

        """Returns prem team details from FPL API for given team name."""

        selected_prem_team = None

        for prem_team in Bootstrap.all_prem_teams:
            if prem_team['name'] == search_name:
                selected_prem_team = prem_team
                break

        return selected_prem_team
    
    
    def get_player_by_id(search_id: int):

        """Returns player details from FPL API for given player id."""

        selected_player = None

        for player in Bootstrap.all_players:
            if player['id'] == search_id:
                selected_player = player
                break

        return selected_player
    

    def get_player_by_name(search_name: str):

        """WIP!! Returns player details from FPL API for given player name."""

        selected_player = None
        search_name = unidecode(search_name).lower()
        split_name = search_name.split(' ')

        # Exception built for...
        if search_name == 'rodri':
            return [i for i in Bootstrap.all_players if i['web_name'] == 'Rodrigo'][0]
        elif search_name == 'kevin de bruyne':
            return [i for i in Bootstrap.all_players if i['web_name'] == 'De Bruyne'][0]
        else:
            for player in Bootstrap.all_players:
                player_full_name = unidecode(player['first_name'] + ' ' + player['second_name']).lower()
                player_web_name = unidecode(player['web_name']).lower()
                if search_name == player_web_name:
                    selected_player = player
                    break
                if player_full_name == search_name:
                    selected_player = player
                    break
                elif search_name in player_full_name:
                    selected_player = player
                    break
                elif split_name[0] in player_full_name and split_name[1] in player_full_name:
                    selected_player = player
                    break

            return selected_player
    

if __name__ == '__main__':
    print(Bootstrap.get_player_by_name('Kevin De Bruyne'))