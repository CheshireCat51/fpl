import os
import pandas as pd
import math
from scipy.integrate import quad
import pandas as pd
from bootstrap import Bootstrap
import subprocess


def poisson_distribution(k: int, lam: float):

    """Returns probability of k events taking place according to Poisson distribution with mean lam."""

    return ((lam**k)*math.e**(-lam))/math.factorial(k)


def normal_distribution(mu: float, sigma: float, limits: tuple):

    """Returns probability of event outcome falling within given limits according to Normal distribution with mean mu and std sigma."""

    normal_prob_density = lambda x: (1/(sigma*math.sqrt(2*math.pi)))*math.e**(-(1/2)*((x-mu)/sigma)**2)

    return quad(normal_prob_density, limits[0], limits[1])[0]


def format_deadline_str(deadline: str):

    """Returns str in MySQL datetime format."""

    deadline_str = deadline.replace('Z', '').replace('T', ' ')

    return deadline_str


def format_null_args(args: list):

    """Replace nan args with NULL such they are readable by MySQL."""

    return ['NULL' if pd.isna(i) else i for i in args]


def except_future_gw(gw_id: int):

    """Return next gw_id if specified gw_id is further in future than next gw. Used to fetch current team strength data."""

    next_gw_id = Bootstrap.get_current_gw_id()+1

    if gw_id > next_gw_id:
        return next_gw_id
    else:
        return gw_id
    

def format_elevenify_data(gw_id: int):

    """Read and format elevenify data to csv."""

    file_path = f'./elevenify/elev_{gw_id}.csv'

    with open(file_path, 'r', encoding='utf-8') as team_strengths_file:
        team_strengths = team_strengths_file.read()
        team_strengths = team_strengths.replace('−', '-').splitlines()

    rows = []
    for team in team_strengths[::2]:
        row = team.split('\t')[1:]
        if len(row) == 0:
            continue
        row.pop(1)  # Remove empty entries
        rows.append(row)

    df = pd.DataFrame(rows, columns=['Team', 'Attack', 'Defence', 'Overall'])
    df.to_csv(file_path, index=False)


def backup_db(database, output_file):

    """
    Dump a MySQL database to a file.
    
    Args:
        host (str): The hostname or IP address of the MySQL server.
        user (str): The MySQL username.
        password (str): The MySQL password.
        database (str): The name of the database to dump.
        output_file (str): The file path to save the dump.

    Returns:
        bool: True if dump succeeded, False otherwise.
    """
    
    try:
        # Build the mysqldump command
        command = [
            "mysqldump",
            "-h", "localhost",
            "-u", "app",
            f'-p"{os.environ.get('DB_PASS')}"',  # Note: No space between `-p` and the password
            database
        ]
        command = ' '.join(command)

        # Open the output file in write mode
        with open(output_file, "w") as file:
            # Execute the command and direct output to the file
            subprocess.run(command, stdout=file, stderr=subprocess.PIPE, check=True)

        print(f"Database dumped successfully to {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error dumping database: {e.stderr.decode('utf-8')}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False


# if __name__ == '__main__':
#     backup_db('fpl_model_2425', './db_backup/fpl_model_2425.sql')


fpl_points_system = {
    'GKP': {
        'Clean Sheet': 4,
        'Goal Scored': 10,
        '3 Saves': 1,
        'Penalty Save': 5,
        '2 Goals Conceded': -1,
    },
    'DEF': {
        'Clean Sheet': 4,
        'Goal Scored': 6,
        '2 Goals Conceded': -1,
    },
    'MID': {
        'Goal Scored': 5,
        'Clean Sheet': 1
    },
    'FWD': {
        'Goal Scored': 4,
    },
    'Other': {
        '< 60 mins': 1,
        '>= 60 mins': 2,
        'Assist': 3,
        'Yellow Card': -1,
        'Red Card': -3,
        'Own Goal': -2,
        'Penalty Miss': -2
    }
}