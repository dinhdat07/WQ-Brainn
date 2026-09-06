import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"

# Create Phase 50 directory if not exists
os.makedirs("e:/CODING/MMO/wq-brain/WQ-Brainn/alpha_insights/phases/phase_50", exist_ok=True)

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
    # 1. Social Media Sentiment vs Option Breakeven
    "-1 * ts_decay_linear(group_rank(ts_corr(snt_social_value, option_breakeven_60, 20), subindustry), 60)",
    
    # 2. Alternative Social Sentiment vs Put-Call Volume
    "-1 * ts_decay_linear(group_rank(ts_corr(scl12_sentiment, pcr_vol_30, 40), subindustry), 60)",
    
    # 3. Social Media Sentiment vs Quality
    "-1 * ts_decay_linear(group_rank(ts_corr(snt_social_value, fscore_quality, 60), subindustry), 60)",
    
    # 4. AI Insider vs Dividend (Dividend is highly uncorrelated with fscore)
    "-1 * ts_decay_linear(group_rank(ts_corr(rp_nip_insider, dividend, 60), subindustry), 60)"
]

sims = []
for expr in expressions:
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
