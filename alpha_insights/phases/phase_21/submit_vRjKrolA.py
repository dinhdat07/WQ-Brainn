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

alpha_id = 'vRjKrolA'

while True:
    resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
    if resp.status_code == 200:
        is_metrics = resp.json().get("is", {})
        checks = is_metrics.get("checks", [])
        corr_check = next((c for c in checks if c["name"] == "SELF_CORRELATION"), None)
        
        if corr_check and corr_check["result"] != "PENDING":
            print(f"Self-correlation check: {corr_check['result']}")
            if corr_check["result"] == "PASS":
                # Try to submit
                print("Submitting alpha...")
                submit_resp = session.post(f"{API_BASE}/alphas/{alpha_id}/submit")
                if submit_resp.status_code == 201:
                    print("Successfully submitted!")
                else:
                    print(f"Failed to submit: {submit_resp.status_code}")
                    print(submit_resp.text)
            break
        else:
            print("Still pending...")
            time.sleep(5)
    else:
        print(f"Error getting alpha: {resp.status_code}")
        time.sleep(5)
