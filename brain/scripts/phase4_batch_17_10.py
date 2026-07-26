import os
import sys
import time
import logging

# Add the parent directory to Python path
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
    file_logger.info("Starting Phase 4 Batch 17 - 10: Mutated Liquidity & Fundamentals (Subindustry Z-Scores)...")
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
        ("17_1_Asset_Turnover_Fast_Reversion", "ts_decay_linear(group_zscore((sales/assets) * rank(-(close/ts_mean(close, 5))), subindustry), 5)", {}),
        ("17_2_PEG_Volume_Spike", "ts_decay_linear(group_zscore((income/close)*ts_delta(income,252) * rank(ts_delta(volume,5)), subindustry), 5)", {}),
        ("17_3_Volume_Surprise_ZScore", "ts_decay_linear(group_zscore(-ts_delta(volume, 5) * sign(returns), subindustry), 5)", {}),
        ("17_4_Liquidity_Trend_Accel", "ts_decay_linear(group_zscore(ts_delta(ts_delta(volume/sharesout, 5), 5), sector), 5)", {}),
        ("17_5_High_Accruals_Short", "ts_decay_linear(group_zscore(-(assets - cash - liabilities), subindustry), 5)", {}),
        ("17_6_Operating_CF_Price_Mom", "ts_decay_linear(group_zscore((cash/assets) * rank(close/ts_mean(close,20)), industry), 5)", {}),
        ("17_7_Asset_vs_Price_Growth", "ts_decay_linear(group_zscore(ts_delta(assets, 63)/assets - ts_delta(close, 63)/close, subindustry), 5)", {}),
        ("17_8_Cap_Weighted_Reversion", "ts_decay_linear(group_zscore(-returns * (close * sharesout), subindustry), 5)", {}),
        ("17_9_Vol_Adj_Reversion_Sub", "ts_decay_linear(group_zscore(-(close / ts_mean(close, 20)) * rank(ts_delta(volume, 5)), subindustry), 5)", {}),
        ("17_10_Amihud_Spike", "ts_decay_linear(group_zscore((abs(returns)/volume) / ts_mean(abs(returns)/volume, 20), subindustry), 5)", {})
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
                
            sharpe = is_stats.get("sharpe", 0)
            fit = is_stats.get("fitness", 0)
            turnover = is_stats.get("turnover", 0)
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            sim_status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            
            file_logger.info(f"[{idx}/{len(tasks)}] {sim_status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {turnover}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
