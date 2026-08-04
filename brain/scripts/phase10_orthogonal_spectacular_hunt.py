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
                alpha_id = sdata.get("alpha")
                return alpha_id
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
    
    # Extract metrics
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

    # Candidate Orthogonal Architectures
    experiments = [
        # Track A: Volatility Term Structure Slope (30d vs 360d) + Long-Term Capital Investment
        {
            "name": "Track A1: Vol Term Structure Slope + Sloan Accruals",
            "expr": "ts_decay_linear(group_rank(ts_backfill(implied_volatility_call_30, 30) - ts_backfill(implied_volatility_call_360, 30), subindustry) + group_rank(-(ts_delta(fnd6_act, 252) - ts_delta(fnd6_che, 252) - (ts_delta(fnd6_lct, 252) - ts_delta(fnd6_dlc, 252))) / ts_backfill(assets, 252), subindustry), 15)",
            "decay": 15
        },
        # Track A2: Pure Volatility Term Structure Ratio (Contango/Backwardation)
        {
            "name": "Track A2: Vol Contango Ratio + Asset Growth Penalty",
            "expr": "ts_decay_linear(group_rank(ts_backfill(implied_volatility_mean_30, 30) / ts_backfill(implied_volatility_mean_360, 30), subindustry) + group_rank(-ts_delta(assets, 252) / ts_backfill(assets, 252), subindustry), 15)",
            "decay": 15
        },
        # Track B: Analyst EPS Revision Momentum + Earnings Surprise
        {
            "name": "Track B1: EPS Revision Momentum + Cash Flow Growth",
            "expr": "ts_decay_linear(group_rank(ts_delta(est_eps_mean, 20) / (abs(est_eps_mean) + 0.01), subindustry) + group_rank(ts_delta(fnd6_cashflow_op, 252) / ts_backfill(assets, 252), subindustry), 12)",
            "decay": 12
        },
        # Track B2: Analyst Recommendation Drift + ROIC
        {
            "name": "Track B2: Target Price Revisions + Operating Profitability",
            "expr": "ts_decay_linear(group_rank(ts_delta(target_price_mean, 20) / target_price_mean, subindustry) + group_rank(fnd6_ebit / ts_backfill(assets, 252), subindustry), 15)",
            "decay": 15
        },
        # Track C: Alpha 101 Mathematical Price/Volume Anomaly (Alpha 54 / Alpha 41 / Alpha 12 hybrid)
        {
            "name": "Track C1: Alpha 101 #41 (High-Low Geometric Spread vs VWAP) + Group Rank",
            "expr": "ts_decay_linear(group_rank(power(high * low, 0.5) - vwap, subindustry) + group_rank(fnd6_ebit / ts_backfill(assets, 252), subindustry), 10)",
            "decay": 10
        },
        {
            "name": "Track C2: Alpha 101 #54 Hybrid + Cash Flow Quality",
            "expr": "ts_decay_linear(group_rank(- (low - close) * power(open, 2) / ((low - high - 0.001) * power(close, 2)), subindustry) + group_rank(fnd6_cashflow_op / ts_backfill(cap, 60), subindustry), 10)",
            "decay": 10
        },
        # Track D: Short Interest Squeeze Pressure + Return on Assets
        {
            "name": "Track D1: Days to Cover Reversal + Operating Margin",
            "expr": "ts_decay_linear(group_rank(-days_to_cover, subindustry) + group_rank(fnd6_ebit / ts_backfill(sales, 252), subindustry), 15)",
            "decay": 15
        },
        {
            "name": "Track D2: Short Interest Ratio Delta + Asset Efficiency",
            "expr": "ts_decay_linear(group_rank(-ts_delta(short_interest_ratio, 20), subindustry) + group_rank(fnd6_ebit / ts_backfill(assets, 252), subindustry), 12)",
            "decay": 12
        }
    ]

    print("\n================ STARTING ORTHOGONAL ALPHA HUNT ================\n")
    results = []
    
    for exp in experiments:
        print(f"\n--- Testing: {exp['name']} ---")
        print(f"Expr: {exp['expr']}")
        aid = run_simulation(session, exp['expr'], decay=exp['decay'])
        if aid:
            perf = check_alpha_performance(session, aid)
            if perf:
                max_corr, worst_sub = evaluate_correlation(session, aid, submitted_pnl_cache)
                perf["max_corr"] = max_corr
                perf["worst_sub"] = worst_sub
                perf["name"] = exp["name"]
                perf["expr"] = exp["expr"]
                
                print(f"  Alpha ID: {aid}")
                print(f"  Sharpe: {perf['sharpe']:.2f} | Fitness: {perf['fitness']:.2f} | TO: {perf['turnover']*100:.1f}% | Margin: {perf['margin']*10000:.1f} bps")
                print(f"  Sub-Univ Sharpe: {perf['sub_univ_val']:.2f} (Limit: {perf['sub_univ_lim']:.2f}) -> {'PASS' if perf['sub_univ_pass'] else 'FAIL'}")
                print(f"  Max Daily Ret Corr vs Portfolio: {max_corr:.4f} (vs {worst_sub}) -> {'PASS (<0.7)' if max_corr < 0.7 else 'FAIL (>=0.7)'}")
                
                results.append(perf)
        time.sleep(2)
        
    print("\n================ SUMMARY OF ALL ORTHOGONAL EXPERIMENTS ================\n")
    for r in results:
        status = "PASSED ALL" if (r['sharpe'] >= 1.5 and r['sub_univ_pass'] and r['max_corr'] < 0.70) else "NEEDS_TUNING"
        print(f"[{status}] ID: {r['alpha_id']} | Sharpe: {r['sharpe']:.2f} | Fit: {r['fitness']:.2f} | TO: {r['turnover']*100:.1f}% | Margin: {r['margin']*10000:.1f} bps | Sub-Univ: {'PASS' if r['sub_univ_pass'] else 'FAIL'} | MaxCorr: {r['max_corr']:.4f} ({r['worst_sub']})")

if __name__ == "__main__":
    main()
