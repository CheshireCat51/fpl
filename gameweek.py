from utils import get_bootstrap_summary


class Gameweek:

    bootstrap_summary = get_bootstrap_summary()

    def __init__(self): 
        pass

    def get_current_gw_id():

        current_gw_id = 0

        for event in Gameweek.bootstrap_summary['events']:
            current_gw_id = event['id']
            if event['is_current'] == True:
                break
            elif event['is_next'] == True:
                current_gw_id -= 1
                
        return current_gw_id