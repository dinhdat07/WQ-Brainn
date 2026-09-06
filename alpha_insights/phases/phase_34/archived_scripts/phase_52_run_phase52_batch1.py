import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"

# Create Phase 52 directory if not exists
os.makedirs("e:/CODING/MMO/wq-brain/WQ-Brainn/alpha_insights/phases/phase_52", exist_ok=True)

with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

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
                print(f"Spawned: {sim_id} for expr:\n{expression[:100]}... (Neut: {neut})\n")
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

jobs = [
    # 1. Social vs Volume (Neutralization: SECTOR)
    ("-1 * ts_mean(group_rank(ts_corr(scl12_sentiment, volume, 60), sector), 90)", "SECTOR"),
    
    # 2. Social vs Volatility/Spread (Neutralization: SUBINDUSTRY)
    ("-1 * ts_mean(group_rank(ts_corr(scl12_sentiment, high - low, 60), subindustry), 90)", "SUBINDUSTRY"),
    
    # 3. Social vs Intraday Return (Neutralization: MARKET)
    ("-1 * ts_mean(group_rank(ts_corr(scl12_sentiment, close / open, 60), market), 90)", "MARKET"),
    
    # 4. Same Options logic as Phase 51 but neutralizing by SECTOR instead of SUBINDUSTRY
    ("-1 * ts_mean(group_rank(ts_corr(scl12_sentiment, pcr_vol_60, 90), sector), 90)", "SECTOR")
]

sims = []
for expr, neut in jobs:
    sims.append(simulate(expr, neut=neut))
    time.sleep(2)

print("Waiting 100 seconds for metrics...")
time.sleep(100)

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
