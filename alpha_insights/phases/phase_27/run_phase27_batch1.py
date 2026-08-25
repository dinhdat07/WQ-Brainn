import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"

# 1. Credentials
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

# 2. Session
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

def simulate(expression, trunc_val=0.08, neut="SUBINDUSTRY"):
    data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": neut,
            "truncation": trunc_val,
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
                print(f"Spawned: {sim_id} for expr:\n{expression[:100]}...\n")
                return sim_id
            elif response.status_code == 429:
                print("429 limit, sleeping 30s")
                time.sleep(30)
            elif response.status_code == 401:
                session.post(f"{API_BASE}/authentication")
            elif response.status_code == 400:
                print(f"Bad Request for expression (Syntax Error?): {response.json()}")
                return None
            else:
                print(f"Error {response.status_code} {response.text}")
                return None
        except Exception:
            time.sleep(10)

expressions = [
    # 1. Post-News Advantageous Momentum
    "ts_decay_linear(group_rank(ts_sum(optimal_position_indicator, 20), sector), 10)",
    
    # 2. Dilution Trap (Annual data, needs backfill)
    "ts_decay_linear(group_rank(-ts_backfill(fn_comp_non_opt_grants_a, 252) / cap, sector), 10)",
    
    # 3. Options Breakeven Expectation
    "ts_decay_linear(group_rank((option_breakeven_30 - close) / close, sector), 10)",
    
    # 4. Conviction-Weighted Social Sentiment
    "ts_decay_linear(group_rank(snt_social_value * snt_social_volume, sector), 10)"
]

sims = []
for expr in expressions:
    sims.append(simulate(expr))
    time.sleep(2)

print("Waiting 60 seconds for metrics...")
time.sleep(60)

for sim_id in sims:
    if not sim_id: continue
    while True:
        resp = session.get(f'{API_BASE}/simulations/{sim_id}')
        if resp.status_code == 401:
            session.post(f'{API_BASE}/authentication')
            continue
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status")
            if status in ["PENDING", "RUNNING"]:
                time.sleep(10)
                continue
                
            print(f'\n--- SIM {sim_id} ---')
            print(f'Status: {status}')
            if status == "ERROR":
                print(f"Error: {data.get('message', 'Unknown')}")
            
            if 'alpha' in data:
                alpha_id = data['alpha']
                while True:
                    alpha_resp = session.get(f'{API_BASE}/alphas/{alpha_id}')
                    if alpha_resp.status_code == 200:
                        is_metrics = alpha_resp.json().get('is', {})
                        if is_metrics:
                            print(f'Alpha ID: {alpha_id}')
                            print(f'Sharpe: {is_metrics.get("sharpe")}')
                            print(f'Fitness: {is_metrics.get("fitness")}')
                            print(f'Turnover: {is_metrics.get("turnover")}')
                            print(f'Margin: {is_metrics.get("margin")}')
                            break
                        else:
                            time.sleep(5)
            break
        else:
            print(f"Failed to get {sim_id}: {resp.status_code} {resp.text}")
            break
