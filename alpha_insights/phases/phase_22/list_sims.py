import json, requests
API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.post(f"{API_BASE}/authentication")

resp = session.get(f"{API_BASE}/simulations?limit=15")
if resp.status_code == 200:
    sims = resp.json().get("results", [])
    for sim in sims:
        print(f"\n--- SIM {sim['id']} ---")
        print(f"Expression: {sim.get('regular', '')[:60]}")
        print(f"Status: {sim.get('status')}")
        if 'alpha' in sim:
            alpha_id = sim['alpha']
            alpha_resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
            if alpha_resp.status_code == 200:
                is_metrics = alpha_resp.json().get('is', {})
                print(f"Sharpe: {is_metrics.get('sharpe')}")
                print(f"Fitness: {is_metrics.get('fitness')}")
                for check in is_metrics.get('checks', []):
                    if check.get('name') in ['LOW_SHARPE', 'LOW_SUB_UNIVERSE_SHARPE', 'SELF_CORRELATION']:
                        print(f"Check {check.get('name')}: {check.get('result')} ({check.get('value', '')})")
else:
    print(f"Error: {resp.status_code}")
