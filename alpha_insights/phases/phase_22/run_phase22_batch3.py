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
            elif resp.status_code == 401:
                session.post(f"{API_BASE}/authentication")
            elif resp.status_code == 403 or resp.status_code == 429:
                time.sleep(5)
                continue
        except requests.exceptions.RequestException as e:
            pass
        time.sleep(5)

def print_metrics(alpha_id):
    while True:
        resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
        if resp.status_code == 401:
            session.post(f"{API_BASE}/authentication")
            continue
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
                for check in checks:
                    if check.get("name") in ["LOW_SHARPE", "LOW_SUB_UNIVERSE_SHARPE", "SELF_CORRELATION"]:
                        print(f"Check {check.get('name')}: {check.get('result')} ({check.get('value', '')})")
                return
        time.sleep(10)

exprs = [
    "ts_decay_linear(group_rank(anl4_fs_detail_rec_v4_nd_estimate, subindustry), 10)",
    "ts_decay_linear(group_rank(-anl4_fs_detail_rec_v4_nd_estimate, subindustry), 10)",
    "ts_decay_linear(-group_zscore(scl12_buzz - ts_mean(scl12_buzz, 10), market), 5)",
    "ts_decay_linear(group_rank(pcr_oi_all, subindustry), 10)",
    "ts_decay_linear(group_rank(-unsystematic_risk_last_30_days, sector), 10)",
    "ts_decay_linear(group_rank(fscore_bfl_quality, subindustry), 10)",
    "ts_decay_linear(group_rank(composite_factor_score_derivative, subindustry), 10)"
]

sims = []
for i, expr in enumerate(exprs):
    print(f"\nStarting Batch 3 Idea {i+1}")
    sim_id = simulate(expr)
    if sim_id:
        sims.append(sim_id)
    time.sleep(2)
