from bootstrap import Bootstrap
from utils import fpl_points_system, poisson_distribution, normal_distribution
import math
import crud


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
        self.penalty_rank = player['penalties_order']

        prem_team = Bootstrap.get_prem_team_by_id(self.player_summary['team'])
        self.prem_team_id = prem_team['id']
        self.prem_team_name = prem_team['name']
        
        self.ownership = player['selected_by_percent']
        self.current_price = player['now_cost']

        self.player_details = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/element-summary/{self.player_id}/').json()
    

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
    

    def get_chance_of_playing(self) -> int:

        """Returns chance of playing next fixture."""

        chance_of_playing = self.player_summary['chance_of_playing_next_round']
        if chance_of_playing == None:
            chance_of_playing = 100

        return int(chance_of_playing)

    
    def get_next_x_fixtures(self, num_fixtures: int = 6):

        """Returns dictionary of next N fixtures for given N."""

        fixtures = {}
        for i in range(num_fixtures+1):
            gw = Bootstrap.get_current_gw_id()+i
            fixtures[gw] = self.get_fixture(gw)

        return fixtures
    

    def get_fixture(self, gw_id: int):

        """Get the fixture and difficulty for the given GW."""

        gameweek = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/fixtures?team={self.prem_team_id}&event={gw_id}').json()
        opponents = []

        for fixture in gameweek:
            if fixture['team_a'] == self.prem_team_id: # if player's team are away team...
                opponent = {
                    'id': fixture['team_h'],
                    'name': Bootstrap.get_prem_team_by_id(fixture['team_h'])['name']
                }
            else: # else if player's team are home team...
                opponent = {
                    'id': fixture['team_a'],
                    'name': Bootstrap.get_prem_team_by_id(fixture['team_a'])['name']
                }
            opponents.append(opponent)
        
        return opponents
    

    def get_points_scored(self, gw_id: int = Bootstrap.get_current_gw_id()-1):

        """Returns points scored in given gw."""

        for event in self.player_details['history']:
            if event['round'] == int(gw_id):
                return event['total_points']
    

    def get_expected_mins(self, gw_id):

        """Calculate expected mins based on mins already played when a player has started this season and injury status."""

        chance_of_playing = self.get_chance_of_playing()
        mean_mins, std_mins = crud.read_expected_mins(self.player_id, gw_id)
        prob_start_given_in_squad = crud.read_start_proportion(self.player_id, gw_id)
        prob_play_and_start = (chance_of_playing/100)*prob_start_given_in_squad
        mean_mins *= prob_play_and_start

        return mean_mins, std_mins
    

    def get_projected_points(self, gw_id = Bootstrap.get_current_gw_id() + 1):

        """Use xMins, xG, xA and xGC to calculate xP for upcoming GW. 
        Doesn't currently take into account goalkeeper points, BPS, "fantasy" assists, yellow cards or red cards."""

        total_ev = 0
        mean_mins, std_mins = self.get_expected_mins(gw_id)
        mean_attack_strength, mean_defence_strength = crud.read_mean_strengths(gw_id)

        if mean_mins != 0:
            for fixture in self.get_fixture(gw_id):
                opponent_id = fixture['id']
            
                save_ev = 0
                mins_ev = Player.get_mins_returns(mean_mins, std_mins)
                attacking_ev = self.get_attacking_returns_per_90(mean_defence_strength, opponent_id, gw_id)
                pen_ev = self.get_penalty_returns_per_90(gw_id)

                if self.position != 'FWD':
                    defensive_ev = self.get_defensive_returns_per_90(mean_attack_strength, opponent_id, gw_id)
                else:
                    defensive_ev = 0

                total_ev += mins_ev + (defensive_ev + attacking_ev + pen_ev + save_ev)*(mean_mins/90)

                # print(mins_ev)
                # print(defensive_ev)
                # print(attacking_ev)
                # print(pen_ev)
        
        return total_ev
    

    def get_mins_returns(mean_mins: float, std_mins: float) -> float:

        """Returns EV due to mins played. Assumes minutes follow normal distribution."""

        if std_mins > 0:
            if mean_mins > 0:
                less_than_60_ev = normal_distribution(mean_mins, std_mins, (0, 60))*fpl_points_system['Other']['< 60 mins']
                more_than_60_ev = normal_distribution(mean_mins, std_mins, (60, 1000))*fpl_points_system['Other']['>= 60 mins']
                return less_than_60_ev + more_than_60_ev
            else:
                return 0
            
        elif std_mins == 0:
            if mean_mins > 60:
                return 2
            elif 0 < mean_mins < 60:
                return 1
            else:
                return 0


    def get_attacking_returns_per_90(self, mean_defence_strength: float, opponent_id: int, gw_id: int) -> float:

        """Returns EV due to attacking returns. Assumes that adjustment affects every player in the team equally, regardless of position.
            Need to adjust for finishing skill."""

        npxG_per_90, xA_per_90 = crud.read_attacking_stats_per_90(self.player_id)
        opponent_defence_strength = crud.read_defence_strength(opponent_id, gw_id)

        # Adjust for defensive strength of opposition
        adjustment = ((opponent_defence_strength-mean_defence_strength)/mean_defence_strength)+1

        goal_ev = fpl_points_system[self.position]['Goal Scored']*npxG_per_90
        assist_ev = fpl_points_system['Other']['Assist']*xA_per_90

        # Return EV adjusted for expected mins as stats are per 90
        return (goal_ev + assist_ev)*adjustment
    

    def get_defensive_returns_per_90(self, mean_attack_strength: float, opponent_id: int, gw_id: int) -> float:

        """Returns EV due to defensive returns. Assumes goals follow Poisson distribution."""

        defensive_ev = 0
        defence_strength = crud.read_defence_strength(self.prem_team_id, gw_id)
        opponent_attack_strength = crud.read_attack_strength(opponent_id, gw_id)
        
        # Adjust defence strength (i.e. projected goals conceded) for attacking strength of opponent relative to the average prem team
        adjusted_defence_strength = defence_strength*(((opponent_attack_strength-mean_attack_strength)/mean_attack_strength)+1)

        # Where i represents goals conceded...
        for i in range(0, 11):
            prob_concede_i_goals = poisson_distribution(i, adjusted_defence_strength)
            if i == 0:
                defensive_ev += prob_concede_i_goals*fpl_points_system[self.position]['Clean Sheet']
            else:
                try:
                    defensive_ev += prob_concede_i_goals*fpl_points_system[self.position]['2 Goals Conceded']*(math.floor(i/2))
                except KeyError:
                    # print('Midfielder. No penalty for 2 or more goals conceded.')
                    pass

        return defensive_ev
    

    def get_penalty_returns_per_90(self, gw_id: int):

        """Returns EV due to penalties considering likelihood of team winning a penalty, player taking it and converting it.
            Assumes penalty has 0.76 xG and a maximum of 5 pens per squad per game. Need to adjust for player penalty conversion rate."""
        
        pen_ev = 0
        pen_xG = 0.76

        if self.penalty_rank != None:
            mean_pens_per_90 = crud.read_penalty_stats_per_90(self.prem_team_id)
            prob_no_superior_pen_takers_on_pitch = 1
            if self.penalty_rank != 1:
                for pen_taker in [i for i in Bootstrap.all_players if i['team'] == self.prem_team_id and i['penalties_order'] != None]:
                    # If the current pen taker is higher in the pecking order than self...
                    if self.penalty_rank > pen_taker['penalties_order']:
                        prob_no_superior_pen_takers_on_pitch *= (1-(crud.read_expected_mins(pen_taker['id'], gw_id)[0]/90)) 

            for i in range(1, 6):
                prob_attempt_i_pens = poisson_distribution(i, mean_pens_per_90)
                pen_ev += prob_no_superior_pen_takers_on_pitch*prob_attempt_i_pens*pen_xG*fpl_points_system[self.position]['Goal Scored']*i

        return pen_ev
    

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