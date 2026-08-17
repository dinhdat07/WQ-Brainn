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

def test_formula(name, expr):
    print(f"\n--- {name} ---")
    settings = {
        "instrumentType": "EQUITY", "region": "USA", "universe": "TOP3000",
        "delay": 1, "decay": 0, "neutralization": "NONE",
        "truncation": 0.08, "pasteurization": "ON", "unitHandling": "VERIFY",
        "nanHandling": "ON", "language": "FASTEXPR", "visualization": False,
    }
    payload = {"type": "REGULAR", "settings": settings, "regular": expr}
    
    resp = session.post(f"{API_BASE}/simulations", json=payload)
    if resp.status_code != 201:
        print(f"Failed to start simulation: {resp.text}")
        return
        
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    
    while True:
        data = session.get(f"{API_BASE}/simulations/{sim_id}").json()
        if data.get("status") in ("COMPLETE", "WARNING"):
            alpha_id = data.get("alpha")
            break
        if data.get("status") in ("ERROR", "FAILED"):
            print("Simulation failed.")
            return
        time.sleep(3)
        
    alpha_data = session.get(f"{API_BASE}/alphas/{alpha_id}").json()
    m = alpha_data.get("is", {})
    sharpe = m.get("sharpe", 0)
    fit = m.get("fitness", 0)
    to = m.get("turnover", 0)
    print(f"  [TOP3000] ID: {alpha_id} | Sharpe: {sharpe:.4f} | Fit: {fit:.4f} | TO: {to:.4f}")
    
    # Extract True Sub-universe Sharpe from checks
    checks = m.get("checks", [])
    sub_sharpe = None
    for check in checks:
        if check.get("name") == "LOW_SUB_UNIVERSE_SHARPE":
            sub_sharpe = check.get("value")
            break
            
    print(f"  [TRUE SUB-UNIVERSE SHARPE (WQBrain)] : {sub_sharpe}")

formulas = {
    "1. Rank Centered": "trade_when(volume > adv20, ts_decay_linear(rank(analyst_revision_rank_derivative * (ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60))) - 0.5, 10), -1)",
    "2. Group Rank Centered": "trade_when(volume > adv20, ts_decay_linear(group_rank(analyst_revision_rank_derivative * (ts_sum(mean_composite_sentiment_score, 10) - ts_sum(mean_composite_sentiment_score, 60)), market) - 0.5, 10), -1)"
}

if __name__ == '__main__':
    for name, expr in formulas.items():
        test_formula(name, expr)
