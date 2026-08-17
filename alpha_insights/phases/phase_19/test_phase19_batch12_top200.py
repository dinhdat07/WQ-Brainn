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

def simulate(expression, universe="TOP3000"):
    settings = {
        "instrumentType": "EQUITY", "region": "USA", "universe": universe,
        "delay": 1, "decay": 0, "neutralization": "NONE",
        "truncation": 0.08, "pasteurization": "ON", "unitHandling": "VERIFY",
        "nanHandling": "ON", "language": "FASTEXPR", "visualization": False,
    }
    payload = {"type": "REGULAR", "settings": settings, "regular": expression}
    
    try:
        resp = session.post(f"{API_BASE}/simulations", json=payload)
        if resp.status_code != 201:
            print(f"Simulation failed: {resp.text}")
            return None
        sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
        while True:
            resp = session.get(f"{API_BASE}/simulations/{sim_id}")
            if resp.status_code != 200:
                time.sleep(3)
                continue
            data = resp.json()
            if data.get("status") in ("COMPLETE", "WARNING"): return data.get("alpha")
            if data.get("status") in ("ERROR", "FAILED"): 
                print(f"  [ERROR] {data.get('message', 'Unknown API Error')}")
                return None
            time.sleep(3)
    except Exception as e:
        print(f"Exception during simulate: {e}")
        return None

def get_metrics(alpha_id):
    if not alpha_id: return {"sharpe": 0, "fitness": 0, "turnover": 0, "margin": 0}
    try:
        resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
        m = resp.json().get("is", {})
        return {
            "sharpe": m.get("sharpe", 0),
            "fitness": m.get("fitness", 0),
            "turnover": m.get("turnover", 0),
            "margin": m.get("margin", 0)
        }
    except Exception as e:
        print(f"Exception getting metrics: {e}")
        return {"sharpe": 0, "fitness": 0, "turnover": 0, "margin": 0}

formulas = {
    "1. Pure ML Revision": "trade_when(volume > adv20, ts_decay_linear(group_zscore(analyst_revision_rank_derivative, market), 10), -1)",
    "2. Pure Debt Repayment": "trade_when(volume > adv20, ts_decay_linear(group_zscore(fn_repayments_of_debt_a / cap, market), 10), -1)",
    "3. Debt + ML Revision": "trade_when(volume > adv20, ts_decay_linear(group_zscore(analyst_revision_rank_derivative, market) + group_zscore(fn_repayments_of_debt_a / cap, market), 10), -1)",
    "4. Slow Reversion * Debt": "trade_when(volume > adv20, ts_decay_linear(group_zscore(fn_repayments_of_debt_a / cap, market) * -(close - ts_mean(close, 10))/ts_mean(close, 10), 10), -1)"
}

for name, expr in formulas.items():
    print(f"\n--- {name} ---")
    aid = simulate(expr, "TOP3000")
    if not aid:
        print("  -> Simulation failed or errored out.")
        continue
    
    m = get_metrics(aid)
    print(f"  [TOP3000] ID: {aid} | Sharpe: {m['sharpe']:.4f} | Fit: {m['fitness']:.4f} | TO: {m['turnover']:.4f}")
    
    if abs(m['sharpe']) > 0.8:
        print("  Testing Sub-universes...")
        for u in ["TOP1000", "TOP500", "TOP200"]:
            sub_id = simulate(expr, u)
            sub_m = get_metrics(sub_id)
            print(f"    [{u}] Sharpe: {sub_m['sharpe']:.4f}")

