import utils


class Bootstrap:

    session = utils.init_session()
    summary = session.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    all_prem_teams = summary['teams']
    all_players = summary['elements']

    def get_current_gw_id():

        current_gw_id = 0

        for event in Bootstrap.summary['events']:
            current_gw_id = event['id']
            if event['is_current'] == True:
                break
            elif event['is_next'] == True:
                current_gw_id -= 1
                
        return current_gw_id
    
    def get_prem_team_by_id(prem_team_id):

        selected_prem_team = None

        for prem_team in Bootstrap.all_prem_teams:
            if prem_team['id'] == prem_team_id:
                selected_prem_team = prem_team
                break

        return selected_prem_team
