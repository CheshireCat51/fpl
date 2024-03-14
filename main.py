import os
from manager import Manager
from user import User
import pandas as pd
# import sasoptpy as so
from bootstrap import Bootstrap
from player import Player


# player_df = pd.DataFrame.from_dict(Bootstrap.all_players, orient='columns')
# prem_team_df = pd.DataFrame.from_dict(Bootstrap.all_prem_teams, orient='columns')


def main():

    """Entrypoint for FPL tracker."""

    # haaland = Player(355)
    # print(haaland.second_name)
    # print(haaland.get_expected_mins(25))
    # print(haaland.get_projected_points(25))

    # nunez = Player(293)
    # print(nunez.second_name)
    # print(nunez.get_expected_mins(25))
    # print(nunez.get_projected_points(25))

    # salah = Player(308)
    # print(salah.second_name)
    # print(salah.get_expected_mins(25))
    # print(salah.get_projected_points(25))

    # salah = Player(362)
    # print(salah.second_name)
    # print(salah.get_expected_mins(25))
    # print(salah.get_projected_points(25))

    # debruyne = Player(349)
    # print(debruyne.second_name)
    # print(debruyne.get_expected_mins(25))
    # print(debruyne.get_projected_points(25))


    # me = Manager(os.environ.get('ME'))
    # print('Me:', me.current_team.get_projected_points(28))
    # # rival = Manager(2320475)
    # # print('Rival:', rival.current_team.get_projected_points(24))

    # for player_id in [86, 630, 89, 321, 203, 407, 526]:
    #     tot_xp = 0
    #     player = Player(player_id)
    #     print(player.second_name)
    #     for gw_id in [30, 31]:
    #         tot_xp += player.get_projected_points(gw_id)
    #     print(tot_xp)
    #     print('\n')

    # porro = Player(506)
    # print(porro.second_name)
    # print(porro.get_expected_mins(27))
    # print(porro.get_projected_points(27))
        
    # bowen = Player(526)
    # print(bowen.second_name)
    # print(bowen.get_expected_mins(28))
    # print(bowen.get_projected_points(28))
        
    son = Player(516)
    print(son.second_name)
    print(son.get_expected_mins(29))
    print(son.get_projected_points(29))


# def solve_gk_problem(budget: float):

#     """Using linear optimisation to pick a lineup and a bench GK."""

#     gkps: list[Player] = []
#     for p in Bootstrap.all_players:
#         if p['element_type'] == 1:
#             gkps.append(Player(p['id']))

#     data = [p.player_id for p in gkps], [p.first_name for p in gkps], [p.second_name for p in gkps], [p.market_price for p in gkps], [p.get_expected_points() for p in gkps]
#     cols = ['Element', 'First', 'Last', 'Price', 'xP']

#     gkp_df = pd.DataFrame(dict(zip(cols, data)))

#     gk_data = gkp_df.copy().reset_index().set_index('Element')
#     model = so.Model(name='gk_model')
#     players = gk_data.index.to_list()

#     # Variables
#     lineup = model.add_variables(players, name='lineup', vartype=so.BIN)
#     bench = model.add_variables(players, name='bench', vartype=so.BIN)

#     # Objective
#     total_xp = so.expr_sum(lineup[p] * float(gk_data.loc[p, 'xP']) for p in players) + 0.1 * so.expr_sum(bench[p] * float(gk_data.loc[p, 'xP']) for p in players)
#     model.set_objective(-total_xp, name='total_xp_obj', sense='N') # cbc minimises by default, therefore we set objective to negative value in order to maximise
    
#     # Constraints
#     model.add_constraints((lineup[p] + bench[p] <= 1 for p in players), name='lineup_or_bench') # cannot have same starting and bench gk
#     model.add_constraint(so.expr_sum(lineup[p] for p in players) == 1, name='single_lineup') # must have starting gk
#     model.add_constraint(so.expr_sum(bench[p] for p in players) == 1, name='single_bench') # must have bench gk
#     model.add_constraint(so.expr_sum((lineup[p] + bench[p]) * (float(gk_data.loc[p, 'Price'])/10) for p in players) <= budget, name='budget_con') # sum of gk prices cannot exceed budget

#     # Solve
#     model.export_mps(filename='gk.mps')
#     command = 'cbc gk.mps solve solu solution.txt'
#     os.system(command)

#     # Parse solution
#     with open('solution.txt', 'r') as f:
#         for v in model.get_variables():
#             v.set_value(0)
#         for line in f:
#             if 'objective value' in line:
#                 continue
#             words = line.split()
#             var = model.get_variable(words[1])
#             var.set_value(float(words[2]))
    
#     # Print solution
#     print('LINEUP')
#     for p in players:
#         if lineup[p].get_value() > 0.5:
#             print(p, gk_data.loc[p])

#     print('\n')

#     print('BENCH')
#     for p in players:
#         if bench[p].get_value() > 0.5:
#             print(p, gk_data.loc[p])


if __name__ == '__main__':
    main()