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

sims = [
    "2wDXz5ap24jJcuk1fzBtv705",
    "3XwlZA6td4i9aANsE7QQf3n",
    "2TOBOrffq50la2hDJd6ZotJ",
    "29GcKv5LF4T8b9oeC8qVbD9",
    "24EWHPaEA5gj9WOWqLzSP52"
]

for sim_id in sims:
    resp = session.get(f'{API_BASE}/simulations/{sim_id}')
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nSIM {sim_id}: {data.get('status')} | Alpha: {data.get('alpha')}")
        
        alpha_id = data.get('alpha')
        if alpha_id:
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
    else:
        print(f"Failed to get {sim_id}: {resp.status_code} {resp.text}")
