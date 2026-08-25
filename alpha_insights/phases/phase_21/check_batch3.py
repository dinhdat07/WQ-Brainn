import os
import json
import requests
import time

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.post(f"{API_BASE}/authentication")

sims = ['DLAcC4Bo4q8ce3fZmsMh62', '2oIboPdct50xakqvYGY8ifs', '1DhxFdccu4nZbcjGR3E3YxJ']

for sim_id in sims:
    while True:
        resp = session.get(f"{API_BASE}/simulations/{sim_id}")
        if resp.status_code == 200:
            if resp.json().get("status") in ["DONE", "COMPLETE"]:
                alpha_id = resp.json().get("alpha")
                break
            elif resp.json().get("status") in ["ERROR", "WARNING"]:
                alpha_id = None
                print(f"Simulation {sim_id} failed.")
                break
            else:
                time.sleep(2)
        else:
            time.sleep(2)

    if alpha_id:
        resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
        if resp.status_code == 200:
            is_metrics = resp.json().get("is", {})
            print(f"\n=== METRICS for {alpha_id} ===")
            print(f"Sharpe: {is_metrics.get('sharpe')}")
            print(f"Fitness: {is_metrics.get('fitness')}")
            print(f"Turnover: {is_metrics.get('turnover')}")
            for check in is_metrics.get("checks", []):
                if check.get("name") in ["LOW_SHARPE", "LOW_SUB_UNIVERSE_SHARPE", "SELF_CORRELATION"]:
                    print(f"{check.get('name')}: {check.get('result')}")
