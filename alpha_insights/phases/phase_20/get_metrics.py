import requests
import time, json

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.headers.update({"Content-Type": "application/json"})
session.post(f"{API_BASE}/authentication")

sim_ids = ['3luh41eJ24u29l1OCCzX8iB', '2Fv2u624B4ANbnW1ggyyb0S9', '3TLbSh4S50CcIy9dgjZqBi', '7cUY82kq5dScjp1eEPSyjbi']
pending_alphas = sim_ids.copy()

while pending_alphas:
    print("\n--- Checking Pending Alphas ---")
    still_pending = []
    for sim_id in pending_alphas:
        try:
            sim_resp = session.get(f"{API_BASE}/simulations/{sim_id}").json()
            alpha_id = sim_resp.get("alpha")
            if not alpha_id:
                print(f"Alpha ID not found for sim {sim_id}")
                continue
                
            resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
            is_metrics = resp.json().get("is", {})
            checks = is_metrics.get("checks", [])
            
            self_corr_status = "PENDING"
            self_corr_value = None
            for check in checks:
                if check.get("name") == "SELF_CORRELATION":
                    self_corr_status = check.get("result")
                    self_corr_value = check.get("value")
                    break
            
            if self_corr_status == "PENDING":
                print(f"Alpha {alpha_id} (Sim {sim_id}) is still PENDING self-correlation. Value: {self_corr_value}")
                still_pending.append(sim_id)
            else:
                print(f"Alpha {alpha_id} (Sim {sim_id}) completed! SELF_CORRELATION: {self_corr_status} ({self_corr_value})")
                print(f"Sharpe: {is_metrics.get('sharpe')}, Fitness: {is_metrics.get('fitness')}, Turnover: {is_metrics.get('turnover')}")
                print("All Checks:")
                for check in checks:
                    print(f"  {check.get('name')}: {check.get('result')} ({check.get('value')})")
        except Exception as e:
            print(f"Error checking {sim_id}: {e}")
            still_pending.append(sim_id)
            
    pending_alphas = still_pending
    if pending_alphas:
        print("Waiting 10 seconds before next check...")
        time.sleep(10)
