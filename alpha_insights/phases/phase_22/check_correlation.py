import json, requests, time

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

alpha_id = "LL7WnpYe"

while True:
    resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
    if resp.status_code == 200:
        data = resp.json()
        is_metrics = data.get("is", {})
        print(f"Alpha {alpha_id}")
        print(f"Sharpe: {is_metrics.get('sharpe')}")
        print(f"Fitness: {is_metrics.get('fitness')}")
        print(f"Turnover: {is_metrics.get('turnover')}")
        
        checks = is_metrics.get("checks", [])
        pending = False
        for c in checks:
            name = c.get("name")
            res = c.get("result")
            val = c.get("value", "")
            print(f"Check {name}: {res} ({val})")
            if res == "PENDING":
                pending = True
                
        if not pending:
            print("All checks completed!")
            break
    else:
        print(f"Error {resp.status_code}")
        
    time.sleep(10)
