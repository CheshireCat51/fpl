from bootstrap import Bootstrap
import re


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
            position = 'GKP'
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
                stats[key]['xMins'] = self.get_expected_mins() # average mins played per gw
            stats[key]['xG'] = self.player_summary[f'expected_goals{suffix}']
            stats[key]['xA'] = self.player_summary[f'expected_assists{suffix}']
            stats[key]['xGI'] = self.player_summary[f'expected_goal_involvements{suffix}']
            stats[key]['xGC'] = self.player_summary[f'expected_goals_conceded{suffix}']

        return stats
    
    def get_expected_mins(self):

        """Calculate expected mins based on mins already played this season and injury status."""

        if self.player_summary['status'] == 'a': # a = available
            x_mins = self.player_summary['minutes']/Bootstrap.get_current_gw_id()
        elif self.player_summary['status'] == 'd': # d = doubt
            chance_of_playing = re.findall(r'(\S*)%', self.player_summary['news'])
            x_mins = (self.player_summary['minutes']/Bootstrap.get_current_gw_id()) * int(chance_of_playing[0])/100
        elif self.player_summary['status'] in ['i', 'u']: # i = injured, u = not in prem anymore
            x_mins = 0

        return x_mins
    
    def get_expected_points(self, gw_id: int = Bootstrap.get_current_gw_id()):

        """Use xG, xA and xGC to calculate xP. Doesn't currently take into account BPS."""

        stats_per_90 = self.get_stats()['per 90']
        try:
            clean_sheet_probability = 1/stats_per_90['xGC']
        except ZeroDivisionError:
            clean_sheet_probability = 0

        clean_sheet_pts = 0
        conceed_pts = 0
        save_pts = 0
        goal_pts = 0
        assist_pts = 0
        mins_pts = 0

        if self.find_position() == 'GKP':
            clean_sheet_pts = fpl_points_system['GKP']['Clean Sheet']*clean_sheet_probability
            conceed_pts = fpl_points_system['GKP']['2 Goals Conceded']*(stats_per_90['xGC']/2)
            goal_pts = fpl_points_system['GKP']['Goal Scored']*stats_per_90['xG']
        elif self.find_position() == 'DEF':
            clean_sheet_pts = fpl_points_system['DEF']['Clean Sheet']*clean_sheet_probability
            conceed_pts = fpl_points_system['DEF']['2 Goals Conceded']*(stats_per_90['xGC']/2)
            goal_pts = fpl_points_system['DEF']['Goal Scored']*stats_per_90['xG']
        elif self.find_position() == 'MID':
            clean_sheet_pts = fpl_points_system['MID']['Clean Sheet']*clean_sheet_probability
            goal_pts = fpl_points_system['MID']['Goal Scored']*stats_per_90['xG']
        elif self.find_position() == 'FWD':
            goal_pts = fpl_points_system['FWD']['Goal Scored']*stats_per_90['xG']

        # clean sheet points cap
        if clean_sheet_pts > 4 and self.find_position() in ['GKP', 'DEF']:
            clean_sheet_pts = 4
        elif clean_sheet_pts > 1 and self.find_position() == 'MID':
            clean_sheet_pts = 1
        else:
            pass

        assist_pts = fpl_points_system['Other']['Assist']*stats_per_90['xA']
        
        if stats_per_90['xMins'] >= 60:
            mins_pts = fpl_points_system['Other']['>= 60 mins']
        elif stats_per_90['xMins'] != 0:
            mins_pts = fpl_points_system['Other']['< 60 mins']
        else:
            mins_pts = 0
        
        return clean_sheet_pts + conceed_pts + save_pts + goal_pts + assist_pts + mins_pts


fpl_points_system = {
    'GKP': {
        'Clean Sheet': 4,
        'Goal Scored': 6,
        'Save (per 3 saves)': 1,
        'Penalty Save': 5,
        '2 Goals Conceded': -1,
    },
    'DEF': {
        'Clean Sheet': 4,
        'Goal Scored': 6,
        '2 Goals Conceded': -1,
    },
    'MID': {
        'Goal Scored': 5,
        'Clean Sheet': 1
    },
    'FWD': {
        'Goal Scored': 4,
    },
    'Other': {
        '< 60 mins': 1,
        '>= 60 mins': 2,
        'Assist': 3,
        'Yellow Card': -1,
        'Red Card': -3,
        'Own Goal': -2,
        'Penalty Miss': -2
    }
}
        