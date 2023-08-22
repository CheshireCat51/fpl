import os
from manager import Manager
from user import User


manager_id = 4361245


def main():

    """Entrypoint for FPL tracker."""

    me = User(manager_id)
    print([i.prem_team for i in me.current_team.players])

    dad = Manager(os.environ.get('DAD_ID'))
    print(dad.current_team.bank_balance)
    print([i.league_name for i in dad.classic_leagues])
    print([dad.get_rank_in_league(i) for i in dad.classic_leagues])


if __name__ == '__main__':
    main()