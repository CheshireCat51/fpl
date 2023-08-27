from bootstrap import Bootstrap
from player import Player
from team import Team


class League():

    def __init__(self, league_id: int):
        self.league_id = league_id
        self.league_summary = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/').json()
        self.league_name = self.league_summary['league']['name']
        self.league_type = League.get_league_type(self.league_summary['league']['scoring'])

    def get_league_type(scoring_type: str):

        if scoring_type == 'c':
            league_type = 'classic'
        elif scoring_type == 'h2h':
            league_type = 'h2h'
        else:
            league_type = None

        return league_type
    
    def get_player_ownership(self, player: Player, user_id: int) -> int | None:

        """Returns the ownership % of Player in given league."""

        num_managers = len(self.league_summary['standings']['results'])

        assert num_managers != 0

        num_managers_owning = 0
        num_managers_below_owning = 0
        num_managers_above_owning = 0
        user_rank = League.get_manager_rank(self, user_id)
        for manager in self.league_summary['standings']['results']:

            if manager['id'] != user_id:
                    
                players = Team(manager['entry']).get_players()
                for selection in players:
                    if selection.player_id == player.player_id:
                        num_managers_owning += 1

                        if manager['rank'] > user_rank:
                            num_managers_below_owning += 1

                        else:
                            num_managers_above_owning += 1
                    
                        break

        return ((num_managers_owning/num_managers), (num_managers_above_owning/num_managers), (num_managers_below_owning/num_managers))
    
    def get_manager_rank(self, manager_id: int) -> int:

        """Returns given Manager's rank in League."""

        rank = -1

        for manager in self.league_summary['standings']['results']:
            if manager['entry'] == manager_id:
                rank = manager['rank']
                break

        return rank
