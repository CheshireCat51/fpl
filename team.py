from player import Player
from requests import Session, get
from gameweek import Gameweek


class Team:

    current_gw_id = Gameweek.get_current_gw_id()

    def __init__(self, session: Session, manager_id: int, gw_id: int = current_gw_id, is_user_team: bool = False):

        if is_user_team and gw_id == Team.current_gw_id:
            team_summary = session.get(f'https://fantasy.premierleague.com/api/my-team/{manager_id}/').json()
            transfers_key = 'transfers'
        else:
            team_summary = get(f'https://fantasy.premierleague.com/api/entry/{manager_id}/event/{gw_id}/picks/').json()
            transfers_key = 'entry_history'
    
        self.players = Team.get_players(self, team_summary['picks'])
        self.team_value = Team.get_team_value(self, team_summary[transfers_key])
        self.bank_balance = Team.get_bank_balance(self, team_summary[transfers_key])

    def get_players(self, picks):

        """Returns a list of Player objects including all members of the team in the given GW."""

        players = []
        for pick in picks:
            player = Player(pick)
            players.append(player)

        return players

    def get_team_value(self, transfers):
        return transfers['value']/10
    
    def get_bank_balance(self, transfers):
        return transfers['bank']/10