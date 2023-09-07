from bootstrap import Bootstrap


class Player:

    def __init__(self, player_id: int):
        for player in Bootstrap.all_players:
            if player['id'] == player_id:
                self.player_summary = player
                break

        self.player_id = player_id
        self.first_name = player['first_name']
        self.second_name = player['second_name']

        prem_team = Bootstrap.get_prem_team_by_id(self.player_summary['team'])
        self.prem_team_id = prem_team['id']
        self.prem_team_name = prem_team['name']
        
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
    
    def get_next_x_fixtures(self, num_fixtures: int = 6):

        fixtures = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/fixtures?team={self.prem_team_id}').json()

        opposition_difficulty = {}
        for i in range(num_fixtures+1):
            for fixture in fixtures:
                if fixture['event'] == Bootstrap.get_current_gw_id()+i and fixture['finished'] == False:
                    if fixture['team_a'] == self.prem_team_id:
                        opposition_difficulty[Bootstrap.get_prem_team_by_id(fixture['team_h'])['name']] = fixture['team_a_difficulty']
                    else:
                        opposition_difficulty[Bootstrap.get_prem_team_by_id(fixture['team_a'])['name']] = fixture['team_h_difficulty']
                    break

        return opposition_difficulty

    def get_stats(self):

        stats = {'total': {}, 'per 90': {}}

        for key in stats.keys():
            if key == 'total':
                suffix = ''
            else:
                suffix = '_per_90'
            stats[key]['xG'] = self.player_summary[f'expected_goals{suffix}']
            stats[key]['xA'] = self.player_summary[f'expected_assists{suffix}']
            stats[key]['xGI'] = self.player_summary[f'expected_goal_involvements{suffix}']
            stats[key]['xGC'] = self.player_summary[f'expected_goals_conceded{suffix}']

        return stats
        