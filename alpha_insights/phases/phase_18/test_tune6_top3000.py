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

def simulate(expression, universe):
    settings = {
        "instrumentType": "EQUITY", "region": "USA", "universe": universe,
        "delay": 1, "decay": 0, "neutralization": "NONE",
        "truncation": 0.08, "pasteurization": "ON", "unitHandling": "VERIFY",
        "nanHandling": "ON", "language": "FASTEXPR", "visualization": False,
    }
    payload = {"type": "REGULAR", "settings": settings, "regular": expression}
    resp = session.post(f"{API_BASE}/simulations", json=payload)
    if resp.status_code != 201: return None
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    while True:
        data = session.get(f"{API_BASE}/simulations/{sim_id}").json()
        if data.get("status") in ("COMPLETE", "WARNING"): return data.get("alpha")
        if data.get("status") in ("ERROR", "FAILED"): return None
        time.sleep(3)

expr_tune6 = "ts_decay_linear(group_neutralize(ts_delta(anl4_afv4_eps_mean, 60), sector) - group_neutralize(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), sector), 5)"

print(f"\n--- Testing Tune 6 (Neutralize Sector) on TOP3000 ---")
alpha_id = simulate(expr_tune6, "TOP3000")
if alpha_id:
    metrics = session.get(f"{API_BASE}/alphas/{alpha_id}").json().get("is", {})
    print(f"  [TOP3000] Sharpe: {metrics.get('sharpe', 0):.4f}, Fitness: {metrics.get('fitness', 0):.4f}")
