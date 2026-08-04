import os
import sys
import time
import json
import pandas as pd
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

SUBMITTED_ALPHAS = [
    "88pomANl", "6Xpn9V2L", "Jjv1g3xO", "d5RaEvVj", 
    "bldOZEjr", "RR1bxvea", "e7x3P7gO", "le3WZmdl", "ZYKo6R78"
]

def fetch_pnl_series(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    for _ in range(3):
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200:
                records = resp.json().get("records", [])
                if records:
                    df = pd.DataFrame(records, columns=["date", "pnl"])
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.sort_values("date").set_index("date")
                    return df["pnl"]
        except Exception:
            pass
        time.sleep(1)
    return None

def run_simulation(session, expr, decay=10, neutralization="SUBINDUSTRY", truncation=0.05):
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": decay,
            "neutralization": neutralization,
            "truncation": truncation,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": expr
    }
    
    resp = session.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code not in (200, 201):
        print(f"Sim error {resp.status_code}: {resp.text[:120]}")
        return None
        
    sim_progress_url = resp.headers.get("Location")
    if not sim_progress_url:
        return None
        
    for _ in range(40):
        time.sleep(4)
        stat = session.get(sim_progress_url)
        if stat.status_code == 200:
            sdata = stat.json()
            status = sdata.get("status")
            if status == "COMPLETE":
                return sdata.get("alpha")
            elif status == "ERROR":
                print(f"Sim failed: {sdata.get('message')}")
                return None
    return None

def check_alpha_performance(session, alpha_id):
    resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
    if resp.status_code != 200:
        return None
    data = resp.json()
    is_data = data.get("is", {})
    checks = is_data.get("checks", [])
    
    sharpe = is_data.get("sharpe", 0.0)
    fitness = is_data.get("fitness", 0.0)
    turnover = is_data.get("turnover", 0.0)
    margin = is_data.get("margin", 0.0)
    returns = is_data.get("returns", 0.0)
    drawdown = is_data.get("drawdown", 0.0)
    
    sub_univ_check = next((c for c in checks if c.get("name") == "LOW_SUB_UNIVERSE_SHARPE"), None)
    sub_univ_pass = (sub_univ_check.get("result") == "PASS") if sub_univ_check else True
    sub_univ_val = sub_univ_check.get("value", 0) if sub_univ_check else 0
    sub_univ_lim = sub_univ_check.get("limit", 0) if sub_univ_check else 0
    
    return {
        "alpha_id": alpha_id,
        "sharpe": sharpe,
        "fitness": fitness,
        "turnover": turnover,
        "margin": margin,
        "returns": returns,
        "drawdown": drawdown,
        "sub_univ_pass": sub_univ_pass,
        "sub_univ_val": sub_univ_val,
        "sub_univ_lim": sub_univ_lim,
        "checks": checks
    }

def evaluate_correlation(session, candidate_id, submitted_pnl_cache):
    cand_pnl = fetch_pnl_series(session, candidate_id)
    if cand_pnl is None:
        return 1.0, "FETCH_ERROR"
        
    max_ret_corr = -1.0
    max_sub_id = ""
    
    cand_ret = cand_pnl.diff().dropna()
    for sub_id, sub_pnl in submitted_pnl_cache.items():
        if sub_pnl is not None:
            sub_ret = sub_pnl.diff().dropna()
            merged = pd.concat([cand_ret, sub_ret], axis=1, join='inner').dropna()
            if len(merged) > 30:
                rc = merged.iloc[:, 0].corr(merged.iloc[:, 1])
                if rc > max_ret_corr:
                    max_ret_corr = rc
                    max_sub_id = sub_id
                    
    return max_ret_corr, max_sub_id

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    if not session:
        print("Auth failed")
        return
        
    print("Pre-loading PnL for 9 submitted alphas...")
    submitted_pnl_cache = {}
    for sub_id in SUBMITTED_ALPHAS:
        s = fetch_pnl_series(session, sub_id)
        if s is not None:
            submitted_pnl_cache[sub_id] = s
            print(f"  Loaded {sub_id} ({len(s)} days)")
            
    print(f"\nLoaded {len(submitted_pnl_cache)}/{len(SUBMITTED_ALPHAS)} submitted alphas into cache.")

    candidates = [
        # 1. Forward Consensus EBIT Yield + Consensus Drift + FCF Quality
        {
            "name": "Pillar 1A: Consensus EBIT Yield + Consensus Revision Drift",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(free_cash_flow_reported_value / cap, subindustry), 12)",
            "decay": 12
        },
        {
            "name": "Pillar 1B: Consensus EBIT Drift + Inventory Turnover Efficiency",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(inventory_turnover, subindustry), 15)",
            "decay": 15
        },
        # 2. Operating Income Yield + Working Capital + Short Term Reversal Overlay
        {
            "name": "Pillar 2A: Operating Profitability + Working Capital + 5d Reversion",
            "expr": "ts_decay_linear(group_rank(operating_income / cap, subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 5) / close, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Pillar 2B: Forward EBIT Yield + Working Capital + Volume-Weighted Reversal",
            "expr": "ts_decay_linear(group_rank(anl4_ebit_mean / cap, subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_rank(volume, 10) * ts_delta(close, 3) / close, subindustry), 10)",
            "decay": 10
        },
        # 3. Alpha 101 #41 (Geometric High-Low VWAP) + Forward Consensus EBIT
        {
            "name": "Pillar 3A: Alpha 101 #41 + Forward EBIT Yield",
            "expr": "ts_decay_linear(group_rank(power(high * low, 0.5) - vwap, subindustry) + 1.5 * group_rank(est_ebit / cap, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Pillar 3B: Alpha 101 #41 + Consensus EBIT Revision Drift",
            "expr": "ts_decay_linear(group_rank(power(high * low, 0.5) - vwap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(est_ebit / cap, subindustry), 10)",
            "decay": 10
        },
        # 4. Alpha 101 #54 (Non-linear Intraday Price Distribution) + Free Cash Flow Yield
        {
            "name": "Pillar 4A: Alpha 101 #54 + Free Cash Flow Yield",
            "expr": "ts_decay_linear(group_rank(- (low - close) * power(open, 2) / ((low - high - 0.001) * power(close, 2)), subindustry) + 1.5 * group_rank(free_cash_flow_reported_value / cap, subindustry), 8)",
            "decay": 8
        },
        # 5. Triple Orthogonal Zenith: Forward EBIT Yield + Consensus Upgrade + Working Capital + Vol Reversal
        {
            "name": "Pillar 5A: Quad Orthogonal Institutional (EBIT Yield + Drift + Working Cap + Reversion)",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.4 * group_rank(-ts_delta(close, 5) / close, subindustry), 12)",
            "decay": 12
        },
        {
            "name": "Pillar 5B: Quad Orthogonal Sector-Neutral (EBIT Yield + Drift + Inventory + Alpha 41)",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(inventory_turnover, subindustry) + 0.5 * group_rank(power(high * low, 0.5) - vwap, subindustry), 12)",
            "decay": 12
        }
    ]

    print("\n================ STARTING ORTHOGONAL SPECTACULAR OPTIMIZATION ================\n")
    results = []
    
    for cand in candidates:
        print(f"\n--- Testing: {cand['name']} ---")
        print(f"Expr: {cand['expr']}")
        aid = run_simulation(session, cand['expr'], decay=cand['decay'])
        if aid:
            perf = check_alpha_performance(session, aid)
            if perf:
                max_corr, worst_sub = evaluate_correlation(session, aid, submitted_pnl_cache)
                perf["max_corr"] = max_corr
                perf["worst_sub"] = worst_sub
                perf["name"] = cand["name"]
                perf["expr"] = cand["expr"]
                perf["decay"] = cand["decay"]
                
                print(f"  Alpha ID: {aid}")
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fitness: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps")
                print(f"  Sub-Univ Sharpe: {perf['sub_univ_val']:.2f} (Limit: {perf['sub_univ_lim']:.2f}) -> {'PASS' if perf['sub_univ_pass'] else 'FAIL'}")
                print(f"  Max Daily Ret Corr vs Portfolio: {max_corr:.4f} (vs {worst_sub}) -> {'PASS (<0.7)' if max_corr < 0.7 else 'FAIL (>=0.7)'}")
                
                results.append(perf)
        time.sleep(2)
        
    print("\n================ SUMMARY OF ALL ORTHOGONAL CANDIDATES ================\n")
    for r in results:
        status = "SPECTACULAR CANDIDATE" if (r['sharpe'] >= 1.5 and r['sub_univ_pass'] and r['max_corr'] < 0.70) else "NEEDS_TUNING"
        print(f"[{status}] ID: {r['alpha_id']} | Sharpe: {r['sharpe']:.2f} | Fit: {r['fitness']:.2f} | TO: {r['turnover']*100:.1f}% | Margin: {r['margin']*10000:.1f} bps | Sub-Univ: {'PASS' if r['sub_univ_pass'] else 'FAIL'} | MaxCorr: {r['max_corr']:.4f} ({r['worst_sub']})")

if __name__ == "__main__":
    main()
