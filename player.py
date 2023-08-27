import requests
from bootstrap import Bootstrap


class Player:

    def __init__(self, player_id: int):
        for player in Bootstrap.summary['elements']:
            if player['id'] == player_id:
                self.player_summary = player
                break

        self.player_id = player_id
        self.first_name = player['first_name']
        self.second_name = player['second_name']
        
        self.ownership = player['selected_by_percent']
        self.market_price = player['now_cost']
    
    def find_position(self) -> str:
        player_type = self.player_summary['element_type']
        if player_type == 1:
            position = 'GK'
        elif player_type == 2:
            position = 'DEF'
        elif player_type == 3:
            position = 'MID'
        elif player_type == 4:
            position = 'FWD'
        return position
    
    def find_prem_team(self) -> str:
        for prem_team in Bootstrap.summary['teams']:
            if prem_team['id'] == self['team']:
                break
        return prem_team['name']
    
    def get_next_x_fixtures(self, num_fixtures: int = 6):
        fixtures = requests.get(f'https://fantasy.premierleague.com/api/fixtures?{Bootstrap.get_current_gw_id()}').json()

    def get_player_stats(self):

        stats = {'total': {}, 'per 90': {}}

        for suffix in ['', '_per_90']:
            for key in stats.keys():
                stats[key]['xG'] = self.player_summary[f'expected_goals{suffix}']
                stats[key]['xA'] = self.player_summary[f'expected_assists{suffix}']
                stats[key]['xGI'] = self.player_summary[f'expected_goal_involvements{suffix}']
                stats[key]['xGC'] = self.player_summary[f'expected_goals_conceded{suffix}']

        return stats
        