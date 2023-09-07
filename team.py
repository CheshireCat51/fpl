from player import Player
from bootstrap import Bootstrap


class Team:

    def __init__(self, manager_id: int, gw_id: int = Bootstrap.get_current_gw_id(), is_user: bool = False):

        if is_user and gw_id == Bootstrap.get_current_gw_id():
            team_summary = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/my-team/{manager_id}/').json()
            transfers_key = 'transfers'
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