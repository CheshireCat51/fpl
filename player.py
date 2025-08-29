from bootstrap import Bootstrap
from utils import fpl_points_system, poisson_distribution, normal_distribution
import math
import crud


class Player:

    def __init__(self, player_id: int):
        self.player_summary = Player.search_for_player(player_id)

        self.player_id = player_id
        self.first_name = self.player_summary['first_name']
        self.second_name = self.player_summary['second_name']
        self.full_name = self.first_name + ' ' + self.second_name
        self.prev_player_id = crud.read_prev_player_id(self.full_name)
        self.position = self.find_position()
        self.penalty_rank = self.player_summary['penalties_order']

        prem_team = Bootstrap.get_prem_team_by_id(self.player_summary['team'])
        self.prem_team_id = prem_team['id']
        self.prem_team_name = prem_team['name']
        self.prev_prem_team_id = crud.read_prev_squad_id(self.prem_team_name)
        
        self.ownership = self.player_summary['selected_by_percent']
        self.current_price = self.player_summary['now_cost']

        self.player_details = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/element-summary/{self.player_id}/').json()


    def search_for_player(player_id: int):
        
        """Check if player exists in FPL API."""

        player_exists = False

        for player in Bootstrap.all_players:
            if player['id'] == player_id:
                player_exists = True
                break

        if player_exists is False:
            raise Exception(f'Player with id {player_id} does not exist in FPL API.')
        else:
            return player
    

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

        """Get the fixture(s) for the given GW."""

        gameweek = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/fixtures?team={self.prem_team_id}&event={gw_id}').json()
        opponents = []

        for fixture in gameweek:
            if fixture['team_a'] == self.prem_team_id: # if player's team are away team...
                opponent = {
                    'id': fixture['team_h'],
                    'name': Bootstrap.get_prem_team_by_id(fixture['team_h'])['name'],
                    'venue': 'Away'
                }
            else: # else if player's team are home team...
                opponent = {
                    'id': fixture['team_a'],
                    'name': Bootstrap.get_prem_team_by_id(fixture['team_a'])['name'],
                    'venue': 'Home'
                }
            opponents.append(opponent)
        
        return opponents
    

    def get_points_scored(self, gw_id: int = Bootstrap.get_current_gw_id(), opposition_id: int | None = None):

        """Returns points scored in given gw. For DGW, opponent id can be specified to get points returned in specific game.
            If opponent id not specified, returns total."""

        total_gw_points = 0

        for event in self.player_details['history']:
            if event['round'] == int(gw_id):
                if opposition_id == None:
                    total_gw_points += event['total_points']
                elif event['opponent_team'] == opposition_id:
                    total_gw_points += event['total_points']
        
        return total_gw_points
    

    def get_expected_mins(self, gw_id):

        """Calculate expected mins based on mins already played when a player has started this season and injury status."""

        # Assume that suspensions are a maximum of one GW (not correct)
        if self.player_summary['status'].lower() == 's' and gw_id != Bootstrap.get_current_gw_id() + 1:
            chance_of_playing = 1
        else:
            chance_of_playing = min((self.get_chance_of_playing()/100) + max(0.25*(gw_id-(Bootstrap.get_current_gw_id()+1)), 0), 1)  # Ensure chance of playing does not exceed 1
        
        mean_mins, std_mins = crud.read_expected_mins(self.player_id, self.prev_player_id, gw_id)
        prob_start_given_in_squad = crud.read_start_proportion(self.player_id, self.prev_player_id, gw_id)
        prob_play_and_start = chance_of_playing*prob_start_given_in_squad
        x_mins = mean_mins*prob_play_and_start

        return x_mins, std_mins
    

    def get_projected_points(self, gw_id = Bootstrap.get_current_gw_id() + 1, fixture_indices: list = list(range(5))):

        """Use xMins, xG, xA and xGC to calculate xP for upcoming GW. 
            Doesn't currently take into account goalkeeper points, BPS, "fantasy" assists, yellow cards or red cards.
            Assumes that a team will have a maximum of 5 fixtures in a gameweek."""

        total_ev = 0
        mean_mins, std_mins = self.get_expected_mins(gw_id)
        mean_attack_strength, mean_defence_strength = crud.read_mean_strengths(gw_id)

        if mean_mins != 0:
            for index, fixture in enumerate(self.get_fixture(gw_id)):
                if index in fixture_indices:
                    opponent_id = fixture['id']
                
                    save_ev = 0
                    mins_ev = Player.get_mins_returns(mean_mins, std_mins)
                    attacking_ev = self.get_attacking_returns_per_90(mean_defence_strength, opponent_id, gw_id)
                    pen_ev, _ = self.get_penalty_returns_per_90(gw_id)
                    def_con_ev = self.get_def_con_returns_per_90()

                    if self.position != 'FWD':
                        defensive_ev = self.get_defensive_returns_per_90(mean_attack_strength, opponent_id, gw_id)
                    else:
                        defensive_ev = 0

                    total_ev += mins_ev + (defensive_ev + attacking_ev + pen_ev + def_con_ev + save_ev)*(mean_mins/90)

                    # print('Mins:', mins_ev)
                    # print('### Per 90 ###')
                    # print('Defence:', defensive_ev)
                    # print('Attack:', attacking_ev)
                    # print('Penalty:', pen_ev)
        
        return total_ev
    

    def get_mins_returns(mean_mins: float, std_mins: float) -> float:

        """Returns EV due to mins played. Assumes minutes follow normal distribution."""

        if std_mins > 0:
            if mean_mins > 0:
                less_than_60_ev = normal_distribution(mean_mins, std_mins, (0, 60))*fpl_points_system['Other']['< 60 mins']
                more_than_60_ev = normal_distribution(mean_mins, std_mins, (60, 120))*fpl_points_system['Other']['>= 60 mins']
                return less_than_60_ev + more_than_60_ev
            else:
                return 0
            
        elif std_mins == 0:
            if mean_mins > 60:
                return fpl_points_system['Other']['>= 60 mins']
            elif 0 < mean_mins < 60:
                return fpl_points_system['Other']['< 60 mins']
            else:
                return 0


    def get_attacking_returns_per_90(self, mean_defence_strength: float, opponent_id: int, gw_id: int) -> float:

        """Returns EV due to attacking returns. Assumes that adjustment affects every player in the team equally, regardless of position.
            Need to adjust for finishing skill."""

        attacking_ev = 0
        npxG_per_90, xA_per_90 = crud.read_attacking_stats_per_90(self.player_id, self.prev_player_id, gw_id)

        opponent_defence_strength = crud.read_defence_strength(opponent_id, gw_id)

        adjustment = ((opponent_defence_strength-mean_defence_strength)/mean_defence_strength)+1  # Adjust for defensive strength of opposition
        adjusted_npxG = npxG_per_90*adjustment
        adjusted_xA = xA_per_90*adjustment

        # npxG_share, xA_share = crud.read_attacking_stats_share(self.player_id, self.prev_player_id)
        # attack_strength = crud.read_attack_strength(self.prem_team_id, gw_id)
        # npxG_shared = npxG_share*attack_strength*adjustment
        # xA_shared = xA_share*attack_strength*adjustment
        # print('Share method npxG: ', npxG_shared)
        # print('npxG method: ', adjusted_npxG)
        # print('Share method xA: ', xA_shared)
        # print('xA method: ', adjusted_xA)

        attacking_ev = adjusted_npxG*fpl_points_system[self.position]['Goal Scored'] + adjusted_xA*fpl_points_system['Other']['Assist']

        return attacking_ev
    

    def get_likelihood_of_x_or_more_goals(self, num_goals: int, mean_defence_strength: float, opponent_id: int, gw_id: int) -> float:

        """Returns likelihood of scoring x or more goals. Assumes goals follow Poisson distribution."""

        npxG_per_90, xA_per_90 = crud.read_attacking_stats_per_90(self.player_id, self.prev_player_id, gw_id)

        opponent_defence_strength = crud.read_defence_strength(opponent_id, gw_id)

        adjustment = ((opponent_defence_strength-mean_defence_strength)/mean_defence_strength)+1  # Adjust for defensive strength of opposition
        adjusted_npxG = npxG_per_90*adjustment
        adjusted_xA = xA_per_90*adjustment

        prob_score = 0
        prob_assist = 0

        for i in range(num_goals, 8):
            prob_score += poisson_distribution(i, adjusted_npxG)
            prob_assist += poisson_distribution(i, adjusted_xA)

        return prob_score, prob_assist
    

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
                if self.position in ['GKP', 'DEF']:
                    defensive_ev += prob_concede_i_goals*fpl_points_system[self.position]['2 Goals Conceded']*(math.floor(i/2))

        return defensive_ev
    

    def get_penalty_returns_per_90(self, gw_id: int):

        """Returns EV due to penalties considering likelihood of team winning a penalty, player taking it and converting it.
            Assumes penalty has 0.76 xG and a maximum of 5 pens per squad per game. Need to adjust for player penalty conversion rate."""
        
        pen_ev = 0
        pen_share = 0
        pen_xG = 0.76

        if self.penalty_rank is not None:
            mean_pen_attempts_per_90 = crud.read_pen_attempts_per_90()
            squad_pen_xG_per_90 = mean_pen_attempts_per_90*pen_xG
            pen_share = self.get_expected_mins(gw_id)[0]/90

            if self.penalty_rank != 1:
                for pen_taker in [i for i in Bootstrap.all_players if i['team'] == self.prem_team_id and i['penalties_order'] is not None]:
                    # If the current pen taker is higher in the pecking order than self...
                    if pen_taker['penalties_order'] < self.penalty_rank:
                        try:
                            superior_pen_taker = Player(pen_taker['id'])
                            pen_share *= 1-(superior_pen_taker.get_expected_mins(gw_id)[0]/90)
                        except:
                            print(f'Missing penalty data for player {superior_pen_taker.player_id}: {superior_pen_taker.first_name + ' ' + superior_pen_taker.second_name}')
            
            pen_ev = pen_share*squad_pen_xG_per_90*fpl_points_system[self.position]['Goal Scored']

        return pen_ev, pen_share
    

    def get_def_con_returns_per_90(self):

        """Returns EV due to clearances, blocks, interceptions and tackles."""

        if self.position == 'DEF':
            mean_def_con, std_def_con = crud.read_cbit_per_90(self.player_id, self.prev_player_id)
            def_con_threshold = 10
        elif self.position in ['MID', 'FWD']:
            mean_def_con, std_def_con = crud.read_cbirt_per_90(self.player_id, self.prev_player_id)
            def_con_threshold = 12
        else:
            raise Exception(f'Position {self.position} not recognised for CBI(R)T returns.')

        if std_def_con > 0:
            if mean_def_con > 0:
                # Work out likelihood of getting above CBI(R)T threshold
                chance_above_threshold = normal_distribution(mean_def_con, std_def_con, (def_con_threshold, 50))
                above_threshold_ev = chance_above_threshold*fpl_points_system[self.position]['Defensive Contribution']
                # print('Chance of scoring CBI(R)T points:', chance_above_threshold*100, '%')
                return above_threshold_ev
            else:
                return 0
            
        elif std_def_con == 0:
            if mean_def_con > def_con_threshold:
                return fpl_points_system[self.position]['Defensive Contribution']
            else:
                return 0


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