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
    if resp.status_code != 201:
        return None
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    while True:
        data = session.get(f"{API_BASE}/simulations/{sim_id}").json()
        if data.get("status") in ("COMPLETE", "WARNING"): return data.get("alpha")
        if data.get("status") in ("ERROR", "FAILED"): return None
        time.sleep(3)

def test_expr(name, expr):
    print(f"\n--- Testing {name} ---")
    for universe in ["TOP500", "TOP200"]:
        print(f"  Testing on {universe}...")
        alpha_id = simulate(expr, universe)
        if alpha_id:
            metrics = session.get(f"{API_BASE}/alphas/{alpha_id}").json().get("is", {})
            print(f"  [{universe}] Sharpe: {metrics.get('sharpe', 0):.4f}, Fitness: {metrics.get('fitness', 0):.4f}")

expr_tune2 = "ts_decay_linear(group_zscore(ts_delta(anl4_afv4_eps_mean, 60), sector) - group_zscore(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), sector), 5)"
expr_tune4 = "trade_when(volume > ts_mean(volume, 20), ts_decay_linear(group_zscore(ts_delta(anl4_afv4_eps_mean, 60), market) - group_zscore(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), market), 5), -1)"
expr_tune6 = "ts_decay_linear(group_neutralize(ts_delta(anl4_afv4_eps_mean, 60), sector) - group_neutralize(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), sector), 5)"
expr_tune7 = "ts_decay_linear(group_neutralize(ts_delta(anl4_afv4_eps_mean, 60), subindustry) - group_neutralize(ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60), subindustry), 5)"

test_expr("Tune 2 (Sector)", expr_tune2)
test_expr("Tune 4 (Market + Liq Filter)", expr_tune4)
test_expr("Tune 6 (Neutralize Sector)", expr_tune6)
test_expr("Tune 7 (Neutralize Subindustry)", expr_tune7)
