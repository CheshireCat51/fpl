import os
from manager import Manager
from user import User
import pandas as pd
# import sasoptpy as so
from bootstrap import Bootstrap
from player import Player


player_df = pd.DataFrame.from_dict(Bootstrap.all_players, orient='columns')
prem_team_df = pd.DataFrame.from_dict(Bootstrap.all_prem_teams, orient='columns')


def main():

    """Entrypoint for FPL tracker."""

    haaland = Player(355)
    print(haaland.get_expected_mins(25))
    print(haaland.get_projected_points(25))

    nunez = Player(757)
    print(nunez.get_expected_mins(25))
    print(nunez.get_projected_points(25))

    # me = Manager(os.environ.get('ME'))
    # print('Me:', me.current_team.get_projected_points(23))
    # rival = Manager(2320475)
    # print('Rival:', rival.current_team.get_projected_points(21))

    # for player_id in [32, 36, 699, 48, 407, 427, 405, 131, 369]:
    #     tot_xp = 0
    #     player = Player(player_id)
    #     print(player.second_name)
    #     for gw_id in [23, 24, 25, 26]:
    #         tot_xp += player.get_projected_points(gw_id)
    #     print(player.current_price)
    #     print(tot_xp)
    #     print('\n')

    # estu = Player(85)
    # print(estu.second_name)
    # print(estu.get_expected_mins(23))
    # print(estu.get_projected_points(23))


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