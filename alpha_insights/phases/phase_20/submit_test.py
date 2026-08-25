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

alpha_id = "1Ywqp3nK"
print(f"Attempting to submit {alpha_id}...")
resp = session.post(f"{API_BASE}/alphas/{alpha_id}/submit")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
