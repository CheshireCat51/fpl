from requests import Session
from team import Team


class Manager:

    def __init__(self, session: Session, manager_id: int, is_me: bool = False):
        if is_me:
            team = Team()
        else:
            team = Team()

        self.team = team
