"""
Phase 10: Sparse Triggers
Goal: Use trade_when to create sparse signals that use sales/assets and options but have low correlation to dense models like 88pomANl.
"""

import os
import sys
import time
import requests

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def run_simulation(session, expr, decay=20, truncation=0.08, neutralization="SUBINDUSTRY"):
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
    
    try:
        resp = session.post("https://api.worldquantbrain.com/simulations", json=payload, timeout=20)
        if resp.status_code not in (200, 201):
            return None
        sim_progress_url = resp.headers.get("Location")
        for _ in range(60):
            time.sleep(5)
            stat = session.get(sim_progress_url, timeout=20)
            if stat.status_code == 200:
                sdata = stat.json()
                if sdata.get("status") == "COMPLETE":
                    return sdata.get("alpha")
                elif sdata.get("status") == "ERROR":
                    return None
    except Exception:
        pass
    return None

def check_alpha_performance(session, alpha_id):
    try:
        resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}", timeout=20)
        if resp.status_code != 200:
            return None
        data = resp.json()
        is_data = data.get("is", {})
        checks = is_data.get("checks", [])
        
        sharpe = is_data.get("sharpe", 0.0)
        fitness = is_data.get("fitness", 0.0)
        turnover = is_data.get("turnover", 0.0)
        margin = is_data.get("margin", 0.0)
        
        sub_univ_check = next((c for c in checks if c.get("name") == "LOW_SUB_UNIVERSE_SHARPE"), None)
        sub_univ_pass = (sub_univ_check.get("result") == "PASS") if sub_univ_check else True
        
        return {
            "id": alpha_id,
            "sharpe": sharpe,
            "fitness": fitness,
            "turnover": turnover,
            "margin": margin,
            "sub_univ_pass": sub_univ_pass
        }
    except:
        return None

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    if not session:
        return
        
    variations = [
        # Sparse 1: Filter Option Skew by Sales/Assets (Only trade top decile of Sales/Assets)
        {
            "name": "Sparse Top Decile Sales -> Opt Skew",
            "expr": "ts_decay_linear(trade_when(group_rank(sales/assets, subindustry) > 0.9, group_rank(implied_volatility_call_270 - implied_volatility_put_270, subindustry), -1), 20)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Sparse 2: Filter Option Skew by Sales/Assets and Intraday
        {
            "name": "Sparse Sales & Intraday -> Opt Skew",
            "expr": "ts_decay_linear(trade_when(group_rank(sales/assets, subindustry) + group_rank(-(close-open)/open, subindustry) > 1.8, group_rank(implied_volatility_call_270 - implied_volatility_put_270, subindustry), -1), 20)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Sparse 3: The nested trade_when
        {
            "name": "Sparse Nested",
            "expr": "ts_decay_linear(trade_when(pcr_oi_270 < 1, trade_when(group_rank(sales/assets, subindustry) > 0.8, -(close-open)/open, -1), -1), 20)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        }
    ]

    print("\n================ SPARSE TRIGGERS BATCH ================\n", flush=True)
    for cand in variations:
        print(f"\n--- Testing: {cand['name']} ---", flush=True)
        aid = run_simulation(session, cand['expr'], decay=cand['decay'], truncation=cand['trunc'], neutralization=cand['neut'])
        if aid:
            perf = check_alpha_performance(session, aid)
            if perf:
                print(f"  Alpha ID: {aid}", flush=True)
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fit: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps | Sub-Univ: {perf['sub_univ_pass']}", flush=True)

if __name__ == "__main__":
    main()
