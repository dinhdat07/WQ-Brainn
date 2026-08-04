"""
Phase 10: Analyst Revisions + IV Skew Optimizer
Targeting Sharpe > 2.5, Fit > 2.8, Margin > 40 bps.
"""

import os
import sys
import time
import requests
import pandas as pd

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def run_simulation(session, expr, decay=10, truncation=0.08, neutralization="SUBINDUSTRY"):
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
                status = sdata.get("status")
                if status == "COMPLETE":
                    return sdata.get("alpha")
                elif status == "ERROR":
                    return None
    except Exception as e:
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
        returns = is_data.get("returns", 0.0)
        
        sub_univ_check = next((c for c in checks if c.get("name") == "LOW_SUB_UNIVERSE_SHARPE"), None)
        sub_univ_pass = (sub_univ_check.get("result") == "PASS") if sub_univ_check else True
        
        return {
            "id": alpha_id,
            "sharpe": sharpe,
            "fitness": fitness,
            "turnover": turnover,
            "margin": margin,
            "returns": returns,
            "sub_univ_pass": sub_univ_pass
        }
    except:
        return None

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    if not session:
        return
        
    variations = [
        # Model 1: Revisions + IV Skew + Reversion
        {
            "name": "M1: Revisions + IV Skew",
            "expr": "ts_decay_linear(group_rank(revisions_est_eps_up_1m / revisions_est_eps_dn_1m, subindustry) + group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)), subindustry) + group_rank(-(close - open) / open, subindustry), 15)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Model 2: Target Price + IV Skew + Reversion
        {
            "name": "M2: Target Price + IV Skew",
            "expr": "ts_decay_linear(group_rank(est_ptp / close, subindustry) + group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)), subindustry) + group_rank(-(close - open) / open, subindustry), 15)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Model 3: Quad Factor (Sales + PTP + IV Skew + Reversion)
        {
            "name": "M3: Quad Target PTP",
            "expr": "ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(est_ptp / close, subindustry) + group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)), subindustry) + group_rank(-(close - open) / open, subindustry), 18)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        }
    ]

    print("\n================ NEW TRIAD/QUAD BATCH ================\n", flush=True)
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
