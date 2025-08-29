import pandas as pd
from bootstrap import Bootstrap
from crud import *
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from player import Player
from utils import fpl_points_system


prev_cnx = init_cnx('previous')


def preprocess():

    """Prepping data for ML."""

    current_gw_id = 38
    ml_data = []

    for player_id in read_all_player_ids():
        player = Player(player_id)
        print(player_id, player.second_name)
        if player.position != 'GKP':
            for gw_id in range(2, current_gw_id):
                try:
                    p_results = read_attacking_stats_per_90(player_id, player.prev_player_id, gw_id)
                except TypeError as e:
                    print(e)
                    continue

                pgw_query = f'SELECT goals, assists, npxG, xA, minutes_played, xMins, points_scored, squad_gameweek_id, projected_points, yellow_cards, red_cards FROM player_gameweek WHERE player_id = {player.prev_player_id} AND gameweek_id = {gw_id} AND minutes_played IS NOT NULL'
                try:
                    pgw_results = execute_from_str(pgw_query, prev_cnx, stat_query=True, fetchall=False)
                except Exception as e:
                    continue

                points_scored = pgw_results[6]

                if player.position == 'DEF':
                    def_con_query = f'SELECT SUM(clearances + blocks + interceptions + tackles) FROM player_gameweek WHERE player_id = {player.prev_player_id} AND gameweek_id = {gw_id} AND minutes_played IS NOT NULL'
                    try:
                        def_con_results = execute_from_str(def_con_query, prev_cnx, stat_query=True, fetchall=False)
                    except Exception as e:
                        continue
                    if def_con_results[0] >= 10:
                        points_scored += fpl_points_system[player.position]['Defensive Contribution']

                elif player.position in ['MID', 'FWD']:
                    def_con_query = f'SELECT SUM(clearances + blocks + interceptions + recoveries + tackles) FROM player_gameweek WHERE player_id = {player.prev_player_id} AND gameweek_id = {gw_id} AND minutes_played IS NOT NULL'
                    try:
                        def_con_results = execute_from_str(def_con_query, prev_cnx, stat_query=True, fetchall=False)
                    except Exception as e:
                        continue
                    if def_con_results[0] >= 12:
                        points_scored += fpl_points_system[player.position]['Defensive Contribution']

                sgw_query = f'SELECT venue, attack_strength, defence_strength, goals_scored, goals_conceded, xG, xGC, opposition_id FROM squad_gameweek WHERE id = {pgw_results[7]}'
                try:
                    sgw_results = execute_from_str(sgw_query, prev_cnx, stat_query=True, fetchall=False)
                except Exception as e:
                    continue

                opp_sgw_query = f'SELECT attack_strength, defence_strength FROM squad_gameweek WHERE squad_id = {sgw_results[7]} AND gameweek_id = {gw_id} AND opposition_id = {player.prem_team_id}'
                try:
                    opp_sgw_results = execute_from_str(opp_sgw_query, prev_cnx, stat_query=True, fetchall=False)
                except Exception as e:
                    continue
            
                row = {
                    'player_id': player.player_id,
                    'player': player.first_name + ' ' + player.second_name,
                    'position': player.position,
                    'gw': str(gw_id),
                    'venue': sgw_results[0],
                    'pen_share': player.get_penalty_returns_per_90(gw_id)[1],
                    'attack_strength': sgw_results[1],
                    'defence_strength': sgw_results[2],
                    'opp_attack_strength': opp_sgw_results[0],
                    'opp_defence_strength': opp_sgw_results[1],
                    'team_xG': sgw_results[4],
                    'team_xGC': sgw_results[5],
                    'minutes_played': pgw_results[4],
                    'goals': pgw_results[0],
                    'assists': pgw_results[1],
                    'goal_share': read_attacking_stats_share(player.player_id, player.prev_player_id)[0],
                    'assist_share': read_attacking_stats_share(player.player_id, player.prev_player_id)[1],
                    'goals_scored': sgw_results[3],
                    'goals_conceded': sgw_results[4],
                    'npxG': pgw_results[2],
                    'xA': pgw_results[3],
                    'npxG_per_90': p_results[0],
                    'xA_per_90': p_results[1],
                    'def_con': def_con_results[0],
                    'yellow_cards': pgw_results[9],
                    'red_cards': pgw_results[10],
                    'xMins': pgw_results[5],
                    'points_scored': points_scored,
                    'stat_xPts': pgw_results[8]
                }
                ml_data.append(row)

    df = pd.DataFrame(ml_data, columns=row.keys())
    df = df.fillna(0)
    df = df[df['minutes_played'] != 0]
    
    df.to_csv('train.csv', index=False)

    return df


def avoid_div_by_zero(player_stat, squad_stat):

    """Prevents division by zero errors."""

    try:
        player_share = float(player_stat)/float(squad_stat)
    except ZeroDivisionError:
        player_share = 0
    except TypeError:
        player_share = 0

    return player_share


def gradient_boosting():

    """Using gradient boosting to predict future points."""

    df = pd.read_csv('train.csv')
    df = df[df['xMins'] != 0]
    df[['player_id', 'player', 'position', 'gw', 'venue']] = df[['player_id', 'player', 'position', 'gw', 'venue']].astype('category')

    X = df.drop(columns=['player_id', 'player', 'gw', 'venue', 'points_scored', 'stat_xPts', 'xMins', 'npxG', 'xA', 'team_xG', 'team_xGC', 'goals_scored', 'goals_conceded', 'goals', 'assists', 'yellow_cards', 'red_cards', 'pen_share', 'def_con', 'npxG_per_90', 'xA_per_90'])
    y = df['points_scored']
    print(X.dtypes)

    # Step 1: Split data into train, validation, and test sets
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)  # Split into test and train
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)  # Split train into validation and train

    xgb_model = train(X_train, X_val, y_train, y_val)
    test(xgb_model, X_test, y_test)
    importance(xgb_model)


def train(X_train, X_val, y_train, y_val):

    """Train XGBoost model."""

    # Initialize the XGBoost regressor
    xgb_model = xgb.XGBRegressor(
        n_estimators=100000,  # Number of boosting rounds
        learning_rate=0.01, # Shrinks contribution of each tree
        max_depth=6,        # Depth of each tree
        subsample=0.9,      # Randomly select a fraction of training data
        colsample_bytree=0.5, # Randomly select a fraction of features
        random_state=42,
        early_stopping_rounds=0,
        eval_metric='rmse',
        enable_categorical=True,
        tree_method='hist'
    )

    # Train the model on training data
    xgb_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=100)
    
    return xgb_model


def test(xgb_model, X_test: pd.DataFrame, y_test):

    """Test XGBoost model."""

    # Predict on test data
    y_pred = xgb_model.predict(X_test)

    player = Player(381)
    gw_id = 4
    npxG_share, xA_share = read_attacking_stats_share(player.player_id, player.prev_player_id)
    # if player.position == 'DEF':
    #     def_con = read_cbit_per_90(player.player_id, player.prev_player_id)[0]
    # elif player.position in ['MID', 'FWD']:
    #     def_con = read_cbirt_per_90(player.player_id, player.prev_player_id)[0]
    # else:
    #     def_con = 0
    new_test = pd.DataFrame(data=[
        [
            # player.first_name + ' ' + player.second_name,
            player.position,
            # player.get_penalty_returns_per_90(gw_id)[1],
            read_attack_strength(player.prem_team_id, gw_id),
            read_defence_strength(player.prem_team_id, gw_id),
            read_attack_strength(player.get_fixture(gw_id)[0]['id'], gw_id),
            read_defence_strength(player.get_fixture(gw_id)[0]['id'], gw_id),
            player.get_expected_mins(gw_id)[0],
            npxG_share,
            xA_share,
            # def_con
        ]
    ], columns=[X_test.columns])
    new_test[['position']] = new_test[['position']].astype('category')
    print(new_test)
    # print(new_test.dtypes)

    # X_test['xMins'] = y_pred[:,0]
    X_test['xPts'] = y_pred
    # X_test['mins'] = y_test['minutes_played']
    X_test['Pts'] = y_test

    # Evaluate the model
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print('### ML metrics ###')
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R-squared Score: {r2:.2f}")

    y_pred = xgb_model.predict(new_test)
    print(y_pred)


def test_stat_method():

    """Get metrics for the stat method."""

    df = pd.read_csv('train.csv')

    df = df[df['stat_xPts'] != 0]

    y_test = df['points_scored']
    y_pred = df['stat_xPts']

    # Evaluate the model
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print('### Stat method metrics ###')
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R-squared Score: {r2:.2f}")


def importance(xgb_model):

    # Plot feature importance
    xgb.plot_importance(xgb_model, importance_type='weight', height=0.5)
    plt.title('Feature Importance')
    plt.show()


if __name__ == '__main__':
    # preprocess()
    gradient_boosting()
    # test_stat_method()