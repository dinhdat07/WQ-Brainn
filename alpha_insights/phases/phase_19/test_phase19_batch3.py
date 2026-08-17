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
    resp = session.post(f"{API_BASE}/simulations", json=payload)
    if resp.status_code != 201:
        print(f"Simulation failed: {resp.text}")
        return None
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    while True:
        data = session.get(f"{API_BASE}/simulations/{sim_id}").json()
        if data.get("status") in ("COMPLETE", "WARNING"): return data.get("alpha")
        if data.get("status") in ("ERROR", "FAILED"): return None
        time.sleep(3)

def get_metrics(alpha_id):
    if not alpha_id: return {"sharpe": 0, "fitness": 0, "turnover": 0, "margin": 0}
    m = session.get(f"{API_BASE}/alphas/{alpha_id}").json().get("is", {})
    return {
        "sharpe": m.get("sharpe", 0),
        "fitness": m.get("fitness", 0),
        "turnover": m.get("turnover", 0),
        "margin": m.get("margin", 0)
    }

def check_correlation(alpha_id):
    old_alphas = ["omNXOQp2", "zqNEzQGd", "RRm3ZdRg", "E5GNlbrG", "LLGr09GL"]
    max_corr = 0
    for old_id in old_alphas:
        url = f"{API_BASE}/alphas/{alpha_id}/correlations/{old_id}"
        resp = session.get(url)
        if resp.status_code == 200:
            corr = resp.json().get("value", 0)
            max_corr = max(max_corr, corr)
    return max_corr

formulas = {
    "1. Option PCR vs Volatility": "trade_when(volume > adv20, ts_decay_linear(group_zscore(pcr_oi_all, subindustry) - group_zscore(parkinson_volatility_30, subindustry), 10), -1)",
    "2. Sales Estimate Delta": "trade_when(volume > adv20, ts_decay_linear(group_zscore(ts_delta(sales_estimate_value, 5), subindustry) * group_zscore(-(close-open)/open, subindustry), 10), -1)",
    "3. Supply Chain Customers Hub": "trade_when(volume > adv20, ts_decay_linear(group_zscore(pv13_ustomergraphrank_hub_rank, sector), 10), -1)",
    "4. Supply Chain Competitors Hub": "trade_when(volume > adv20, ts_decay_linear(group_zscore(pv13_ompetitorgraphrank_hub_rank, sector), 10), -1)",
    "5. ML Revision Only": "trade_when(volume > adv20, ts_decay_linear(group_neutralize(analyst_revision_rank_derivative, subindustry), 5), -1)"
}

for name, expr in formulas.items():
    print(f"\n--- {name} ---")
    aid = simulate(expr, "TOP3000")
    if not aid:
        print("  -> Simulation failed or errored out.")
        continue
    
    m = get_metrics(aid)
    print(f"  [TOP3000] ID: {aid} | Sharpe: {m['sharpe']:.4f} | Fit: {m['fitness']:.4f} | TO: {m['turnover']:.4f}")
    
    if m['sharpe'] > 1.5:
        corr = check_correlation(aid)
        print(f"  -> Max Correlation with past alphas: {corr:.4f}")
        
        print("  Testing Sub-universes...")
        for u in ["TOP1000", "TOP500", "TOP200"]:
            sub_id = simulate(expr, u)
            sub_m = get_metrics(sub_id)
            print(f"    [{u}] Sharpe: {sub_m['sharpe']:.4f}")

