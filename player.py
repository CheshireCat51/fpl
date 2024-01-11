from bootstrap import Bootstrap
from utils import fpl_points_system, poisson_distribution, normal_distribution
import math
import crud
import requests


class Player:

    def __init__(self, player_id: int):
        for player in Bootstrap.all_players:
            if player['id'] == player_id:
                self.player_summary = player
                break

        self.player_id = player_id
        self.first_name = player['first_name']
        self.second_name = player['second_name']
        self.position = self.find_position()

        prem_team = Bootstrap.get_prem_team_by_id(self.player_summary['team'])
        self.prem_team_id = prem_team['id']
        self.prem_team_name = prem_team['name']
        
        self.ownership = player['selected_by_percent']
        self.current_price = player['now_cost']

        self.player_details = requests.get(f'https://fantasy.premierleague.com/api/element-summary/{self.player_id}/').json()
    

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

        fixture_difficulties = {}
        for i in range(num_fixtures+1):
            gw = Bootstrap.get_current_gw_id()+i
            fixture_difficulties[gw] = self.get_fixture(gw)

        return fixture_difficulties
    

    def get_fixture(self, gw_id: int = Bootstrap.get_current_gw_id()+1):

        """Get the fixture and difficulty for the given GW."""

        fixture = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/fixtures?team={self.prem_team_id}&event={gw_id}').json()[0]
        fixture_difficulty = {}

        if fixture['team_a'] == self.prem_team_id: # if player's team are away team...
            fixture_difficulty = {
                'id': fixture['team_h'],
                'name': Bootstrap.get_prem_team_by_id(fixture['team_h'])['name']
            }
        else: # else if player's team are home team...
            fixture_difficulty = {
                'id': fixture['team_a'],
                'name': Bootstrap.get_prem_team_by_id(fixture['team_a'])['name']
            }
        
        return fixture_difficulty


    def get_stats(self):

        stats = {'total': {}, 'per 90': {}}

        for key in stats.keys():
            if key == 'total':
                suffix = ''
            else:
                suffix = '_per_90'
                stats[key]['clean_sheets'] = self.player_summary[f'clean_sheets{suffix}']
            stats[key]['xG'] = self.player_summary[f'expected_goals{suffix}']
            stats[key]['xA'] = self.player_summary[f'expected_assists{suffix}']
            stats[key]['xGI'] = self.player_summary[f'expected_goal_involvements{suffix}']
            stats[key]['xGC'] = self.player_summary[f'expected_goals_conceded{suffix}']

        return stats
    

    def get_points_scored(self, gw_id: int = Bootstrap.get_current_gw_id()-1):

        """Returns points scored in given gw."""

        for event in self.player_details['history']:
            if event['round'] == int(gw_id):
                return event['total_points']
    

    def get_expected_mins(self):

        """Calculate expected mins based on mins already played this season and injury status."""

        if self.player_summary['status'] == 'a': # a = available
            x_mins = self.player_summary['minutes']/(Bootstrap.get_current_gw_id()+1)
        elif self.player_summary['status'] == 'd': # d = doubt
            chance_of_playing = self.player_summary['chance_of_playing_next_round']
            if chance_of_playing == None:
                chance_of_playing = 0
            x_mins = (self.player_summary['minutes']/Bootstrap.get_current_gw_id()) * int(chance_of_playing)/100
        elif self.player_summary['status'] in ['i', 's', 'u']: # i = injured, u = not in prem anymore, s = suspended
            x_mins = 0

        return x_mins
    

    def get_expected_points(self, gw_id: int = Bootstrap.get_current_gw_id()+1):

        """Use xG, xA and xGC to calculate xP. Doesn't currently take into account BPS."""

        save_ev = 0
        defensive_ev = 0
        attacking_ev = self.get_attacking_returns()
        mins_ev = self.get_mins_returns()

        if mins_ev != 0:
            if self.position != 'FWD':
                defensive_ev = self.get_defensive_returns()
            total_ev = save_ev + defensive_ev + attacking_ev + mins_ev

        else:
            total_ev = 0
        
        return total_ev
    

    def get_mins_returns(self) -> float:

        """Returns EV due to mins played. Assumes minutes follow Normal distribution. WORK OUT HOW TO GET STD."""

        x_mins = self.get_expected_mins()

        if x_mins > 0:
            less_than_60_ev = normal_distribution(x_mins, 12, (-1000, 60))*fpl_points_system['Other']['< 60 mins']
            more_than_60_ev = normal_distribution(x_mins, 12, (60, 1000))*fpl_points_system['Other']['>= 60 mins']
            return less_than_60_ev + more_than_60_ev
        else:
            return 0


    def get_attacking_returns(self) -> float:

        """Returns EV due to attacking returns. Assumes Player plays 90 mins."""

        stats_per_90 = self.get_stats()['per 90']

        goal_ev = fpl_points_system[self.position]['Goal Scored']*stats_per_90['xG']
        assist_ev = fpl_points_system['Other']['Assist']*stats_per_90['xA']

        return goal_ev + assist_ev
    

    def get_defensive_returns(self) -> float:

        """Returns EV due to defensive returns. Assumes goals follow Poisson distribution."""

        defensive_ev = 0

        # Where i represents goals conceded...
        for i in range(0, 11):
            prob_concede_i_goals = poisson_distribution(i, crud.read_defence_strength(self.prem_team_id))
            if i == 0:
                defensive_ev += prob_concede_i_goals*fpl_points_system[self.position]['Clean Sheet']
            else:
                try:
                    defensive_ev += prob_concede_i_goals*fpl_points_system[self.position]['2 Goals Conceded']*(math.floor(i/2))
                except KeyError:
                    # print('Midfielder. No penalty for 2 or more goals conceded.')
                    pass

        return defensive_ev
    

    def get_rank_gain_per_point_scored(self):
        
        """Returns places gained by Manager for each point scored by Player.
        Only relevant for Players owned by Manager."""

        self.ownership

        return 


    def get_rank_loss_per_point_scored(self):
        
        """Returns places lost by Manager for each point scored by Player.
        Only relevant for Players not owned by Manager."""

        self.ownership

        return