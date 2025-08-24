import pandas as pd
from bootstrap import Bootstrap
from crud import execute_from_str, read_all_player_ids, read_attacking_stats_per_90, init_cnx
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from player import Player


def preprocess():

    """Prepping data for ML."""

    current_gw_id = Bootstrap.get_current_gw_id()
    ml_data = []

    for player_id in read_all_player_ids():
        player = Player(player_id)
        print(player_id, player.second_name)
        for gw_id in range(2, current_gw_id):
            try:
                p_results = read_attacking_stats_per_90(player_id, player.prev_player_id, gw_id)
            except TypeError:
                continue

            pgw_query = f'SELECT goals, assists, npxG, xA, minutes_played, xMins, points_scored, squad_gameweek_id, projected_points FROM player_gameweek WHERE player_id = {player_id} AND gameweek_id = {gw_id} AND minutes_played IS NOT NULL'
            try:
                pgw_results = execute_from_str(pgw_query, init_cnx()).fetchall()[0]
            except IndexError:
                continue

            sgw_query = f'SELECT venue, attack_strength, defence_strength, goals_conceded, xG, xGC, opposition_id FROM squad_gameweek WHERE id = {pgw_results[7]}'
            try:
                sgw_results = execute_from_str(sgw_query, init_cnx()).fetchall()[0]
            except IndexError:
                continue

            opp_sgw_query = f'SELECT attack_strength, defence_strength FROM squad_gameweek WHERE squad_id = {sgw_results[6]} AND gameweek_id = {gw_id} AND opposition_id = {player.prem_team_id}'
            try:
                opp_sgw_results = execute_from_str(opp_sgw_query, init_cnx()).fetchall()[0]
            except IndexError:
                continue
        
            row = {
                'player': player_id,
                'pos': player.position,
                'pen_rank': player.player_summary['penalties_order'],
                'gw': gw_id,
                'venue': sgw_results[0],
                'attack_strength': sgw_results[1],
                'defence_strength': sgw_results[2],
                'opp_attack_strength': opp_sgw_results[0],
                'opp_defence_strength': opp_sgw_results[1],
                # 'team_xG': sgw_results[3],
                # 'team_xGC': sgw_results[4],
                'minutes_played': pgw_results[4],
                'goals': pgw_results[0],
                'assists': pgw_results[1],
                'goals_conceded': sgw_results[3],
                # 'npxG_per_90': p_results[0],
                # 'xA_per_90': p_results[1],
                'npxG': pgw_results[2],
                'xA': pgw_results[3],
                'xMins': pgw_results[5],
                'points_scored': pgw_results[6],
                'stat_xPts': pgw_results[8]
            }
            ml_data.append(row)

    df = pd.DataFrame(ml_data, columns=row.keys())
    df = df.fillna(0)
    df = df[df['minutes_played'] != 0]
    
    df.to_csv('train.csv', index=False)

    return df


def gradient_boosting():

    """Using gradient boosting to predict future points."""

    df = pd.read_csv('train.csv')
    df = df[df['xMins'] != 0]

    X = df.drop(columns=['points_scored', 'stat_xPts', 'xMins', 'goals', 'assists', 'goals_conceded', 'gw'])
    X[['player', 'pos', 'pen_rank', 'venue']] = X[['player', 'pos', 'pen_rank', 'venue']].astype('category')
    y = df['points_scored']

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
        n_estimators=1000,  # Number of boosting rounds
        learning_rate=0.1, # Shrinks contribution of each tree
        max_depth=6,        # Depth of each tree
        subsample=0.8,      # Randomly select a fraction of training data
        colsample_bytree=0.5, # Randomly select a fraction of features
        random_state=42,
        early_stopping_rounds=1000,
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

    new_test = pd.DataFrame(data=[[328,'MID',2.0,'Home',2.21,1.21,1.23,1.58,84.4648,0.5983,0.3895]], columns=X_test.columns)
    new_test[['player', 'pos', 'pen_rank', 'venue']] = new_test[['player', 'pos', 'pen_rank', 'venue']].astype('category')

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
    preprocess()
    gradient_boosting()
    test_stat_method()