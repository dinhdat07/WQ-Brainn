import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"

# 1. Credentials
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

# 2. Session
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

sims = [
    "3YGp0HdIH4WiaJ6XyIlSIle", # pcr_oi_all
    "2gQKp7aKt4iEclMT89CGbui", # unsystematic risk
    "49VhQgaeM5eLcm1114ixvoUR" # inventory / sales
]

for sim_id in sims:
    while True:
        resp = session.get(f'{API_BASE}/simulations/{sim_id}')
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status")
            print(f'\n--- SIM {sim_id} ---')
            print(f'Status: {status}')
            if status in ["PENDING", "RUNNING"]:
                time.sleep(10)
                continue
                
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
            print(f"Failed to get {sim_id}: {resp.status_code}")
            break
