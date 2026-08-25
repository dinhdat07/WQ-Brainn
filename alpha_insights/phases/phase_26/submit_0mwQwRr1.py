import requests
import json
import time

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.post(f"{API_BASE}/authentication")

TARGET_ALPHA = "0mwQwRr1"

print("Submitting alpha...")
submit_url = f"{API_BASE}/alphas/{TARGET_ALPHA}/submit"
resp = session.post(submit_url)
if resp.status_code == 201:
    print(f"Submission accepted. Waiting for result...")
else:
    print(f"Failed to submit: {resp.status_code}")
    print(resp.text)
    exit(1)

while True:
    time.sleep(10)
    alpha_resp = session.get(f'{API_BASE}/alphas/{TARGET_ALPHA}')
    if alpha_resp.status_code == 200:
        data = alpha_resp.json()
        status = data.get("status")
        if status == "SUBMITTED":
            print("SUCCESS! Alpha was submitted successfully.")
            break
        elif status == "FAIL":
            print("Submission FAILED.")
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
