import requests
from league import League
from bootstrap import Bootstrap
from manager import Manager


class Player:

    def __init__(self, player_id: int):
        player = Player.find_player(player_id)

        self.player_id = player_id
        self.first_name = player['first_name']
        self.second_name = player['second_name']
        self.ownership = player['selected_by_percent']
        self.prem_team = Player.find_prem_team(player['team'])
        self.market_price = player['now_cost']

    def find_player(player_id: int):
        for player in Bootstrap.summary['elements']:
            if player['id'] == player_id:
                break
        return player
    
    def find_prem_team(prem_team_id: int):
        for prem_team in Bootstrap.summary['teams']:
            if prem_team['id'] == prem_team_id:
                break
        return prem_team['name']
    
    def get_next_x_fixtures(self, num_fixtures: int = 6):
        fixtures = requests.get(f'https://fantasy.premierleague.com/api/fixtures?{Bootstrap.get_current_gw_id()}').json()

    def get_ownership_below_user(self, league: League):

        """Returns the ownership % of Player in given league by Managers ranked below User."""

        pass
    
    def get_ownership_above_user(self, league: League):

        """Returns the ownership % of Player in given league by players ranked below User."""

        pass