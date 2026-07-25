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
    file_logger.info("Starting Phase 3 Batch 14 - 10: Matrix Alternative Data...")
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
        ("14_1_Options_Vol_Arb_Pure", "group_rank(implied_volatility_call_120 / parkinson_volatility_120, sector)", {"truncation": 0.05}),
        ("14_2_Options_Vol_Spread", "ts_decay_linear(rank(implied_volatility_call_120 - implied_volatility_put_120), 5)", {}),
        ("14_3_Sentiment_Momentum", "ts_decay_linear(rank(ts_delta(mean_composite_sentiment_score, 10)), 5)", {}),
        ("14_4_Sentiment_Reversal", "ts_decay_linear(rank(-ts_corr(open, mean_composite_sentiment_score, 10)), 5)", {}),
        ("14_5_Target_Price_Premium", "ts_decay_linear(rank(est_ptp / close), 5)", {}),
        ("14_6_Target_Price_Revision", "ts_decay_linear(rank(ts_delta(est_ptp, 20)), 5)", {}),
        ("14_7_EPS_Revision", "ts_decay_linear(rank(ts_delta(anl4_afv4_eps_mean, 20)), 5)", {}),
        ("14_8_Normalized_EPS_Revision", "ts_decay_linear(rank(ts_delta(anl4_afv4_eps_mean / close, 10)), 5)", {}),
        ("14_9_Options_PutCall_Volume", "ts_decay_linear(rank(pcr_vol_10), 5)", {}),
        ("14_10_EPS_vs_Price_Divergence", "ts_decay_linear(rank(-ts_corr(close, anl4_afv4_eps_mean, 20)), 5)", {})
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
