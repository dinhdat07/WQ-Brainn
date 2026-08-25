import os
import json
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.post(f"{API_BASE}/authentication")

for alpha_id in ['6XlnjwxG', 'vRjKrlWb']:
    resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
    if resp.status_code == 200:
        is_metrics = resp.json().get("is", {})
        print(f"\n=== METRICS for {alpha_id} ===")
        print(f"Sharpe: {is_metrics.get('sharpe')}")
        print(f"Fitness: {is_metrics.get('fitness')}")
        print(f"Turnover: {is_metrics.get('turnover')}")
        for check in is_metrics.get("checks", []):
            if check.get("name") in ["LOW_SHARPE", "LOW_SUB_UNIVERSE_SHARPE"]:
                print(f"{check.get('name')}: {check.get('result')}")
