import json
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.post(f"{API_BASE}/authentication")

sim_id = "1wWoK8tC5hraaBqRnY4XN8"
resp = session.get(f'{API_BASE}/simulations/{sim_id}')
data = resp.json()

if 'alpha' in data:
    alpha_id = data['alpha']
    alpha_resp = session.get(f'{API_BASE}/alphas/{alpha_id}')
    is_metrics = alpha_resp.json().get('is', {})
    print(f'Alpha ID: {alpha_id}')
    print(f'Sharpe: {is_metrics.get("sharpe")}')
    print(f'Fitness: {is_metrics.get("fitness")}')
    print(f'Turnover: {is_metrics.get("turnover")}')
else:
    print(f"Status is {data.get('status')}")
