import os
from manager import Manager
from user import User
from bootstrap import Bootstrap


manager_id = 4361245


def main():

    """Entrypoint for FPL tracker."""

    me = User(manager_id)
    dad = Manager(os.environ.get('DAD_ID'))

    for player in dad.current_team.get_players():
        if player.second_name == 'Chilwell':
            selected_player = player
            break

    print(selected_player.get_next_x_fixtures())
    print(me.current_team.transfers)

    for league in me.get_leagues():
        if league.league_name == 'Fight and Win!':
            selected_league = league
            break


if __name__ == '__main__':
    main()