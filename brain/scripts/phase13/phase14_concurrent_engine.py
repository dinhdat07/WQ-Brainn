import os
import sys
import json
import time
import requests
import numpy as np
from concurrent.futures import ThreadPoolExecutor

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def fetch_pnl(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    resp = session.get(url)
    if resp.status_code != 200 or not resp.text.strip():
        return []
    data = resp.json()
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
    return [cum_pnl[i+1] - cum_pnl[i] for i in range(len(cum_pnl)-1)]

def run_single_simulation(session, cand, active_rets):
    print(f"[LAUNCH] {cand['name']}: {cand['expr']}")
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": cand.get("decay", 0),
            "neutralization": cand.get("neut", "SUBINDUSTRY"),
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": cand["expr"],
    }
    
    resp = session.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code != 201:
        print(f"[FAIL] {cand['name']} post failed: {resp.status_code} {resp.text}")
        return None
        
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    
    alpha_id = None
    for _ in range(45):
        time.sleep(4)
        s_resp = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}")
        if s_resp.status_code == 200:
            s_data = s_resp.json()
            s_status = s_data.get("status")
            if s_status == "COMPLETE":
                alpha_id = s_data.get("alpha")
                break
            elif s_status in ["ERROR", "FAIL", "CANCELLED"]:
                print(f"[FAIL] {cand['name']} sim status: {s_status} -> {s_data.get('message')}")
                return None
                
    if not alpha_id:
        print(f"[TIMEOUT] {cand['name']} timed out.")
        return None
        
    a_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
    if a_resp.status_code != 200:
        return None
        
    a_data = a_resp.json()
    is_data = a_data.get("is", {})
    sharpe = is_data.get("sharpe", 0)
    fitness = is_data.get("fitness", 0)
    turnover = is_data.get("turnover", 0)
    margin = is_data.get("margin", 0)
    sub_sharpe = is_data.get("subUniverseSharpe", 0)
    checks = a_data.get("is", {}).get("checks", [])
    
    pnl = fetch_pnl(session, alpha_id)
    new_ret = daily_returns(pnl)
    
    max_corr = 0.0
    max_corr_id = None
    corrs = {}
    
    if len(new_ret) > 100:
        for old_id, old_ret in active_rets.items():
            min_len = min(len(new_ret), len(old_ret))
            if min_len > 100:
                c = float(np.corrcoef(new_ret[-min_len:], old_ret[-min_len:])[0, 1])
                corrs[old_id] = round(c, 4)
                if abs(c) > abs(max_corr):
                    max_corr = c
                    max_corr_id = old_id
                    
    res = {
        "name": cand["name"],
        "alpha_id": alpha_id,
        "formula": cand["expr"],
        "decay": cand.get("decay", 0),
        "neut": cand.get("neut", "SUBINDUSTRY"),
        "sharpe": sharpe,
        "fitness": fitness,
        "turnover": turnover,
        "margin": margin,
        "sub_sharpe": sub_sharpe,
        "max_corr": max_corr,
        "max_corr_id": max_corr_id,
        "corrs": corrs,
        "checks": checks
    }
    
    print(f"\n[DONE] [{alpha_id}] {cand['name']}: Sharpe={sharpe:.2f} | Fit={fitness:.2f} | TO={turnover*100:.1f}% | SubSh={sub_sharpe:.2f} | MaxCorr={max_corr:.4f} (vs {max_corr_id})")
    return res

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    resp = session.get("https://api.worldquantbrain.com/users/self/alphas?stage=OS&limit=50")
    active_alphas = resp.json().get("results", [])
    print(f"Loaded {len(active_alphas)} active OS alphas. Pre-fetching daily returns...")
    
    active_rets = {}
    for a in active_alphas:
        aid = a["id"]
        pnl = fetch_pnl(session, aid)
        ret = daily_returns(pnl)
        if len(ret) > 100:
            active_rets[aid] = ret
        time.sleep(0.2)
        
    print(f"Pre-fetched returns for {len(active_rets)} active alphas.")
    
    candidates = [
        # 1. Competitor / Peer Network Lead-Lag Momentum Spillover
        {
            "name": "Competitor_Network_Momentum_5D",
            "expr": "ts_decay_linear(group_rank(ts_mean(ts_backfill(rel_ret_comp, 10), 5) - ts_mean(returns, 5), subindustry), 5)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 2. Product Space Overlap Peer Gap
        {
            "name": "Product_Overlap_Peer_Gap",
            "expr": "ts_decay_linear(group_rank(ts_backfill(rel_ret_all, 10) - returns, subindustry), 5)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 3. Supply Chain Partner Lead-Lag
        {
            "name": "Supply_Chain_Partner_LeadLag",
            "expr": "ts_decay_linear(group_rank(ts_backfill(rel_ret_part, 10) - returns, subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 4. Multi-Factor Acceleration + Cashflow Efficiency vs Valuation
        {
            "name": "MultiFactor_Acceleration_Derivative",
            "expr": "ts_decay_linear(group_rank(multi_factor_acceleration_score_derivative, subindustry) + group_rank(cashflow_efficiency_rank_derivative, subindustry) - group_rank(relative_valuation_rank_derivative, subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 5. Growth Potential Derivative Momentum
        {
            "name": "Growth_Potential_Derivative_Alpha",
            "expr": "ts_decay_linear(group_rank(growth_potential_rank_derivative, subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 6. Post-News Reaction Slope Bull-Trap (Silver #6)
        {
            "name": "News_Reaction_Slope_Bull_Trap",
            "expr": "ts_decay_linear(group_rank(-ts_backfill(news_max_up_ret, 30) * abs(ts_regression(ts_backfill(news_pct_1min, 30), ts_step(1), 5, rettype = 2)), industry), 5)",
            "decay": 0, "neut": "INDUSTRY"
        },
        # 7. Long-Term Investment Trend (Silver #4)
        {
            "name": "Long_Term_Investment_Trend",
            "expr": "ts_decay_linear(group_rank(ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 8. Operating Cashflow vs Capex Quality Spread (Silver #5)
        {
            "name": "FCF_Quality_Spread_Signal",
            "expr": "ts_decay_linear(ts_scale(ts_backfill(est_cashflow_op, 60), 252) - ts_scale(ts_backfill(est_capex, 60), 252), 22)",
            "decay": 2, "neut": "INDUSTRY"
        },
        # 9. Options Volume PCR vs Vol Jump Dislocation
        {
            "name": "Options_PCR_Vol_Dislocation",
            "expr": "ts_decay_linear(group_rank(1 / (ts_backfill(pcr_vol_270, 30) + 0.05), subindustry) + group_rank(ts_backfill(historical_volatility_10, 30) / (ts_backfill(parkinson_volatility_10, 30) + 0.001), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # 10. Share Turnover Velocity + Earnings Yield Hybrid
        {
            "name": "Share_Turnover_Velocity_Hybrid",
            "expr": "ts_decay_linear(-0.8 * group_rank(adv20 / (sharesout * close + 1), subindustry) + group_rank(est_ebit / cap, subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        }
    ]
    
    print(f"\n--- RUNNING {len(candidates)} CONCURRENT SIMULATIONS ---")
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_single_simulation, session, cand, active_rets) for cand in candidates]
        for f in futures:
            r = f.result()
            if r:
                results.append(r)
                
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase14_concurrent_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nCompleted! Saved {len(results)} evaluated models to {out_file}")

if __name__ == "__main__":
    main()
