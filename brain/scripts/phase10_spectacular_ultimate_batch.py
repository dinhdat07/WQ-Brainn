"""
Phase 10: Spectacular Ultimate Batch (Non-linear & Alternative Data)
Hunts for Sharpe > 2.5, Fitness > 2.8, Margin > 40bps.
Tests 5 completely disparate, non-correlated fundamental and microstructure branches.
"""

import os
import sys
import json
import time
import requests
import pandas as pd
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

SUBMITTED_ALPHAS = [
    "88pomANl", "6Xpn9V2L", "Jjv1g3xO", "d5RaEvVj", 
    "bldOZEjr", "RR1bxvea", "e7x3P7gO", "le3WZmdl", "ZYKo6R78"
]

def fetch_daily_pnl(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    for _ in range(5):
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200 and resp.text.strip():
                data = resp.json()
                records = data.get("records", [])
                if not records:
                    return None
                dates = []
                pnls = []
                for r in records:
                    if isinstance(r, list) and len(r) >= 2:
                        dates.append(r[0])
                        pnls.append(r[1])
                    elif isinstance(r, dict):
                        dates.append(r.get("date"))
                        pnls.append(r.get("pnl"))
                df = pd.DataFrame({"date": dates, "pnl": pnls}).dropna()
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date").set_index("date")
                return df["pnl"].diff().dropna()
        except Exception:
            pass
        time.sleep(1)
    return None

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
    
    resp = session.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code not in (200, 201):
        print(f"  Sim error {resp.status_code}: {resp.text[:120]}", flush=True)
        return None
        
    sim_progress_url = resp.headers.get("Location")
    if not sim_progress_url:
        return None
        
    for _ in range(45):
        time.sleep(5)
        stat = session.get(sim_progress_url)
        if stat.status_code == 200:
            sdata = stat.json()
            status = sdata.get("status")
            if status == "COMPLETE":
                return sdata.get("alpha")
            elif status == "ERROR":
                print(f"  Sim failed: {sdata.get('message')}", flush=True)
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
    
    return {
        "id": alpha_id,
        "sharpe": sharpe,
        "fitness": fitness,
        "turnover": turnover,
        "margin": margin,
        "returns": returns,
        "drawdown": drawdown,
        "sub_univ_pass": sub_univ_pass
    }

def evaluate_correlation(session, target_id, submitted_daily_cache):
    target_daily = fetch_daily_pnl(session, target_id)
    if target_daily is None:
        return 999.0, "UNKNOWN"
        
    max_corr = -1.0
    max_sub = ""
    for sub_id, sub_daily in submitted_daily_cache.items():
        common = pd.concat([target_daily, sub_daily], axis=1, join="inner").dropna()
        if len(common) > 100:
            c = common.iloc[:, 0].corr(common.iloc[:, 1])
            if c > max_corr:
                max_corr = c
                max_sub = sub_id
    return max_corr, max_sub

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    if not session:
        print("Auth failed", flush=True)
        return
        
    print("Pre-loading Daily Returns for 9 submitted alphas...", flush=True)
    submitted_daily_cache = {}
    for sub_id in SUBMITTED_ALPHAS:
        s = fetch_daily_pnl(session, sub_id)
        if s is not None:
            submitted_daily_cache[sub_id] = s
            print(f"  Loaded {sub_id} ({len(s)} days)", flush=True)
            
    variations = [
        # Branch 1: Options IV Skew (Strong institutional signal)
        {
            "name": "B1: Options IV Skew Momentum",
            "expr": "ts_decay_linear(group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)) / ts_backfill(implied_volatility_mean_180, 20), subindustry), 15)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Branch 2: Peer Group Momentum Gap (Mean reversion intra-sector)
        {
            "name": "B2: 5-Day Peer vs Stock Gap Reversion",
            "expr": "cum_rel = (1 + ts_delay(rel_ret_all, 4)) * (1 + ts_delay(rel_ret_all, 3)) * (1 + ts_delay(rel_ret_all, 2)) * (1 + ts_delay(rel_ret_all, 1)) * (1 + rel_ret_all); cum_ret = (1 + ts_delay(returns, 4)) * (1 + ts_delay(returns, 3)) * (1 + ts_delay(returns, 2)) * (1 + ts_delay(returns, 1)) * (1 + returns); ts_decay_linear(rank(cum_rel - cum_ret), 10)",
            "decay": 0, "trunc": 0.08, "neut": "SECTOR"
        },
        # Branch 3: Long-term Investment Trend (Regression over 2 years)
        {
            "name": "B3: Long-Term Investment Trend x Revenue Momentum",
            "expr": "ts_decay_linear(rank(ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 504, rettype = 2) * group_rank(ts_delta(sales, 60), subindustry)), 20)",
            "decay": 0, "trunc": 0.08, "neut": "SUBINDUSTRY"
        },
        # Branch 4: FCF Quality vs Capex Spread
        {
            "name": "B4: True FCF Quality vs Capex",
            "expr": "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry), 15)",
            "decay": 0, "trunc": 0.08, "neut": "INDUSTRY"
        },
        # Branch 5: Microstructure Bull Trap (1min News slope)
        {
            "name": "B5: News 1Min Slope Bull Trap",
            "expr": "slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 10, rettype = 2); ts_decay_linear(group_rank(-ts_backfill(news_max_up_ret, 60) * abs(slope), subindustry), 10)",
            "decay": 0, "trunc": 0.08, "neut": "INDUSTRY"
        }
    ]

    print("\n================ STARTING SPECTACULAR BATCH ================\n", flush=True)
    results = []
    
    for cand in variations:
        print(f"\n--- Testing: {cand['name']} ---", flush=True)
        aid = run_simulation(session, cand['expr'], decay=cand['decay'], truncation=cand['trunc'], neutralization=cand['neut'])
        if aid:
            perf = check_alpha_performance(session, aid)
            if perf:
                max_corr, worst_sub = evaluate_correlation(session, aid, submitted_daily_cache)
                print(f"  Alpha ID: {aid}", flush=True)
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fitness: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps | Returns: {perf['returns']*100:.1f}%", flush=True)
                print(f"  Sub-Univ Pass: {perf['sub_univ_pass']} | Max Daily Ret Corr vs Portfolio: {max_corr:.4f} (vs {worst_sub})", flush=True)
                perf["name"] = cand["name"]
                perf["max_corr"] = max_corr
                perf["worst_sub"] = worst_sub
                results.append(perf)

    print("\n================ FINAL SUMMARY ================\n", flush=True)
    for r in results:
        status = "SPECTACULAR CANDIDATE" if r['sharpe'] >= 2.0 and r['fitness'] >= 2.0 and r['sub_univ_pass'] and r['max_corr'] < 0.70 else "NEEDS_TUNING"
        print(f"[{status}] ID: {r['id']} | Sharpe: {r['sharpe']:.2f} | Fit: {r['fitness']:.2f} | TO: {r['turnover']*100:.1f}% | Margin: {r['margin']*10000:.1f} bps | Corr: {r['max_corr']:.4f}", flush=True)

if __name__ == "__main__":
    main()
