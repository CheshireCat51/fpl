import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from io import StringIO


host = 'https://fbref.com'


## METHOD ONE ##

def main():

    url = '/en/comps/9/Premier-League-Stats'
    r = requests.get(host + url)

    soup = BeautifulSoup(r.content, 'lxml')
    squads_standard_stats_table = soup.find('table', {'id': 'stats_squads_standard_for'})
    squads_df = pd.read_html(StringIO(str(squads_standard_stats_table)), header=0)[0]
    squads_df.to_excel('squads.xlsx', header=True)
    squads = squads_standard_stats_table.find_all('th', {'scope': 'row', 'data-stat': 'team'})
    for squad in squads:
        print(squad.text)
        write_squad_data_to_excel(squad)
        time.sleep(10)


def write_squad_data_to_excel(squad):

    squad_stats_page_url = squad.find('a').get('href')
    df = pd.read_html(host + squad_stats_page_url, header=0)[0]

    with pd.ExcelWriter('players.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=squad.text, header=True)


# ## METHOD TWO ##

# def get_all_player_data():

#     df = pd.read_html(host + '/en/comps/9/stats/Premier-League-Stats', match='Player Standard Stats ')
#     df.to_excel('fbref_data_single_sheet.xlsx', header=True)
#     print(df)


if __name__ == '__main__':
    main()