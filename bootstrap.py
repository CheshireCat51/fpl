import utils


class Bootstrap:

    session = utils.init_session()
    summary = session.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()

    def get_current_gw_id():

        current_gw_id = 0

        for event in Bootstrap.summary['events']:
            current_gw_id = event['id']
            if event['is_current'] == True:
                break
            elif event['is_next'] == True:
                current_gw_id -= 1
                
        return current_gw_id