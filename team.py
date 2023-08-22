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

        self.team_summary = team_summary
        self.players = Team.get_players(self)
        self.team_value = Team.get_team_value(self, team_summary[transfers_key])
        self.bank_balance = Team.get_bank_balance(self, team_summary[transfers_key])

    def get_players(self) -> list[Player]:

        """Returns a list of Player objects including all members of the team in the given GW."""

        players = []
        for pick in self.team_summary['picks']:
            player = Player(pick['element'])
            players.append(player)

        return players

    def get_team_value(self, transfers):

        """Returns value of team in given GW."""

        return transfers['value']/10
    
    def get_bank_balance(self, transfers):

        """Returns bank balance in given GW."""

        return transfers['bank']/10