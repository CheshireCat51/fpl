import utils
import requests


class Bootstrap:

    session = requests.session()
    summary = session.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    all_prem_teams = summary['teams']
    all_players = summary['elements']

    def get_current_gw_id():

        current_gw_id = 0

        for event in Bootstrap.summary['events']:
            current_gw_id = event['id']
            if event['is_current'] == True and event['finished'] == False:
                break
            elif event['is_next'] == True:
                break
                
        return current_gw_id
    
    def get_prem_team_by_id(prem_team_id):

        selected_prem_team = None

        for prem_team in Bootstrap.all_prem_teams:
            if prem_team['id'] == prem_team_id:
                selected_prem_team = prem_team
                break

        return selected_prem_team
    
    def get_player_by_id(player_id):

        selected_player = None

        for player in Bootstrap.all_players:
            if player['element'] == player_id:
                selected_player = player
                break

        return selected_player
    

