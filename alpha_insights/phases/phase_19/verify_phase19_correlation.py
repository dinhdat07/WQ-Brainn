import os
import json
import time
import requests
import numpy as np

API_BASE = "https://api.worldquantbrain.com"

with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

def simulate_and_check(expr):
    settings = {
        "instrumentType": "EQUITY", "region": "USA", "universe": "TOP3000",
        "delay": 1, "decay": 0, "neutralization": "NONE",
        "truncation": 0.08, "pasteurization": "ON", "unitHandling": "VERIFY",
        "nanHandling": "ON", "language": "FASTEXPR", "visualization": False,
    }
    payload = {"type": "REGULAR", "settings": settings, "regular": expr}
    resp = session.post(f"{API_BASE}/simulations", json=payload)
    if resp.status_code != 201:
        print(f"Failed to start simulation: {resp.text}")
        return
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    
    print(f"Started simulation {sim_id}. Waiting for completion...")
    while True:
        data = session.get(f"{API_BASE}/simulations/{sim_id}").json()
        if data.get("status") in ("COMPLETE", "WARNING"):
            aid = data.get("alpha")
            break
        if data.get("status") in ("ERROR", "FAILED"):
            print("Simulation failed.")
            return
        time.sleep(3)
        
    m = session.get(f"{API_BASE}/alphas/{aid}").json()
    metrics = m.get("is", {})
    print(f"Metrics -> Sharpe: {metrics.get('sharpe')}, Fit: {metrics.get('fitness')}, TO: {metrics.get('turnover')}")
    
    # Extract True Sub-universe Sharpe from checks
    checks = metrics.get("checks", [])
    sub_sharpe = None
    for check in checks:
        if check.get("name") == "LOW_SUB_UNIVERSE_SHARPE":
            sub_sharpe = check.get("value")
            break
            
    print(f"TRUE SUB-UNIVERSE SHARPE (WQBrain) : {sub_sharpe}")
    print(f"FINAL ALPHA ID TO SUBMIT: {aid}")

if __name__ == '__main__':
    expr = "trade_when(volume > adv20, -ts_decay_linear(group_neutralize(analyst_revision_rank_derivative, market) + group_neutralize(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), market), 10), -1)"
    simulate_and_check(expr)
