from manager import Manager
import requests
import json


class User(Manager):

    def __init__(self, manager_id: int):
        super().__init__(manager_id, is_user=True)


def generate_team_json(team_id):

    """Get info about current selected team."""

    BASE_URL = "https://fantasy.premierleague.com/api"
    with requests.Session() as session:
        static_url = f"{BASE_URL}/bootstrap-static/"
        static = session.get(static_url).json()
        next_gw = [x for x in static["events"] if x["is_next"]][0]["id"]

        start_prices = {x["id"]: x["now_cost"] - x["cost_change_start"] for x in static["elements"]}
        gw1_url = f"{BASE_URL}/entry/{team_id}/event/1/picks/"
        gw1 = session.get(gw1_url).json()

        transfers_url = f"{BASE_URL}/entry/{team_id}/transfers/"
        transfers = session.get(transfers_url).json()[::-1]

        chips_url = f"{BASE_URL}/entry/{team_id}/history/"
        chips = session.get(chips_url).json()["chips"]
        free_hit = [x for x in chips if x["name"] == "freehit"]
        if free_hit:
            free_hit = free_hit[0]["event"]

    # squad will remain an ID:purchase_price map throughout iteration over transfers
    # once they have been iterated through, can then add on the current selling price
    squad = {x["element"]: start_prices[x["element"]] for x in gw1["picks"]}

    itb = 1000 - sum(squad.values())
    for t in transfers:
        if t["event"] == free_hit:
            continue
        itb += t["element_out_cost"]
        itb -= t["element_in_cost"]
        del squad[t["element_out"]]
        squad[t["element_in"]] = t["element_in_cost"]

    free_transfers = get_free_transfers(transfers, next_gw, free_hit)
    my_data = {
        "chips": [],
        "picks": [],
        "team_id": team_id,
        "transfers": {
            "bank": itb,
            "limit": free_transfers,
            "made": 0,
        }
    }

    for player_id, purchase_price in squad.items():
        now_cost = [x for x in static["elements"] if x["id"] == player_id][0]["now_cost"]

        diff = now_cost - purchase_price
        if diff > 0:
            selling_price = purchase_price + (diff // 2)
        else:
            selling_price = now_cost

        my_data["picks"].append(
            {
                "element": player_id,
                "purchase_price": purchase_price,
                "selling_price": selling_price,
            }
        )

    return my_data


def get_free_transfers(transfers, next_gw, free_hit):

    """Returns number of free transfers."""

    n_transfers = {gw: 0 for gw in range(2, next_gw)}

    for t in transfers:
        n_transfers[t["event"]] += 1
        
    free_transfers = {gw: 0 for gw in range(2, next_gw + 1)}
    free_transfers[2] = 1

    for i in range(3, next_gw + 1):
        if (i - 1) == free_hit:
            free_transfers[i] = 1
            continue
        free_transfers[i] = free_transfers[i - 1]
        free_transfers[i] -= n_transfers[i - 1]
        free_transfers[i] = max(free_transfers[i], 0)
        free_transfers[i] += 1
        free_transfers[i] = min(free_transfers[i], 2)

    return free_transfers[next_gw]


if __name__ == '__main__':
    with open('my_team_data.json', 'w') as file:
        json.dump(generate_team_json(4361245), file)