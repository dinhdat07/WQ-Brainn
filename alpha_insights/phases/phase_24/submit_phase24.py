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

expression = "ts_decay_linear(group_rank(fn_repayments_of_debt_a / cap, subindustry) + group_rank(-scl12_buzz, subindustry) + group_rank(implied_volatility_call_60 - historical_volatility_60, subindustry) + group_rank(-ts_delta(close, 5), subindustry), 10)"

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

print("Simulating final Phase 24 Alpha...")
response = session.post(f"{API_BASE}/simulations", json=data)
sim_id = response.headers.get("Location").split("/")[-1]
print(f"Simulation ID: {sim_id}")

while True:
    resp = session.get(f'{API_BASE}/simulations/{sim_id}')
    if resp.status_code == 200:
        sim_data = resp.json()
        status = sim_data.get("status")
        if status == "COMPLETE":
            alpha_id = sim_data.get("alpha")
            print(f"Alpha ID: {alpha_id}")
            break
        elif status == "ERROR":
            print("Error in simulation")
            exit(1)
    time.sleep(5)

print(f"Testing correlation for Alpha {alpha_id}...")
while True:
    alpha_resp = session.get(f'{API_BASE}/alphas/{alpha_id}')
    if alpha_resp.status_code == 200:
        alpha_data = alpha_resp.json()
        if alpha_data.get('is'):
            is_metrics = alpha_data['is']
            for check in is_metrics.get('checks', []):
                if check.get('name') == 'SELF_CORRELATION':
                    result = check.get('result')
                    print(f"Correlation: {result} ({check.get('value')})")
                    if result == 'PASS':
                        print("Correlation passed! Submitting...")
                        sub_resp = session.post(f"{API_BASE}/alphas/{alpha_id}/submit")
                        if sub_resp.status_code == 201:
                            print("SUBMISSION SUCCESSFUL!")
                        else:
                            print(f"Submission failed: {sub_resp.status_code} {sub_resp.text}")
                        exit(0)
                    elif result == 'FAIL':
                        print("Correlation failed. Cannot submit.")
                        exit(1)
    time.sleep(5)
