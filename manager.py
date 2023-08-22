from team import Team
from league import League
from bootstrap import Bootstrap


class Manager:

    def __init__(self, manager_id: int, is_user: bool = False):
        self.manager_id = manager_id
        self.manager_summary = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/entry/{self.manager_id}/').json()
        self.current_team = Team(manager_id, is_user=is_user)
        self.classic_leagues = Manager.get_leagues(self, league_type='classic')
        self.h2h_leagues = Manager.get_leagues(self, league_type='h2h')

    def get_leagues(self, league_type: str = 'classic') -> list[League]:

        """Returns list of Leagues of given type in which Manager competes."""

        leagues = []
        for league in self.manager_summary['leagues'][league_type]:
            league = League(league['id'])
            leagues.append(league)

        return leagues

    def get_rank_in_league(self, league: League):

        """Returns Manager's rank in given League."""

        rank = 0

        for search_league in self.manager_summary['leagues'][league.league_type]:
            if search_league['id'] == league.league_id:
                rank = search_league['entry_rank']
                break

        return rank