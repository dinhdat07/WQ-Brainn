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
                print(f"Simulation started for {expression[:60]}... ID: {sim_id}")
                return sim_id
            elif response.status_code == 429 or response.status_code == 403:
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
                        return resp.json().get("alpha")
            elif resp.status_code == 403 or resp.status_code == 429:
                time.sleep(5)
                continue
        except requests.exceptions.RequestException as e:
            pass
        time.sleep(5)

def print_metrics(alpha_id):
    while True:
        resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
        if resp.status_code == 200:
            is_metrics = resp.json().get("is", {})
            
            # Wait for SELF_CORRELATION check to complete
            checks = is_metrics.get("checks", [])
            corr_check = next((c for c in checks if c["name"] == "SELF_CORRELATION"), None)
            
            if corr_check and corr_check["result"] != "PENDING":
                print(f"\n=== METRICS for {alpha_id} ===")
                print(f"Sharpe: {is_metrics.get('sharpe')}")
                print(f"Fitness: {is_metrics.get('fitness')}")
                print(f"Turnover: {is_metrics.get('turnover')}")
                print(f"Drawdown: {is_metrics.get('drawdown')}")
                for check in checks:
                    if check.get("name") in ["LOW_SHARPE", "LOW_SUB_UNIVERSE_SHARPE", "SELF_CORRELATION"]:
                        print(f"Check {check.get('name')}: {check.get('result')} ({check.get('value', '')})")
                return
            elif not corr_check:
                # Still calculating metrics entirely
                pass
        time.sleep(10)

exprs = [
    "ts_decay_linear(group_zscore(-beta_last_30_days_spy, subindustry) * ts_rank(-historical_volatility_10, 20), 10)",
    "ts_decay_linear(group_rank(earnings_certainty_rank_derivative - ts_mean(earnings_certainty_rank_derivative, 20), sector), 10)",
    "ts_decay_linear(group_rank(option_breakeven_30 / close, subindustry), 5)",
    "trade_when(snt_social_volume < ts_mean(snt_social_volume, 60), group_rank(-snt_social_volume, market), -1)"
]

sims = []
for i, expr in enumerate(exprs):
    print(f"\nStarting Batch 1 Idea {i+1}")
    sim_id = simulate(expr)
    if sim_id:
        sims.append(sim_id)
    time.sleep(2)

print("\nWaiting for simulations to complete and waiting for correlation checks...")
for sim_id in sims:
    alpha_id = check_status(sim_id)
    if alpha_id:
        print_metrics(alpha_id)
