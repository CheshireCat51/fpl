from requests import Session


class League():

    def __init__(self, session: Session, league_id: int):
        self.league_summary = session.get(f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/')

    def get_ownership(self, player_id: int):
        pass

    def get_ownership_below_me(self, player_id: int):
        pass
    
    def get_ownership_above_me(self, player_id: int):
        pass
