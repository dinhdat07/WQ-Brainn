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
        # --- 1. CORPORATE ACTION & EARNINGS EVALUATION SENTIMENT ---
        "corp_action_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(corporate_action_sentiment, subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "earnings_eval_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(earnings_evaluation_sentiment, subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "news_impact_proj_assets_sales_intra_60d": "ts_decay_linear(group_zscore(news_impact_projection_score, subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 2. MEAN EVENT SENTIMENT & EQUITY SENTIMENT ---
        "mean_event_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(mean_event_sentiment_score, subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "equity_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(equity_sentiment_score, subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "editorial_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(editorial_commentary_sentiment_2, subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 3. COMBINATIONS WITH EBITDA/EV & ROIC-LIKE PROXIES ---
        "corp_action_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(corporate_action_sentiment, subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "earnings_eval_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(earnings_evaluation_sentiment, subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "mean_event_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(mean_event_sentiment_score, subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 4. SENTIMENT x PRICE-VOLUME CORRELATION (80d Decay) ---
        "corp_action_sent_corr_ret_vol_80d": "-ts_decay_linear(group_zscore(corporate_action_sentiment, subindustry) * ts_corr(returns, volume, 20), 80)",
        "earnings_eval_sent_corr_ret_vol_80d": "-ts_decay_linear(group_zscore(earnings_evaluation_sentiment, subindustry) * ts_corr(returns, volume, 20), 80)",
        "mean_event_sent_corr_ret_vol_80d": "-ts_decay_linear(group_zscore(mean_event_sentiment_score, subindustry) * ts_corr(returns, volume, 20), 80)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 22 (Hidden Sentiment Gems)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_22_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 22 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
