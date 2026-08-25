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

alpha_id = "ALPHA_ID_HERE"

print(f"Submitting alpha {alpha_id}...")
submit_url = f"{API_BASE}/alphas/{alpha_id}/submit"
resp = session.post(submit_url)

if resp.status_code == 201:
    print("Submit initiated.")
elif resp.status_code == 400:
    print(f"Failed to submit. {resp.json()}")
    exit(1)
elif resp.status_code == 403:
    print("Forbidden. (Not owner or simulated over 1 year ago)")
    exit(1)
else:
    print(f"Unknown status: {resp.status_code} {resp.text}")
    exit(1)

time.sleep(2)

while True:
    alpha_resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
    if alpha_resp.status_code == 200:
        data = alpha_resp.json()
        status = data.get("status")
        print(f"Status: {status}")
        
        if status in ["WARNING", "FAIL", "SUCCESS"]:
            print(f"Submit complete. Status: {status}")
            print(f"Details: {data.get('message', 'No message')}")
            
            # Additional detail fetching for self-correlation
            is_metrics = data.get("is", {})
            checks = is_metrics.get("checks", [])
            for c in checks:
                name = c.get("name")
                res = c.get("result")
                val = c.get("value", "")
                if name == "SELF_CORRELATION":
                    print(f"--> SELF_CORRELATION Check: {res} (Correlation = {val})")
                elif res == "FAIL":
                    print(f"--> {name} Check: {res} (Value = {val})")
            
            break
        elif status == "ERROR":
            print(f"Submit ERROR: {data.get('message', 'No message')}")
            break
        time.sleep(10)
    else:
        print("Failed to get alpha status.")
        break
