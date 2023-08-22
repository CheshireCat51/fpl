from manager import Manager


class User(Manager):

    def __init__(self, manager_id: int):
        super().__init__(manager_id, is_user=True)