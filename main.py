import os
from manager import Manager
from user import User
import pandas as pd
from bootstrap import Bootstrap
from player import Player
import crud


def main():

    """Entrypoint for FPL tracker."""

    for player_id in [16]:
        player = Player(player_id)
        print(player.second_name)
        print(crud.read_attacking_stats_per_90(player_id, crud.read_prev_player_id(player.full_name, crud.init_cnx('previous')), 5))
        print(player.get_projected_points(8))
        print('\n')

    # me = Manager(os.environ.get('ME'))
    # gabriel = Player(3)
    # for league in me.get_leagues():
    #     if league.league_name not in ['Brentford', 'Overall', 'Gameweek 1', 'England', 'Second Chance', 'Sky Sports League']:
    #         print(league.league_name)
    #         print(league.get_player_ownership(gabriel, int(os.environ.get('ME'))))
    #         print('\n')
    # print(me.current_team.get_projected_points())


if __name__ == '__main__':
    main()