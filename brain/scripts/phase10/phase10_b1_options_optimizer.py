"""
Phase 10: Options Skew Optimizer
Focuses on Options Implied Volatility and Put-Call Ratio datasets to hit SPECTACULAR.
"""

import os
import sys
import time
import requests
import pandas as pd
import numpy as np

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
            "nanHandling": "OFF",
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
        if not sim_progress_url:
            return None
            
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
        print(f"Exception during simulation: {e}")
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
        # Base from B1, change neutralization to SECTOR to fix Sub-universe
        {
            "name": "B1.1 Options Skew SECTOR",
            "expr": "ts_decay_linear(group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)) / ts_backfill(implied_volatility_mean_180, 20), sector), 20)",
            "decay": 0, "trunc": 0.08, "neut": "SECTOR"
        },
        # Base from B1, change neutralization to MARKET
        {
            "name": "B1.2 Options Skew MARKET",
            "expr": "ts_decay_linear(rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)) / ts_backfill(implied_volatility_mean_180, 20)), 20)",
            "decay": 0, "trunc": 0.08, "neut": "MARKET"
        },
        # Introduce Option Spread * Momentum
        {
            "name": "B1.3 Options Skew * Short Term Reversion",
            "expr": "skew = (ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)) / ts_backfill(implied_volatility_mean_180, 20); ts_decay_linear(rank(skew) * rank(-returns), 15)",
            "decay": 0, "trunc": 0.08, "neut": "INDUSTRY"
        },
        # Incorporate Put-Call OI Ratio from Silver Alpha
        {
            "name": "B1.4 PCR Open Interest + IV Spread",
            "expr": "pcr = ts_backfill(pcr_oi_270, 20); spread = ts_backfill(implied_volatility_call_270, 20) - ts_backfill(implied_volatility_put_270, 20); ts_decay_linear(rank(spread) * rank(1 / pcr), 20)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Heavily decayed non-linear Options
        {
            "name": "B1.5 Extreme Decay Options",
            "expr": "ts_decay_linear(group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)) / ts_backfill(implied_volatility_mean_180, 20), subindustry), 40)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        }
    ]

    print("\n================ OPTIONS BATCH ================\n", flush=True)
    results = []
    
    for cand in variations:
        print(f"\n--- Testing: {cand['name']} ---", flush=True)
        aid = run_simulation(session, cand['expr'], decay=cand['decay'], truncation=cand['trunc'], neutralization=cand['neut'])
        if aid:
            perf = check_alpha_performance(session, aid)
            if perf:
                print(f"  Alpha ID: {aid}", flush=True)
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fit: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps | Sub-Univ: {perf['sub_univ_pass']}", flush=True)
                results.append(perf)
        else:
            print("  Simulation failed or timed out.", flush=True)

if __name__ == "__main__":
    main()
