import sys
import json
import time
import requests

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def simulate_alpha(session, code, name):
    url = "https://api.worldquantbrain.com/simulations"
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "OFF",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": code
    }
    
    for attempt in range(5):
        resp = session.post(url, json=payload)
        if resp.status_code == 201:
            sim_loc = resp.headers.get("Location")
            sim_id = sim_loc.split("/")[-1] if sim_loc else ""
            return {"name": name, "code": code, "status": "simulating", "id": sim_id, "sim_url": sim_loc}
        elif resp.status_code == 429:
            time.sleep(10)
        else:
            return {"name": name, "code": code, "status": "error", "error": resp.text}
    return {"name": name, "code": code, "status": "error", "error": "rate_limited"}

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    alphas = {
        # --- 1. TRIAD 90D IV REGIME + EBITDA/EV + INTRADAY REVERSION ---
        "triad_90d_ebitda_ev_intra_10d": "ts_decay_linear(group_rank(ebitda / enterprise_value, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_90, 60) < 1, (ts_backfill(implied_volatility_call_90, 60) - ts_backfill(implied_volatility_put_90, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",
        "triad_90d_ebitda_ev_intra_15d": "ts_decay_linear(group_rank(ebitda / enterprise_value, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_90, 60) < 1, (ts_backfill(implied_volatility_call_90, 60) - ts_backfill(implied_volatility_put_90, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 15)",

        # --- 2. TRIAD 180D IV REGIME + WORKING CAPITAL/ASSETS + INTRADAY REVERSION ---
        "triad_180d_wc_assets_intra_10d": "ts_decay_linear(group_rank(working_capital / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, (ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",
        "triad_180d_wc_assets_intra_15d": "ts_decay_linear(group_rank(working_capital / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, (ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 15)",

        # --- 3. TRIAD ANALYST DISPERSION + REVISION REGIME + INTRADAY REVERSION ---
        "triad_anl_disp_revision_intra_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",
        "triad_anl_disp_revision_intra_15d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 15)",

        # --- 4. TRIAD 90D IV REGIME + GROSS PROFIT/ASSETS + VOLUME REVERSION ---
        "triad_90d_gp_assets_vol_corr_10d": "ts_decay_linear(group_rank(gross_profit / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_90, 60) < 1, (ts_backfill(implied_volatility_call_90, 60) - ts_backfill(implied_volatility_put_90, 60)), -1), subindustry) + group_rank(-ts_corr(returns, volume, 20), subindustry), 10)",
        "triad_90d_gp_assets_vol_corr_15d": "ts_decay_linear(group_rank(gross_profit / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_90, 60) < 1, (ts_backfill(implied_volatility_call_90, 60) - ts_backfill(implied_volatility_put_90, 60)), -1), subindustry) + group_rank(-ts_corr(returns, volume, 20), subindustry), 15)",

        # --- 5. TRIAD 180D IV SKEW REGIME + FCF YIELD + INTRADAY REVERSION ---
        "triad_180d_fcf_skew_intra_10d": "ts_decay_linear(group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, ts_backfill(implied_volatility_mean_skew_180, 60), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",
        "triad_180d_fcf_skew_intra_15d": "ts_decay_linear(group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, ts_backfill(implied_volatility_mean_skew_180, 60), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 15)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 25 (Orthogonal Triad Mutations)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_25_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 25 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
