"""
Phase 10 Orthogonal Spectacular Supercharger
Focuses on supercharging the passing orthogonal architectures (vRNqd0mb & WjAqNnWk)
to reach Spectacular/Excellent performance (Sharpe >= 1.5 - 2.5, Fitness >= 1.5 - 2.6,
TO 5-8%, Margin > 20 bps, Max Ret Corr < 0.70).
"""

import os
import sys
import json
import time
import requests
import pandas as pd
import numpy as np

# Ensure parent directory is in sys.path
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
                        
                df = pd.DataFrame({"date": dates, "pnl": pnls})
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date").drop_duplicates("date").set_index("date")
                return df["pnl"]
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
    return None

def run_simulation(session, expr, decay=12, neutralization="SUBINDUSTRY", truncation=0.08):
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
        print(f"Sim error {resp.status_code}: {resp.text[:120]}", flush=True)
        return None
        
    sim_progress_url = resp.headers.get("Location")
    if not sim_progress_url:
        return None
        
    for _ in range(45):
        time.sleep(4)
        stat = session.get(sim_progress_url)
        if stat.status_code == 200:
            sdata = stat.json()
            status = sdata.get("status")
            if status == "COMPLETE":
                return sdata.get("alpha")
            elif status == "ERROR":
                print(f"Sim failed: {sdata.get('message')}", flush=True)
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
    
    conc_check = next((c for c in checks if c.get("name") == "CONCENTRATED_WEIGHT"), None)
    conc_pass = (conc_check.get("result") == "PASS") if conc_check else True
    
    turnover_check = next((c for c in checks if c.get("name") == "LOW_TURNOVER" or c.get("name") == "HIGH_TURNOVER"), None)
    
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
        "conc_pass": conc_pass,
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
        print("Auth failed", flush=True)
        return
        
    print("Pre-loading PnL for 9 submitted alphas...", flush=True)
    submitted_pnl_cache = {}
    for sub_id in SUBMITTED_ALPHAS:
        s = fetch_pnl_series(session, sub_id)
        if s is not None:
            submitted_pnl_cache[sub_id] = s
            print(f"  Loaded {sub_id} ({len(s)} days)", flush=True)
            
    print(f"\nLoaded {len(submitted_pnl_cache)}/{len(SUBMITTED_ALPHAS)} submitted alphas into cache.", flush=True)

    # Systematic Variations to Supercharge Sharpe & Fitness while maintaining Orthogonality (< 0.70)
    variations = [
        # Batch A: Supercharged Quad Orthogonal (Tuning Decay, Weights, Reversion Term)
        {
            "name": "Quad A1: Decay 8, Vol-adjusted 3d Reversion",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.6 * group_rank(-ts_delta(close, 3) / (ts_std_dev(returns, 20) * close + 0.001), subindustry), 8)",
            "decay": 8
        },
        {
            "name": "Quad A2: Decay 10, Volume-Weighted 5d Reversion",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_rank(volume, 10) * ts_delta(close, 5) / close, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Quad A3: Consensus EPS + EBIT Multi-Revision Engine",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(ts_delta(est_eps, 20) / (abs(est_eps) + 0.05), subindustry) + group_rank(working_capital / assets, subindustry) + 0.4 * group_rank(-ts_delta(close, 5) / close, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Quad A4: Forward EBIT Yield + FCF Yield + Working Capital + 4d Reversion",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 10)",
            "decay": 10
        },
        
        # Batch B: Non-Linear & Interaction Enhanced Orthogonal Formulations
        {
            "name": "Pillar B1: Multiplicative Interaction (EBIT Yield * Revision Drift) + Quality",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) * group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.4 * group_rank(-ts_delta(close, 5) / close, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Pillar B2: Forward Sales Yield + EBIT Drift + Retained Earnings Solvency",
            "expr": "ts_decay_linear(group_rank(est_sales / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(retained_earnings / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 5) / close, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Pillar B3: Operating Margin Quality + Consensus Revision + Working Capital + Vol Reversal",
            "expr": "ts_decay_linear(group_rank(operating_income / sales, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_rank(volume, 5) * ts_delta(close, 4) / close, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Pillar B4: 5-Factor Institutional Sovereign (EBIT Yield + EPS Drift + FCF + WC + Vol Reversal)",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_eps, 30) / (abs(est_eps) + 0.05), subindustry) + 0.7 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_rank(volume, 10) * ts_delta(close, 3) / close, subindustry), 8)",
            "decay": 8
        },
        
        # Batch C: Alpha 101 Formula Adaptations with Valid FastExpr Syntax
        {
            "name": "Alpha101 C1: Alpha #41 (sqrt(high*low) - vwap) + Consensus Revision + Working Cap",
            "expr": "ts_decay_linear(group_rank(sqrt(high * low) - vwap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Alpha101 C2: Alpha #53 Non-Linear Intraday Spread + EBIT Yield + EPS Drift",
            "expr": "ts_decay_linear(group_rank(-ts_delta((((close - low) - (high - close)) / (close - open + 0.0001)), 9), subindustry) + group_rank(est_ebit / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry), 10)",
            "decay": 10
        }
    ]

    print("\n================ STARTING SUPERCHARGER BATCH ================\n", flush=True)
    results = []
    
    for cand in variations:
        print(f"\n--- Testing: {cand['name']} ---", flush=True)
        print(f"Expr: {cand['expr']}", flush=True)
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
                
                print(f"  Alpha ID: {aid}", flush=True)
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fitness: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps | Returns: {perf['returns']*100:.1f}%", flush=True)
                print(f"  Sub-Univ Sharpe: {perf['sub_univ_val']:.2f} (Limit: {perf['sub_univ_lim']:.2f}) -> {'PASS' if perf['sub_univ_pass'] else 'FAIL'}", flush=True)
                print(f"  Max Daily Ret Corr vs Portfolio: {max_corr:.4f} (vs {worst_sub}) -> {'PASS (<0.7)' if max_corr < 0.7 else 'FAIL (>=0.7)'}", flush=True)
                
                results.append(perf)
        time.sleep(2)
        
    print("\n================ SUMMARY OF SUPERCHARGED CANDIDATES ================\n", flush=True)
    for r in results:
        is_spectacular = (r['sharpe'] >= 1.4 and r['fitness'] >= 1.0 and r['sub_univ_pass'] and r['max_corr'] < 0.70 and r['turnover'] >= 0.03 and r['turnover'] <= 0.15)
        status = "SPECTACULAR CANDIDATE" if is_spectacular else "NEEDS_TUNING"
        print(f"[{status}] ID: {r['alpha_id']} | Sharpe: {r['sharpe']:.2f} | Fit: {r['fitness']:.2f} | TO: {r['turnover']*100:.1f}% | Margin: {r['margin']*10000:.1f} bps | Sub-Univ: {'PASS' if r['sub_univ_pass'] else 'FAIL'} | MaxCorr: {r['max_corr']:.4f} ({r['worst_sub']})", flush=True)

    # Save detailed JSON of all results
    with open(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase10_supercharged_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
