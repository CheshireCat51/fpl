from matplotlib import pyplot as plt
import pandas as pd
from player import Player
import mplcursors
import numpy as np
from user import User
from manager import Manager
from dotenv import load_dotenv
import os
from crud import execute_from_str, init_cnx
from bootstrap import Bootstrap


# Load environment vars
load_dotenv()


def xp_vs_eo(gw_id: int = Bootstrap.get_current_gw_id()+1):

    """Plot expected points vs expected ownership in order to visualise threat of individual players to a given team."""

    xp = pd.read_csv(f'./optim_data/fplreview_{gw_id}.csv')

    pts_cols = [col_name for col_name in xp.columns if 'Pts' in col_name]

    xp['Total_Pts'] = xp[pts_cols].sum(axis=1)
    xp = xp[xp['Total_Pts'] > 0].reset_index()
    xp['EO'] = 0.0

    for index, player_id in xp['ID'].items():
        player = Player(player_id)
        xp.at[index, 'EO'] = float(player.ownership)

    # xp = xp[xp['EO'] > 0].reset_index()

    # Create client user object
    me = User(os.environ.get('ME'))
    # me = Manager(7103935)
    my_team = [i['element'] for i in me.current_team.team_summary['picks']]
    my_team_xp = xp[xp['ID'].isin(my_team)]
    # not_my_team_xp = xp[~xp['ID'].isin(my_team)]

    max_eo = xp['EO'].max()
    max_pts = xp['Total_Pts'].max()
    threat_grad = xp['Total_Pts']*xp['EO']/100
    gain_grad = xp['Total_Pts']*(1-xp['EO']/100)

    xp['threat'] = threat_grad
    xp['gain'] = gain_grad

    print(xp.sort_values(by='threat', ascending=False).head(15))
    print(xp.sort_values(by='gain', ascending=False).head(15))

    my_team_gain = 0
    for index in xp.index:
        player_id = xp.at[index, 'ID']
        if player_id in my_team_xp['ID'].to_list():
            my_team_gain += gain_grad[index]
        elif player_id in xp['ID'].to_list():
            my_team_gain -= threat_grad[index]

    plt.scatter(xp['Total_Pts'], xp['EO'], c=threat_grad, cmap='turbo')
    plt.colorbar(label='Threat (Pts)')
    
    # Add tooltips using mplcursors
    cursor = mplcursors.cursor(hover=True)

    plt.scatter(my_team_xp['Total_Pts'], my_team_xp['EO'], c='white', label='My Team', edgecolors='black')  # Highlight specific points with a different color
    plt.text(x=0, y=max_eo, s=f'Expected 8 GW gain: {round(my_team_gain, 2)} Pts', fontdict={'size':18})
    # arrow_properties = dict(facecolor='black', arrowstyle='->', lw=1)
    # plt.annotate("", xy=(max_pts-3, max_eo), xytext=(0, max_eo), arrowprops=arrow_properties)
    # plt.text(max_pts/2, max_eo+1, 'Decision Quality', fontsize=12, ha='center', va='center', rotation=0)
    # plt.annotate("", xy=(max_pts, 0), xytext=(max_pts, max_eo-3), arrowprops=arrow_properties)
    # plt.text(max_pts+1, max_eo/2, 'Risk', fontsize=12, ha='center', va='center', rotation=270)
    plt.xlabel('Total xPts over next 8 GWs')
    plt.ylabel('Ownership (%)')

    # Customize the tooltip to display the label for each point
    @cursor.connect("add")
    def on_add(sel):
        index = sel.index  # Index of the hovered point
        player_id = xp.at[index, 'ID']
        if player_id in my_team_xp['ID'].to_list():
            sel.annotation.set_text(f"{xp.at[index, 'Name']}\nGain: {round(gain_grad[index], 2)}")
        elif player_id in xp['ID'].to_list():
            sel.annotation.set_text(f"{xp.at[index, 'Name']}\nThreat: {round(threat_grad[index], 2)}")

    plt.grid(visible=True)
    plt.show()


def xp_vs_pts():

    """Graphing expected against realised points over the season."""

    current_gw_id = Bootstrap.get_current_gw_id()-1

    query = 'SELECT my_projected_points, my_points_scored FROM gameweek'
    results = execute_from_str(query, init_cnx()).fetchall()
    projected = [i[0] for i in results]
    realised = [i[1] for i in results]
    gw_range = range(1,current_gw_id+1)

    plt.plot(gw_range, [sum(projected[1:i]) for i in gw_range], label='Projected')
    plt.plot(gw_range, [sum(realised[1:i]) for i in gw_range], label='Realised')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    xp_vs_eo()
    # xp_vs_pts()
