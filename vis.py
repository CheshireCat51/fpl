from matplotlib import pyplot as plt
import pandas as pd
from player import Player
import mplcursors
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from user import User
from dotenv import load_dotenv
import os


# Load environment vars
load_dotenv()
# Create client user object
me = User(os.environ.get('ME'))


def xp_vs_eo(gw_id: int):

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

    my_team = [i['element'] for i in me.optim_data['picks']]
    my_team_xp = xp[xp['ID'].isin(my_team)]
    # xp = xp[~xp['ID'].isin(my_team)]

    # Define the red-to-green colormap
    red_blue_cmap = LinearSegmentedColormap.from_list("RedBlue", ["blue", "red"], 100)

    max_eo = xp['EO'].max()
    max_pts = xp['Total_Pts'].max()
    threat_grad = (xp['Total_Pts']*xp['EO']/100)#/(max_pts*max_eo)
    gain_grad = (xp['Total_Pts']*(1-xp['EO']/100))#/(max_pts*max_eo)

    gain = 0
    for index in xp.index:
        player_id = xp.at[index, 'ID']
        if player_id in my_team_xp['ID'].to_list():
            gain += gain_grad[index]
        elif player_id in xp['ID'].to_list():
            gain -= threat_grad[index]
    print('Expected gain on field over next 8 GWs:', gain)

    plt.scatter(xp['Total_Pts'], xp['EO'], c=threat_grad, cmap=red_blue_cmap)
    plt.colorbar(label='Threat (Pts)')
    # Add tooltips using mplcursors
    cursor = mplcursors.cursor(hover=True)

    plt.scatter(my_team_xp['Total_Pts'], my_team_xp['EO'], c='yellow', label='My Team', edgecolors='green')  # Highlight specific points with a different color
    # plt.plot(xp['Total_Pts'], xp['Total_Pts'], label='Threat contours')
    plt.xlabel('Total xPts over next 8 GWs')
    plt.ylabel('Ownership (%)')
    # plt.legend()

    # Customize the tooltip to display the label for each point
    @cursor.connect("add")
    def on_add(sel):
        index = sel.index  # Index of the hovered point
        player_id = xp.at[index, 'ID']
        if player_id in my_team_xp['ID'].to_list():
            sel.annotation.set_text(f"{xp.at[index, 'Name']}\nGain: {round(gain_grad[index], 2)}")
        elif player_id in xp['ID'].to_list():
            sel.annotation.set_text(f"{xp.at[index, 'Name']}\nThreat: {round(threat_grad[index], 2)}")

    plt.show()


if __name__ == '__main__':
    xp_vs_eo(14)
