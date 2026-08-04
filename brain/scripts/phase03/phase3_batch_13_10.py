import os
import time
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain1 import sign_in
from brain3 import run_simulation

# truncate the log file on each run so we don't get confused
with open("logs/mutation_optimizer.log", "w") as f:
    f.truncate(0)

logging.basicConfig(filename="logs/mutation_optimizer.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Phase 3 Batch 13 - 10...")
    session, _ = sign_in("brain_credentials.txt")
    if not session:
        print("Auth failed")
        return

    base_settings = {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "neutralization": "NONE",
        "truncation": 0.08,
        "pasteurization": "ON",
        "testPeriod": "P2Y",
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False
    }
    
    tasks = [
        ("13_1_Analyst_Revisions_Divergence", "ts_decay_linear(rank(anl4_fs_basic_splt_v4_nd_eps_estimate - close), 5)", {}),
        ("13_2_Options_Volatility_Fixed", "ts_decay_linear(rank(ts_backfill(implied_volatility_call_120, 60) / parkinson_volatility_120), 5)", {}),
        ("13_3_Sentiment_Divergence", "ts_decay_linear(rank(-ts_corr(open, ts_backfill(composite_sentiment_score_2, 10), 10)), 5)", {}),
        ("13_4_EBITDA_Reversion", "ts_decay_linear(rank(-ts_delta(anl4_ebitda_mean, 60)), 5)", {}),
        ("13_5_RD_Intensity", "ts_decay_linear(rank(fnd6_newa2v1300_rdip), 5)", {}),
        ("13_6_Short_Indicators_vs_Price", "ts_decay_linear(rank(-ts_corr(best_position_indicator, close, 20)), 5)", {}),
        ("13_7_Earnings_Quality", "ts_decay_linear(rank(anl4_fs_basic_splt_v4_nd_sales_estimate / close), 5)", {}),
        ("13_8_Cash_Accumulation", "ts_decay_linear(rank(ts_delta(cash_st, 60)), 5)", {}),
        ("13_9_Analyst_Holds_Ratio", "ts_decay_linear(rank(-anl4_hold), 5)", {}),
        ("13_10_Target_Price_Acceleration", "ts_decay_linear(rank(ts_delta(est_ptp, 5)), 5)", {})
    ]
    
    file_logger.info(f"Total concepts to process: {len(tasks)}")
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}: {expr}")
        
        settings = base_settings.copy()
        settings.update(overrides)

        payload = {
            "type": "REGULAR",
            "settings": settings,
            "regular": expr
        }
        
        try:
            body = run_simulation(session, payload)
            
            alpha_id = body.get("alpha")
            if not alpha_id:
                file_logger.error(f"[{idx}/{len(tasks)}] FAILED: No alpha ID returned. Body: {body}")
                continue
                
            # Fetch the alpha to get the stats
            alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
            resp = session.get(alpha_url)
            alpha_data = resp.json()
            is_stats = alpha_data.get("is", {})
            
            if not is_stats:
                file_logger.error(f"[{idx}/{len(tasks)}] FAILED: IS Stats Missing. Alpha Data: {alpha_data}")
                continue
                
            sharpe = is_stats.get("sharpe", 0)
            fit = is_stats.get("fitness", 0)
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            
            file_logger.info(f"[{idx}/{len(tasks)}] {status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()

