import requests, json

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.headers.update({"Content-Type": "application/json"})
session.post(f"{API_BASE}/authentication")

resp = session.get(f"{API_BASE}/simulations?limit=5")
for sim in resp.json().get('results', []):
    print(f"ID: {sim['id']}, Status: {sim['status']}")
    if sim['status'] == "DONE":
        print(f"  Expression: {sim['regular']}")
        alpha_resp = session.get(f"{API_BASE}/alphas/{sim['alpha']}")
        if alpha_resp.status_code == 200:
            is_metrics = alpha_resp.json().get("is", {})
            print(f"  Sharpe: {is_metrics.get('sharpe')}")
        else:
            print(f"  Error getting alpha: {alpha_resp.status_code}")
    elif sim['status'] == "ERROR":
        print(f"  Message: {sim.get('message')}")
        print(f"  Expression: {sim['regular']}")
