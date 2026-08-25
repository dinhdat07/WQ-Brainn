import json
import requests
import sys

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.post(f"{API_BASE}/authentication")

alpha_id = "MP7lYoLk"
resp = session.post(f"{API_BASE}/alphas/{alpha_id}/submit")

if resp.status_code == 201:
    print(f"SUCCESS: Submitted alpha {alpha_id}")
else:
    print(f"ERROR {resp.status_code}: {resp.text}")
