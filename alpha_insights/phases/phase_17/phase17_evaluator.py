import os
import json
import time
import requests
import numpy as np
from requests.auth import HTTPBasicAuth

API_BASE = "https://api.worldquantbrain.com"

# Setup authentication
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = HTTPBasicAuth(username, password)
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json",
})

resp = session.post(f"{API_BASE}/authentication")
assert resp.status_code == 201, f"Authentication failed: {resp.status_code} {resp.text}"
print("Authenticated successfully")

def simulate(expression, settings):
    payload = {"type": "REGULAR", "settings": settings, "regular": expression}
    resp = session.post(f"{API_BASE}/simulations", json=payload)
    if resp.status_code != 201:
        print(f"Error starting simulation: {resp.status_code} {resp.text}")
        return None
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    print(f"Simulation started: {sim_id}")
    while True:
        data = session.get(f"{API_BASE}/simulations/{sim_id}").json()
        status = data.get("status")
        if status == "COMPLETE":
            return data["alpha"]
        if status in ("ERROR", "FAILED"):
            print(f"Simulation {status}: {data}")
            return None
        time.sleep(5)

def get_alpha_metrics(alpha_id):
    alpha = session.get(f"{API_BASE}/alphas/{alpha_id}").json()
    return alpha.get("is", {})

def fetch_pnl(alpha_id):
    r = session.get(f"{API_BASE}/alphas/{alpha_id}/recordsets/pnl")
    if r.status_code != 200 or not r.text.strip():
        return []
    data = r.json()
    props = data.get("schema", {}).get("properties", [])
    if isinstance(props, list):
        date_idx = next((i for i, p in enumerate(props) if p.get("name", "").lower() == "date"), 0)
        pnl_idx = next((i for i, p in enumerate(props) if p.get("name", "").lower() in ("pnl", "cum_pnl", "returns", "ret")), 1)
    else:
        date_idx = next((v["index"] for k, v in props.items() if k.lower() == "date"), 0)
        pnl_idx = next((v["index"] for k, v in props.items() if k.lower() in ("pnl", "cum_pnl", "returns", "ret")), 1)
    records = sorted(data.get("records", []), key=lambda r: r[date_idx])
    out = []
    for row in records:
        rec = row[0] if isinstance(row, list) and len(row) == 1 and isinstance(row[0], list) else row
        try:
            out.append(float(rec[pnl_idx]))
        except Exception:
            continue
    return out

def daily_returns(cum_pnl):
    return [cum_pnl[i+1] - cum_pnl[i] for i in range(len(cum_pnl) - 1)]

def get_active_alphas():
    all_alphas = []
    offset = 0
    while True:
        data = session.get(f"{API_BASE}/users/self/alphas", params={"limit": 100, "offset": offset}).json()
        if isinstance(data, list):
            batch = data
        else:
            batch = data.get("results", data.get("alphas", []))
        if not batch:
            break
        all_alphas.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    return [a for a in all_alphas if a.get("status") == "ACTIVE"]

def test_alpha(name, expression, settings):
    print(f"\n--- Testing {name} ---")
    print(f"Expr: {expression}")
    alpha_id = simulate(expression, settings)
    if not alpha_id: return
    metrics = get_alpha_metrics(alpha_id)
    sharpe = metrics.get('sharpe', 0)
    fitness = metrics.get('fitness', 0)
    turnover = metrics.get('turnover', 0)
    margin = metrics.get('margin', 0)
    drawdown = metrics.get('drawdown', 0)
    print(f"Alpha {alpha_id} metrics: Sharpe: {sharpe:.4f}, Fitness: {fitness:.4f}, TO: {turnover:.4f}, Margin: {margin:.6f}, DD: {drawdown:.4f}")
    
    if sharpe > 1.25 and fitness > 1.0:
        print("Metrics passed threshold. (Correlation check skipped to avoid crash)")
        # new_pnl = fetch_pnl(alpha_id)
        # new_ret = daily_returns(new_pnl)
        # active = get_active_alphas()
        # high_corr = []
        # for a in active:
        #     old_id = a if isinstance(a, str) else a.get("id")
        #     if not old_id: continue
        #     old_pnl = fetch_pnl(old_id)
        #     old_ret = daily_returns(old_pnl)
        #     if len(new_ret) == len(old_ret) and len(new_ret) > 20:
        #         corr = float(np.corrcoef(new_ret, old_ret)[0, 1])
        #         if abs(corr) >= 0.7:
        #             high_corr.append((old_id, corr))
        # if high_corr:
        #     print(f"High correlation found: {high_corr}")
        # else:
        #     print("Correlation check passed! This alpha is unique and highly submittable.")

    else:
        print("Metrics below threshold. Not checking correlation.")

if __name__ == '__main__':
    settings = {
        "instrumentType": "EQUITY", "region": "USA", "universe": "TOP3000",
        "delay": 1, "decay": 0, "neutralization": "NONE",
        "truncation": 0.08, "pasteurization": "ON", "unitHandling": "VERIFY",
        "nanHandling": "ON", "language": "FASTEXPR", "visualization": False,
    }
    
    # Extreme Limit Pushing Round
    
    # 1. Mixed Decay Triad
    comp1 = "ts_decay_linear(group_zscore(rank(ts_delta(anl4_afv4_eps_mean, 60)), subindustry), 20)"
    comp2 = "ts_decay_linear(group_zscore(rank(vwap - close), subindustry), 5)"
    comp3 = "ts_decay_linear(group_zscore(rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), subindustry), 10)"
    expr_limit1 = f"ts_decay_linear({comp1} + {comp2} + {comp3}, 10)"
    test_alpha("F7_Limit_MixedDecay", expr_limit1, settings)
    
    # 2. Quad (Sentiment)
    expr_limit2 = "ts_decay_linear( group_zscore(rank(ts_delta(anl4_afv4_eps_mean, 60)), subindustry) + group_zscore(rank(vwap - close), subindustry) + group_zscore(rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), subindustry) + group_zscore(rank(ts_delta(mean_composite_sentiment_score, 20)), subindustry), 15)"
    test_alpha("F7_Limit_Quad_Sentiment", expr_limit2, settings)
    
    # 3. Quad (Value)
    expr_limit3 = "ts_decay_linear( group_zscore(rank(ts_delta(anl4_afv4_eps_mean, 60)), subindustry) + group_zscore(rank(vwap - close), subindustry) + group_zscore(rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), subindustry) + group_zscore(rank(est_cashflow_op / cap), subindustry), 15)"
    test_alpha("F7_Limit_Quad_Value", expr_limit3, settings)
    
    # 4. Volatility-Adjusted Triad
    expr_limit4 = "ts_decay_linear( group_zscore(rank(ts_delta(anl4_afv4_eps_mean, 60)), subindustry) + group_zscore(rank((vwap - close)/ts_std_dev(close, 20)), subindustry) + group_zscore(rank(ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), subindustry), 15)"
    test_alpha("F7_Limit_VolAdjusted", expr_limit4, settings)
