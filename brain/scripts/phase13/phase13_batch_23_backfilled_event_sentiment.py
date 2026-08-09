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
        # --- 1. BACKFILLED MEAN EVENT SENTIMENT x EBITDA/EV ---
        "bf_event_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(mean_event_sentiment_score, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "bf_event_sent_ebitda_ev_intra_80d": "ts_decay_linear(group_zscore(ts_backfill(mean_event_sentiment_score, 90), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 80)",
        "bf_event_sent_ebitda_ev_pcr270_60d": "ts_decay_linear(group_zscore(ts_backfill(mean_event_sentiment_score, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * group_zscore(pcr_oi_270 / ts_delay(pcr_oi_270, 20), subindustry), 60)",

        # --- 2. BACKFILLED CORPORATE ACTION SENTIMENT ---
        "bf_corp_action_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(corporate_action_sentiment, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "bf_corp_action_sent_ebitda_ev_intra_80d": "ts_decay_linear(group_zscore(ts_backfill(corporate_action_sentiment, 90), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 80)",

        # --- 3. BACKFILLED EARNINGS EVALUATION SENTIMENT ---
        "bf_earnings_eval_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(earnings_evaluation_sentiment, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "bf_earnings_eval_sent_ebitda_ev_intra_80d": "ts_decay_linear(group_zscore(ts_backfill(earnings_evaluation_sentiment, 90), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 80)",

        # --- 4. BACKFILLED EDITORIAL COMMENTARY SENTIMENT ---
        "bf_editorial_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(editorial_commentary_sentiment_2, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "bf_editorial_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(editorial_commentary_sentiment_2, 60), subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 5. BACKFILLED EQUITY SENTIMENT SCORE ---
        "bf_equity_sent_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(equity_sentiment_score, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "bf_equity_sent_assets_sales_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(equity_sentiment_score, 60), subindustry) * group_zscore(assets / sales, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- 6. NEWS IMPACT PROJECTION SCORE ---
        "bf_news_impact_ebitda_ev_intra_60d": "ts_decay_linear(group_zscore(ts_backfill(news_impact_projection_score, 60), subindustry) * group_zscore(ebitda / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 23 (Backfilled Event Sentiment)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_23_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 23 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
