"""
Phase 10 Penta-Core Spectacular Refinement Optimizer
Iterates on the submittable orthogonal champion d5ZXQ3Ej (Sharpe 1.50, Fit 1.13, TO 6.0%, Margin 23.9 bps, Max Corr 0.6072)
to achieve Spectacular Sharpe (1.70 - 2.50+) while strictly locking Max Daily Return Correlation < 0.70.
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

def run_simulation(session, expr, decay=10, truncation=0.08):
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": decay,
            "neutralization": "SUBINDUSTRY",
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
        time.sleep(4)
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
    sub_univ_val = sub_univ_check.get("value", 0) if sub_univ_check else 0
    sub_univ_lim = sub_univ_check.get("limit", 0) if sub_univ_check else 0
    
    conc_check = next((c for c in checks if c.get("name") == "CONCENTRATED_WEIGHT"), None)
    conc_pass = (conc_check.get("result") == "PASS") if conc_check else True
    
    return {
        "id": alpha_id,
        "sharpe": sharpe,
        "fitness": fitness,
        "turnover": turnover,
        "margin": margin,
        "returns": returns,
        "drawdown": drawdown,
        "sub_univ_pass": sub_univ_pass,
        "sub_univ_val": sub_univ_val,
        "sub_univ_lim": sub_univ_lim,
        "conc_pass": conc_pass
    }

def evaluate_correlation(session, target_id, submitted_pnl_cache):
    target_daily = fetch_daily_pnl(session, target_id)
    if target_daily is None:
        return 999.0, "UNKNOWN"
        
    max_corr = -1.0
    max_sub = ""
    for sub_id, sub_daily in submitted_pnl_cache.items():
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
            
    print(f"\nLoaded {len(submitted_daily_cache)}/{len(SUBMITTED_ALPHAS)} submitted alphas into cache.", flush=True)

    variations = [
        # Variation 1: Decay 12 + Multi-Horizon EBIT & Retained Earnings
        {
            "name": "Penta V1: EBIT Yield + FCF + Retained Earnings + 30d Revision + 4d Rev",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + 0.5 * group_rank(retained_earnings / assets, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 12)",
            "decay": 12,
            "trunc": 0.08
        },
        # Variation 2: Decay 10 + Volatility-scaled Reversion Engine
        {
            "name": "Penta V2: EBIT Yield + FCF + Revision + Working Capital + Vol-scaled Reversion",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.6 * group_rank(-ts_delta(close, 3) / (ts_std_dev(returns, 20) * close + 0.001), subindustry), 10)",
            "decay": 10,
            "trunc": 0.08
        },
        # Variation 3: Decay 10 + 20d Revision + 4d Reversion
        {
            "name": "Penta V3: EBIT Yield + FCF + 20d Revision + Working Capital + 4d Reversion",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 10)",
            "decay": 10,
            "trunc": 0.08
        },
        # Variation 4: Truncation 0.05 + Decay 10 (Reduces tail concentration, boosts Sharpe/Fitness)
        {
            "name": "Penta V4: Truncation 0.05 Champion Tuning",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 10)",
            "decay": 10,
            "trunc": 0.05
        },
        # Variation 5: Decay 14 + FCF Yield Heavy
        {
            "name": "Penta V5: Decay 14 + FCF Heavy + 30d Revision + Working Capital",
            "expr": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 1.2 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.4 * group_rank(-ts_delta(close, 5) / close, subindustry), 14)",
            "decay": 14,
            "trunc": 0.08
        }
    ]

    print("\n================ STARTING PENTA REFINEMENT BATCH ================\n", flush=True)
    results = []
    
    for cand in variations:
        print(f"\n--- Testing: {cand['name']} ---", flush=True)
        print(f"Expr: {cand['expr']}", flush=True)
        aid = run_simulation(session, cand['expr'], decay=cand['decay'], truncation=cand['trunc'])
        if aid:
            perf = check_alpha_performance(session, aid)
            if perf:
                max_corr, worst_sub = evaluate_correlation(session, aid, submitted_daily_cache)
                perf["max_corr"] = max_corr
                perf["worst_sub"] = worst_sub
                perf["name"] = cand["name"]
                perf["expr"] = cand["expr"]
                perf["decay"] = cand["decay"]
                perf["trunc"] = cand["trunc"]
                
                print(f"  Alpha ID: {aid}", flush=True)
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fitness: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps | Returns: {perf['returns']*100:.1f}%", flush=True)
                print(f"  Sub-Univ Sharpe: {perf['sub_univ_val']} (Limit: {perf['sub_univ_lim']}) -> {'PASS' if perf['sub_univ_pass'] else 'FAIL'}", flush=True)
                print(f"  Max Daily Ret Corr vs Portfolio: {max_corr:.4f} (vs {worst_sub}) -> {'PASS (<0.7)' if max_corr < 0.70 else 'FAIL (>=0.7)'}", flush=True)
                
                results.append(perf)

    print("\n================ SUMMARY OF PENTA CANDIDATES ================\n", flush=True)
    for r in results:
        status = "SPECTACULAR CANDIDATE" if r['sharpe'] >= 1.25 and r['fitness'] >= 1.0 and r['sub_univ_pass'] and r['max_corr'] < 0.70 else "NEEDS_TUNING"
        print(f"[{status}] ID: {r['id']} | Sharpe: {r['sharpe']:.2f} | Fit: {r['fitness']:.2f} | TO: {r['turnover']*100:.1f}% | Margin: {r['margin']*10000:.1f} bps | Sub-Univ: {'PASS' if r['sub_univ_pass'] else 'FAIL'} | MaxCorr: {r['max_corr']:.4f} ({r['worst_sub']})", flush=True)

if __name__ == "__main__":
    main()
