import os
import sys
import json
import time
import requests
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def get_daily_pnl_returns(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    resp = session.get(url)
    if resp.status_code != 200 or not resp.text.strip():
        return {}
    try:
        data = resp.json()
    except Exception:
        return {}
    records = sorted(data.get("records", []), key=lambda r: r[0])
    daily_diffs = {}
    for i in range(1, len(records)):
        dt = records[i][0]
        daily_diffs[dt] = float(records[i][1]) - float(records[i-1][1])
    return daily_diffs

def simulate_alpha(session, expr, decay=5, neut="SUBINDUSTRY", trunc=0.08):
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": decay,
            "neutralization": neut,
            "truncation": trunc,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": expr,
    }
    
    resp = session.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code != 201:
        return None, f"HTTP {resp.status_code}: {resp.text[:100]}"
        
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    
    for _ in range(40):
        time.sleep(4)
        s_resp = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}")
        if s_resp.status_code == 200:
            s_data = s_resp.json()
            s_status = s_data.get("status")
            if s_status == "COMPLETE":
                return s_data.get("alpha"), None
            elif s_status in ["ERROR", "FAIL", "CANCELLED"]:
                return None, s_data.get("message")
    return None, "TIMEOUT"

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    # 1. Fetch active alphas
    resp = session.get("https://api.worldquantbrain.com/users/self/alphas?stage=OS&limit=50")
    active_alphas = resp.json().get("results", [])
    print(f"Loaded {len(active_alphas)} active OS alphas. Pre-fetching daily returns...")
    
    active_rets = {}
    for a in active_alphas:
        aid = a["id"]
        r = get_daily_pnl_returns(session, aid)
        if len(r) > 100:
            active_rets[aid] = r
            print(f"  - Active [{aid}] loaded: {len(r)} days")
        time.sleep(0.2)
        
    # Unexplored orthogonal alpha ideas across 4 pure fundamental & alternative domains
    models = [
        # Domain 1: Sloan Accrual & Earnings Quality
        {
            "domain": "Accruals_Quality",
            "desc": "Operating Cash Flow vs Net Income Divergence (Accrual Anomaly)",
            "expr": "ts_decay_linear(group_rank((ts_backfill(cashflow_op, 60) - ts_backfill(net_income, 60)) / (ts_backfill(assets, 60) + 1), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "domain": "Accruals_Quality",
            "desc": "Working Capital Accrual Ratio vs Assets",
            "expr": "ts_decay_linear(-group_rank(ts_delta(ts_backfill(working_capital, 60), 252) / (ts_backfill(assets, 60) + 1), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # Domain 2: Long-Term Capex & Investment Trend (Silver #4 adaptation)
        {
            "domain": "Capex_Investment_Trend",
            "desc": "Long-Term Capex / Sales Trend (Capital Reinvestment)",
            "expr": "ts_decay_linear(group_rank(ts_regression(ts_sum(ts_backfill(capex, 60), 252) / (ts_sum(ts_backfill(sales, 60), 252) + 1), ts_step(1), 504, rettype = 2), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "domain": "Capex_Investment_Trend",
            "desc": "R&D Expenditure Intensity to Market Cap",
            "expr": "ts_decay_linear(group_rank(ts_backfill(rnd_exp, 60) / (cap + 1), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # Domain 3: Analyst Estimate Revision Momentum & Consensus Dispersion
        {
            "domain": "Analyst_Estimates",
            "desc": "Analyst Consensus EPS 90-Day Revision Drift",
            "expr": "ts_decay_linear(group_rank(ts_delta(ts_backfill(est_eps, 20), 90) / (abs(ts_delay(ts_backfill(est_eps, 20), 90)) + 0.01), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "domain": "Analyst_Estimates",
            "desc": "Operating Cash Flow Estimate vs Capex Estimate (Silver #5 pure)",
            "expr": "ts_decay_linear(group_rank(ts_backfill(est_cashflow_op, 60) - ts_backfill(est_capex, 60), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "domain": "Analyst_Estimates",
            "desc": "Pre-tax Profit Estimate Growth Acceleration",
            "expr": "ts_decay_linear(group_rank(ts_delta(ts_backfill(est_ptp, 20), 30) - ts_delay(ts_delta(ts_backfill(est_ptp, 20), 30), 30), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # Domain 4: Fundamental Return on Invested Capital & Gross Profitability (Novy-Marx Quality)
        {
            "domain": "Quality_Profitability",
            "desc": "Novy-Marx Gross Profitability (Gross Profit / Assets)",
            "expr": "ts_decay_linear(group_rank((ts_backfill(sales, 60) - ts_backfill(cogs, 60)) / (ts_backfill(assets, 60) + 1), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "domain": "Quality_Profitability",
            "desc": "Return on Invested Capital (ROIC) Cross-Sectional Spread",
            "expr": "ts_decay_linear(group_rank(ts_backfill(ebit, 60) / (ts_backfill(assets, 60) - ts_backfill(current_liab, 60) + 1), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # Domain 5: Alternative Sentiment / Buzz Velocity
        {
            "domain": "Alt_Data",
            "desc": "Social Media Buzz Reversal (Glazar style)",
            "expr": "buzz = ts_backfill(scl12_buzz, 20); ts_decay_linear(-group_rank(buzz / (ts_mean(buzz, 60) + 1), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        }
    ]
    
    print(f"\n=======================================================")
    print(f"Beginning Deep Orthogonal Exploration across {len(models)} hypotheses...")
    
    winners = []
    for idx, m in enumerate(models):
        print(f"\n[{idx+1}/{len(models)}] Testing ({m['domain']}): {m['desc']}")
        print(f"   Expr: {m['expr']}")
        
        alpha_id, err = simulate_alpha(session, m["expr"], decay=m["decay"], neut=m["neut"])
        if not alpha_id:
            print(f"   [FAIL] {err}")
            time.sleep(2)
            continue
            
        a_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
        a_data = a_resp.json()
        is_data = a_data.get("is", {})
        sharpe = is_data.get("sharpe", 0)
        fitness = is_data.get("fitness", 0)
        turnover = is_data.get("turnover", 0)
        margin = is_data.get("margin", 0)
        sub_sharpe = is_data.get("subUniverseSharpe", 0)
        checks = is_data.get("checks", [])
        
        print(f"   [SUCCESS] [{alpha_id}] Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | TO: {turnover*100:.1f}% | SubSharpe: {sub_sharpe}")
        
        t_ret = get_daily_pnl_returns(session, alpha_id)
        max_c = 0.0
        max_id = None
        corrs = {}
        if len(t_ret) > 100:
            for aid, a_ret in active_rets.items():
                common_dates = sorted(set(t_ret.keys()).intersection(set(a_ret.keys())))
                if len(common_dates) > 100:
                    v1 = [t_ret[d] for d in common_dates]
                    v2 = [a_ret[d] for d in common_dates]
                    c = float(np.corrcoef(v1, v2)[0, 1])
                    corrs[aid] = round(c, 4)
                    if abs(c) > abs(max_c):
                        max_c = c
                        max_id = aid
                        
        print(f"   >>> MAX DAILY CORRELATION: {max_c:.4f} (vs {max_id}) <<<")
        print(f"   All correlations: {corrs}")
        
        # Check pass status
        check_fails = [c["name"] for c in checks if c.get("result") == "FAIL"]
        print(f"   Failing Checks: {check_fails if check_fails else 'NONE (ALL PASS)'}")
        
        m_res = {
            "domain": m["domain"],
            "desc": m["desc"],
            "alpha_id": alpha_id,
            "formula": m["expr"],
            "sharpe": sharpe,
            "fitness": fitness,
            "turnover": turnover,
            "margin": margin,
            "sub_sharpe": sub_sharpe,
            "max_corr": max_c,
            "max_corr_id": max_id,
            "corrs": corrs,
            "checks": checks
        }
        winners.append(m_res)
        time.sleep(2)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\deep_orthogonal_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(winners, f, indent=2)
    print(f"\nDone! Results saved to {out_file}")

if __name__ == "__main__":
    main()
