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
    "ts_decay_linear(group_rank(-parkinson_volatility_30, subindustry), 10)",
    "ts_decay_linear(group_rank(nws18_qcm, subindustry), 10)",
    "ts_decay_linear(group_rank(mean_earnings_evaluation_sentiment, subindustry), 10)",
    "ts_decay_linear(group_rank(mean_merger_acquisition_sentiment, subindustry), 10)"
]

sims = []
for expr in exprs:
    sims.append(simulate(expr))
    time.sleep(2)

print("Waiting 90 seconds for some metrics to calculate...")
time.sleep(90)

for sim_id in sims:
    if not sim_id: continue
    resp = session.get(f'{API_BASE}/simulations/{sim_id}')
    if resp.status_code == 401:
        session.post(f'{API_BASE}/authentication')
        resp = session.get(f'{API_BASE}/simulations/{sim_id}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'\n--- SIM {sim_id} ---')
        print(f'Status: {data.get("status")}')
        if 'alpha' in data:
            alpha_id = data['alpha']
            print(f'Alpha ID: {alpha_id}')
            alpha_resp = session.get(f'{API_BASE}/alphas/{alpha_id}')
            if alpha_resp.status_code == 200:
                is_metrics = alpha_resp.json().get('is', {})
                print(f'Sharpe: {is_metrics.get("sharpe")}')
                print(f'Fitness: {is_metrics.get("fitness")}')
                print(f'Turnover: {is_metrics.get("turnover")}')
                for check in is_metrics.get('checks', []):
                    if check.get('name') in ['LOW_SHARPE', 'LOW_SUB_UNIVERSE_SHARPE', 'SELF_CORRELATION']:
                        print(f"Check {check.get('name')}: {check.get('result')} ({check.get('value', '')})")
