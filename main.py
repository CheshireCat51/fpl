import os
from manager import Manager
from user import User
import pandas as pd
from bootstrap import Bootstrap
from player import Player
import crud


def main():

    """Entrypoint for FPL tracker."""

    for player_id in [17]:
        try:
            fpl_player = Player(player_id)
        except:
            continue
        print(fpl_player.player_id, fpl_player.second_name)
        for gw_id in [7]:
            try:
                xp = fpl_player.get_projected_points(gw_id)
            except Exception as e:
                xp = 0
            try:
                xmins = fpl_player.get_expected_mins(gw_id)[0]
            except Exception as e:
                xmins = 0
            
            print(f'GW{gw_id}')
            print('xP:', xp)
            print('xMins:', xmins)
            print('\n')

    # me = Manager(os.environ.get('ME'))
    # print(me.current_team.get_projected_points())


if __name__ == '__main__':
    main()