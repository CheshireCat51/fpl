import os
from manager import Manager
from user import User
import pandas as pd
from bootstrap import Bootstrap
from player import Player
import crud


def main():

    """Entrypoint for FPL tracker."""

    # print('Isak')
    # rogers = Player(401)
    # print(rogers.get_projected_points(21))

    # print('Wood')
    # rogers = Player(447)
    # print(rogers.get_projected_points(21))

    # print('Evanilson')
    # rogers = Player(617)
    # print(rogers.get_projected_points(21))

    # print('JP')
    # rogers = Player(129)
    # print(rogers.get_projected_points(21))

    # for player_id in [3]:
    #     try:
    #         fpl_player = Player(player_id)
    #     except:
    #         continue
    #     print(fpl_player.player_id, fpl_player.second_name)
    #     for gw_id in [15, 16, 17]:
    #         # try:
    #         xp = fpl_player.get_projected_points(gw_id)
    #         # except Exception as e:
    #         #     xp = 0
    #         try:
    #             xmins = fpl_player.get_expected_mins(gw_id)[0]
    #         except Exception as e:
    #             xmins = 0
            
            # print(f'GW{gw_id}')
            # print('xP:', xp)
            # print('xMins:', xmins)
            # print('\n')

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