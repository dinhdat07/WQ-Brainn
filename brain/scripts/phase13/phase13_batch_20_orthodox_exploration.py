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
        # --- 1. IV TERM STRUCTURE SLOPE (180d - 30d) ---
        "iv_slope_180_30_asset_turn_intra_60d": "ts_decay_linear(group_zscore(implied_volatility_mean_180 - implied_volatility_mean_30, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "iv_slope_180_30_asset_turn_corr_60d": "ts_decay_linear(group_zscore(implied_volatility_mean_180 - implied_volatility_mean_30, subindustry) * group_zscore(sales / assets, subindustry) * ts_corr(returns, volume, 20), 60)",
        "iv_slope_360_30_asset_turn_intra_80d": "ts_decay_linear(group_zscore(implied_volatility_mean_360 - implied_volatility_mean_30, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 80)",

        # --- 2. OPEN INTEREST PCR DYNAMICS (pcr_oi_90 / pcr_oi_180) ---
        "pcr_oi_90_trend_asset_turn_intra_60d": "ts_decay_linear(group_zscore(pcr_oi_90 / ts_delay(pcr_oi_90, 20), subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "pcr_oi_180_trend_asset_turn_intra_60d": "ts_decay_linear(group_zscore(pcr_oi_180 / ts_delay(pcr_oi_180, 20), subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "pcr_oi_60_trend_asset_turn_intra_60d": "ts_decay_linear(group_zscore(pcr_oi_60 / ts_delay(pcr_oi_60, 20), subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 3. LONG-TERM IV MEAN SKEW (180d / 270d / 360d) ---
        "iv_skew_180_asset_turn_intra_60d": "ts_decay_linear(group_zscore(implied_volatility_mean_skew_180, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "iv_skew_270_asset_turn_intra_60d": "ts_decay_linear(group_zscore(implied_volatility_mean_skew_270, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "iv_skew_360_asset_turn_intra_60d": "ts_decay_linear(group_zscore(implied_volatility_mean_skew_360, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 4. PARKINSON VOLATILITY SPREAD ---
        "parkinson_vrp_30_asset_turn_intra_60d": "ts_decay_linear(group_zscore(parkinson_volatility_30 - implied_volatility_mean_30, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "parkinson_vrp_60_asset_turn_intra_60d": "ts_decay_linear(group_zscore(parkinson_volatility_60 - implied_volatility_mean_60, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 5. ANALYST RECOMMENDATION SCORE ---
        "analyst_rec_asset_turn_intra_60d": "ts_decay_linear(group_zscore(-ts_backfill(anl4_fs_detail_rec_v4_nd_estimate, 60), subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 20...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_20_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 20 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
