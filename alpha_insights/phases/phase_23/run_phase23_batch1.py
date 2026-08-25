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
    # 1. Idiosyncratic Risk (Short high risk)
    "ts_decay_linear(group_rank(-unsystematic_risk_last_60_days, subindustry), 15)",
    
    # 2. Idiosyncratic Risk with Market Neutralization
    "ts_decay_linear(group_zscore(-unsystematic_risk_last_30_days, market), 15)",
    
    # 3. Analyst Sales Estimate Dispersion (High dispersion = bad)
    "ts_decay_linear(group_rank(-(sales_estimate_maximum - sales_estimate_minimum) / abs(sales_estimate_value), market), 15)",
    
    # 4. Footnotes: Debt Issuance (High issuance = bad)
    "ts_decay_linear(group_rank(-fn_proceeds_from_issuance_of_debt_a / cap, subindustry), 15)",
    
    # 5. Footnotes combination: Debt + Stock Grants
    "ts_decay_linear(group_rank(-fn_proceeds_from_issuance_of_debt_a / cap, market) + group_rank(-fn_comp_non_opt_grants_a / cap, market), 20)"
]

sims = []
for expr in exprs:
    sims.append(simulate(expr))
    time.sleep(2)

print("Waiting 100 seconds for some metrics to calculate...")
time.sleep(100)

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
