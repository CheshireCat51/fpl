import os
from manager import Manager
from user import User


manager_id = 4361245


def main():

    """Entrypoint for FPL tracker."""

    me = User(manager_id)

    for player in me.current_team.get_players():
        if player.second_name == 'Maddison':
            selected_player = player
            break 

    for league in me.get_leagues():
        if league.league_name == 'League of legends':
            selected_league = league
            break 

    print(selected_league.get_player_ownership(selected_player, me.manager_id))

    # dad = Manager(os.environ.get('DAD_ID'))
    # print(dad.current_team.bank_balance)
    # print([i.league_name for i in dad.classic_leagues])
    # print([dad.get_rank_in_league(i) for i in dad.classic_leagues])


if __name__ == '__main__':
    main()