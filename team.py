from player import Player
from bootstrap import Bootstrap
import json


class Team:


    def __init__(self, manager_id: int, gw_id: int = Bootstrap.get_current_gw_id(), is_user: bool = False):

        if is_user:
            try:
                with open('team.json', 'r') as f:
                    team_summary = json.load(f)
                transfers_key = 'transfers'
            except:
                team_summary = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gw_id}/picks/').json()
                transfers_key = 'entry_history'
        else:
            team_summary = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gw_id}/picks/').json()
            transfers_key = 'entry_history'

        self.is_user = is_user
        self.team_summary = team_summary
        self.transfers = team_summary[transfers_key]


    def get_players(self) -> list[Player]:

        """Returns a list of Player objects including all members of the team in the given GW."""

        players = []
        for pick in self.team_summary['picks']:
            player = Player(pick['element'])
            players.append(player)

        return players
    

    def get_captain(self):

        """Returns Player object of captain."""

        for pick in self.team_summary['picks']:
            if pick['is_captain']:
                captain = Player(pick['element'])

        return captain
    

    def get_vice_captain(self):

        """Returns Player object of vice-captain."""
        
        for pick in self.team_summary['picks']:
            if pick['is_vice_captain']:
                vice_captain = Player(pick['element'])

        return vice_captain


    def get_team_value(self):

        """Returns value of team in given GW."""

        team_value = 0

        if self.is_user:
            team_value = self.transfers['value']/10
        else:
            team_value = (self.transfers['value'] - self.transfers['bank'])/10

        return team_value
    

    def get_bank_balance(self):

        """Returns bank balance in given GW."""

        return self.transfers['bank']/10
    

    def get_projected_points(self, gw_id = Bootstrap.get_current_gw_id() + 1):

        """Sum of projected points of the starting 11 of the given team."""

        total_xp = 0
        captain_pts_added = False
        captain_found = False
        for player in self.get_players():
            for pick in self.team_summary['picks']:
                if pick['element'] == player.player_id and pick['multiplier'] != 0 and player.position != 'GKP':
                    xp = player.get_projected_points(gw_id)
                    # check that captain is not suspended, injured or out for another reason
                    if pick['is_captain']:
                        print('C')
                        if xp != 0:
                            xp *= pick['multiplier']
                            captain_found = True
                            captain_pts_added = True
                        else:
                            captain_found = True
                    elif pick['is_vice_captain'] and captain_found == True and captain_pts_added == False:
                        print('VC')
                        xp *= 2
                        captain_pts_added = True
                    total_xp += xp
                    print(player.second_name)
                    print(player.player_id)
                    print(xp)
                    print('\n')
                    break

        try:
            assert captain_pts_added == True
        except AssertionError:
            print('Captain points not added.')

        return total_xp