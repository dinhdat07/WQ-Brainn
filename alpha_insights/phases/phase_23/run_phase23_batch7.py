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

def simulate(expression):
    data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
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
                print(f"Spawned: {sim_id} for {expression[:30]}")
                return sim_id
            elif response.status_code == 429:
                print("429 limit, sleeping 30s")
                time.sleep(30)
            elif response.status_code == 401:
                session.post(f"{API_BASE}/authentication")
            else:
                print(f"Error {response.status_code} {response.text}")
                return None
        except Exception:
            time.sleep(10)

exprs = [
    # 1. Smoothed Analyst Revision Rank Derivative
    "ts_decay_linear(group_zscore(-ts_mean(analyst_revision_rank_derivative, 10), subindustry), 15)",
    
    # 2. Smoothed Growth Potential Rank Derivative
    "ts_decay_linear(group_zscore(-ts_mean(growth_potential_rank_derivative, 10), subindustry), 15)",
    
    # 3. Smoothed PCR All
    "ts_decay_linear(group_zscore(-ts_mean(pcr_oi_all, 10), subindustry), 15)",
    
    # 4. Analyst Rec Mean
    "ts_decay_linear(group_zscore(-ts_mean(anl4_fs_detail_rec_v4_nd_estimate, 10), subindustry), 15)",
    
    # 5. Composite Factor Score Derivative
    "ts_decay_linear(group_zscore(-ts_mean(composite_factor_score_derivative, 10), subindustry), 15)"
]

sims = []
for expr in exprs:
    sims.append(simulate(expr))
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
                            print(f'Sharpe: {is_metrics.get("sharpe")}')
                            print(f'Fitness: {is_metrics.get("fitness")}')
                            print(f'Turnover: {is_metrics.get("turnover")}')
                            for check in is_metrics.get('checks', []):
                                if check.get('name') in ['LOW_SHARPE', 'LOW_SUB_UNIVERSE_SHARPE', 'SELF_CORRELATION']:
                                    print(f"Check {check.get('name')}: {check.get('result')} ({check.get('value', '')})")
                            break
                        else:
                            time.sleep(5)
            break
        else:
            print(f"Failed to get {sim_id}: {resp.status_code} {resp.text}")
            break
