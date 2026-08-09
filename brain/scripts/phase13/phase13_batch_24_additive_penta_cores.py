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
        # --- 1. PENTA-CORE REVISION & OPTIONS SKEW HYBRID ---
        "pentacore_opt_skew_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + 0.5 * group_rank(implied_volatility_mean_skew_180, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 10)",
        
        # --- 2. PENTA-CORE REVISION & PCR DYNAMICS ---
        "pentacore_pcr_trend_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + 0.5 * group_rank(pcr_oi_270 / ts_delay(pcr_oi_270, 20), subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 10)",

        # --- 3. PENTA-CORE REVISION & EPS DISPERSION / ACCURACY ---
        "pentacore_eps_median_mean_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 10)",

        # --- 4. PENTA-CORE HIGHER DECAY (20d/30d) FOR LOWER TURNOVER (< 4%) ---
        "pentacore_base_decay20": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 20)",
        "pentacore_base_decay30": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-ts_delta(close, 4) / close, subindustry), 30)",

        # --- 5. PENTA-CORE WITH INTRADAY LOCATION VALUE REVERSION ---
        "pentacore_clv_decay15": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-(close - open) / (high - low + 0.001), subindustry), 15)",
        "pentacore_clv_decay20": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.8 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), subindustry) + group_rank(working_capital / assets, subindustry) + 0.5 * group_rank(-(close - open) / (high - low + 0.001), subindustry), 20)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 24 (Additive Penta-Core Multi-Factors)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_24_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 24 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
