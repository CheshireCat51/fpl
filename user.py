from manager import Manager
import requests


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
        fh = [x for x in chips if x["name"] == "freehit"]
        if fh:
            fh = fh[0]["event"]

    # squad will remain an ID:purchase_price map throughout iteration over transfers
    # once they have been iterated through, can then add on the current selling price
    squad = {x["element"]: start_prices[x["element"]] for x in gw1["picks"]}

    itb = 1000 - sum(squad.values())
    for t in transfers:
        if t["event"] == fh:
            continue
        itb += t["element_out_cost"]
        itb -= t["element_in_cost"]
        del squad[t["element_out"]]
        squad[t["element_in"]] = t["element_in_cost"]

    fts = calculate_fts(transfers, next_gw, fh)
    my_data = {
        "chips": [],
        "picks": [],
        "team_id": team_id,
        "transfers": {
            "bank": itb,
            "limit": fts,
            "made": 0,
        }
    }
    for player_id, purchase_price in squad.items():
        now_cost = [x for x in static["elements"] if x["id"] == player_id][0]["now_cost"]

        diff = now_cost - purchase_price
        if diff > 0:
            selling_price = purchase_price + diff // 2
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


def calculate_fts(transfers, next_gw, fh):
    n_transfers = {gw: 0 for gw in range(2, next_gw)}
    for t in transfers:
        n_transfers[t["event"]] += 1
    fts = {gw: 0 for gw in range(2, next_gw + 1)}
    fts[2] = 1
    for i in range(3, next_gw + 1):
        if (i - 1) == fh:
            fts[i] = 1
            continue
        fts[i] = fts[i - 1]
        fts[i] -= n_transfers[i - 1]
        fts[i] = max(fts[i], 0)
        fts[i] += 1
        fts[i] = min(fts[i], 2)
    return fts[next_gw]