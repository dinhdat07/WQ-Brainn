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
        # --- 1. KAKUSHADZE #55 (STOCHASTIC OSCILLATOR vs VOLUME CORRELATION) x FUNDAMENTAL ---
        "k55_stoch_vol_corr_assets_sales_60d": "-ts_decay_linear(ts_corr(group_rank((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12) + 0.001)), group_rank(volume), 10) * group_zscore(assets / sales, subindustry), 60)",
        "k55_stoch_vol_corr_assets_sales_80d": "-ts_decay_linear(ts_corr(group_rank((close - ts_min(low, 20)) / (ts_max(high, 20) - ts_min(low, 20) + 0.001)), group_rank(volume), 20) * group_zscore(assets / sales, subindustry), 80)",
        "k55_stoch_vol_corr_pcr270_60d": "-ts_decay_linear(ts_corr(group_rank((close - ts_min(low, 12)) / (ts_max(high, 12) - ts_min(low, 12) + 0.001)), group_rank(volume), 10) * group_zscore(pcr_oi_270 / ts_delay(pcr_oi_270, 20), subindustry), 60)",

        # --- 2. KAKUSHADZE #40 (HIGH VOLATILITY x HIGH-VOLUME CORRELATION) x FUNDAMENTAL ---
        "k40_high_vol_corr_assets_sales_60d": "-ts_decay_linear(group_rank(ts_std_dev(high, 10)) * ts_corr(high, volume, 10) * group_zscore(assets / sales, subindustry), 60)",
        "k40_high_vol_corr_assets_sales_80d": "-ts_decay_linear(group_rank(ts_std_dev(high, 20)) * ts_corr(high, volume, 20) * group_zscore(assets / sales, subindustry), 80)",

        # --- 3. KAKUSHADZE #60 (INTRADAY LOCATION VALUE x VOLUME) x FUNDAMENTAL ---
        "k60_clv_volume_assets_sales_60d": "-ts_decay_linear(group_rank(((close - low) - (high - close)) / (high - low + 0.001) * volume) * group_zscore(assets / sales, subindustry), 60)",
        "k60_clv_volume_assets_sales_80d": "-ts_decay_linear(group_rank(((close - low) - (high - close)) / (high - low + 0.001) * volume) * group_zscore(assets / sales, subindustry), 80)",

        # --- 4. KAKUSHADZE #58 / #59 (VWAP-VOLUME INDUSTRY RESIDUAL DYNAMICS) ---
        "k58_vwap_vol_corr_assets_sales_60d": "-ts_decay_linear(ts_corr(group_neutralize(vwap, subindustry), volume, 10) * group_zscore(assets / sales, subindustry), 60)",
        "k58_vwap_vol_corr_assets_sales_80d": "-ts_decay_linear(ts_corr(group_neutralize(vwap, subindustry), volume, 20) * group_zscore(assets / sales, subindustry), 80)",

        # --- 5. KAKUSHADZE #43 (VOLUME ACCELERATION x MOMENTUM REVERSION) x ASSETS/SALES ---
        "k43_vol_accel_reversion_assets_sales_60d": "ts_decay_linear(ts_rank(volume / adv20, 20) * ts_rank(-ts_delta(close, 7), 8) * group_zscore(assets / sales, subindustry), 60)",
        "k43_vol_accel_reversion_assets_sales_80d": "ts_decay_linear(ts_rank(volume / adv20, 20) * ts_rank(-ts_delta(close, 7), 8) * group_zscore(assets / sales, subindustry), 80)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 21 (Kakushadze Orthogonal Hybrids)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_21_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 21 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
