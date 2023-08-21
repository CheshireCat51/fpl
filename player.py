from utils import get_bootstrap_summary
import requests
from gameweek import Gameweek


class Player:

    bootstrap_summary = get_bootstrap_summary()

    def __init__(self, player_summary):
        player = Player.find_player(player_summary['element'])

        self.first_name = player['first_name']
        self.second_name = player['second_name']
        self.ownership = player['selected_by_percent']
        self.prem_team = Player.find_prem_team(player['team'])
        self.market_price = player['now_cost']

    def find_player(player_id: int):
        for player in Player.bootstrap_summary['elements']:
            if player['id'] == player_id:
                break
        return player
    
    def find_prem_team(prem_team_id: int):
        for prem_team in Player.bootstrap_summary['teams']:
            if prem_team['id'] == prem_team_id:
                break
        return prem_team['name']
    
    def get_next_x_fixtures(num_fixtures: int = 6):
        fixtures = requests.get(f'https://fantasy.premierleague.com/api/fixtures?{Gameweek.get_current_gw_id()}').json()