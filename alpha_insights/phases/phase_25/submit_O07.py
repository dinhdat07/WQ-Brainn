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

ALPHA_ID = "O07wR2Qq"
submit_url = f"{API_BASE}/alphas/{ALPHA_ID}/submit"
print(f"Submitting alpha {ALPHA_ID}...")

resp = session.post(submit_url)
if resp.status_code == 201:
    print(f"Submission accepted. Waiting for result...")
elif resp.status_code == 403:
    print("403 Forbidden. Check if alpha is eligible for submission.")
    print(resp.text)
    exit(1)
elif resp.status_code == 400:
    print("400 Bad Request.")
    print(resp.text)
    exit(1)
else:
    print(f"Failed to submit: {resp.status_code}")
    print(resp.text)
    exit(1)

while True:
    time.sleep(10)
    alpha_resp = session.get(f'{API_BASE}/alphas/{ALPHA_ID}')
    if alpha_resp.status_code == 200:
        data = alpha_resp.json()
        status = data.get("status")
        if status == "SUBMITTED":
            print("SUCCESS! Alpha was submitted successfully.")
            break
        elif status == "FAIL":
            print("Submission FAILED.")
            # Print failure reasons
            checks = data.get("is", {}).get("checks", [])
            for c in checks:
                if c.get("result") == "FAIL":
                    print(f"Failed on: {c.get('name')} (value: {c.get('value')})")
            break
        elif status == "WARNING":
            print("Submission got WARNING but might be submitted.")
            break
        else:
            print(f"Current status: {status}")
    else:
        print("Waiting...")
