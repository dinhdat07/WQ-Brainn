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

sim_ids = ["1RJIpS5zX4L29b63epTBNK9", "NsZUC5gy58Oa5Z12wMJwy6z", "20TJDXe684sRakjSZ6nMnPi", "1gkDpecw44zMb5r1foW6huCx"]
for sid in sim_ids:
    resp = session.get(f"{API_BASE}/simulations/{sid}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"ID {sid}: status {data.get('status')}")
        if data.get("status") == "ERROR":
            for warning in data.get("warnings", []):
                print(f"Warning: {warning}")
            for error in data.get("errors", []):
                print(f"Error: {error}")
    else:
        print(f"ID {sid}: Error {resp.status_code}")
