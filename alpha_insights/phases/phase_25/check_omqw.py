import json
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.post(f"{API_BASE}/authentication")

sim_id = "omqwENqk"
resp = session.get(f'{API_BASE}/alphas/{sim_id}')
data = resp.json()

is_metrics = data.get('is', {})
print(f'Alpha ID: {sim_id}')
print(f'Sharpe: {is_metrics.get("sharpe")}')
print(f'Fitness: {is_metrics.get("fitness")}')
print(f'Turnover: {is_metrics.get("turnover")}')
