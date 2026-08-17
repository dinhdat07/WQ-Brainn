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

def get_metrics(alpha_id):
    if not alpha_id: return {"sharpe": 0, "fitness": 0}
    return session.get(f"{API_BASE}/alphas/{alpha_id}").json().get("is", {})

variants = {
    "Rank (Flat)": "ts_decay_linear(rank(ts_delta(anl4_afv4_eps_mean, 60)) - rank(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60)), 5)",
    "Group Rank (Sector)": "ts_decay_linear(group_rank(ts_delta(anl4_afv4_eps_mean, 60), sector) - group_rank(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), sector), 5)",
    "Group Rank (Subindustry)": "ts_decay_linear(group_rank(ts_delta(anl4_afv4_eps_mean, 60), subindustry) - group_rank(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), subindustry), 5)",
    "Rank + Liquidity": "trade_when(volume > ts_mean(volume, 20), ts_decay_linear(rank(ts_delta(anl4_afv4_eps_mean, 60)) - rank(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60)), 5), -1)"
}

universes = ["TOP3000", "TOP1000", "TOP200"]

for name, expr in variants.items():
    print(f"\n--- {name} ---")
    for u in universes:
        aid = simulate(expr, u)
        m = get_metrics(aid)
        print(f"  [{u}] Sharpe: {m.get('sharpe', 0):.4f}, Fitness: {m.get('fitness', 0):.4f}")
        if aid and u == "TOP3000":
            print(f"  -> ID: {aid}")
