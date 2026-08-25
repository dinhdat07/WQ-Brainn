import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

def simulate(expression, universe="TOP3000", delay=1, neutralization="SUBINDUSTRY", truncation=0.08):
    data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": universe,
            "delay": delay,
            "decay": 0,
            "neutralization": neutralization,
            "truncation": truncation,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": expression
    }
    
    while True:
        try:
            response = session.post(f"{API_BASE}/simulations", json=data, timeout=10)
            if response.status_code == 201:
                sim_id = response.headers.get("Location").split("/")[-1]
                print(f"Simulation started for {expression[:40]}... ID: {sim_id}")
                return sim_id
            elif response.status_code == 429 or response.status_code == 403:
                print(f"Rate limited (simulate). Waiting...")
                time.sleep(10)
            else:
                print(f"Error starting simulation: {response.status_code}")
                print(response.text)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed in simulate: {e}")
            time.sleep(10)

def check_status(sim_id):
    while True:
        try:
            resp = session.get(f"{API_BASE}/simulations/{sim_id}", timeout=10)
            if resp.status_code == 200:
                if "status" in resp.json():
                    status = resp.json()["status"]
                    if status == "WARNING" or status == "ERROR":
                        print(f"Simulation failed: {status}")
                        return None
                    if status == "DONE" or status == "COMPLETE":
                        alpha_id = resp.json().get("alpha")
                        return alpha_id
            elif resp.status_code == 403 or resp.status_code == 429:
                time.sleep(5)
                continue
            else:
                print(f"Error checking status: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        time.sleep(2)

def print_metrics(alpha_id):
    resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
    if resp.status_code == 200:
        is_metrics = resp.json().get("is", {})
        print(f"\n=== METRICS for {alpha_id} ===")
        print(f"Sharpe: {is_metrics.get('sharpe')}")
        print(f"Fitness: {is_metrics.get('fitness')}")
        print(f"Turnover: {is_metrics.get('turnover')}")
    else:
        print(f"Error getting alpha metrics: {resp.status_code}")

exprs = [
    "ts_decay_linear(group_rank(-unsystematic_risk_last_30_days, subindustry), 10)",
    "ts_decay_linear(group_rank(ts_sum(snt_social_value, 5), subindustry), 10)",
    "ts_decay_linear(group_rank(fscore_bfl_value, subindustry), 10)",
    "ts_decay_linear(group_rank(fscore_bfl_momentum, subindustry), 10)",
    "ts_decay_linear(group_rank(ts_backfill(sales_estimate_value, 60) / cap, subindustry), 10)",
    "ts_decay_linear(group_rank(ts_sum(optimal_position_indicator, 10), subindustry), 10)"
]

sims = []
for i, expr in enumerate(exprs):
    print(f"\nStarting Batch 2 Idea {i+1}")
    sim_id = simulate(expr)
    if sim_id:
        sims.append(sim_id)
    time.sleep(5)

for sim_id in sims:
    alpha_id = check_status(sim_id)
    if alpha_id:
        print_metrics(alpha_id)
