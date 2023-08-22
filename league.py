from bootstrap import Bootstrap


class League():

    def __init__(self, league_id: int):
        self.league_id = league_id
        self.league_summary = Bootstrap.session.get(f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/').json()
        self.league_name = self.league_summary['league']['name']
        self.league_type = League.get_league_type(self)

    def get_league_type(self):

        scoring_type = self.league_summary['league']['scoring']

        if scoring_type == 'c':
            league_type = 'classic'
        elif scoring_type == 'h2h':
            league_type = 'h2h'
        else:
            league_type = None

        return league_type
