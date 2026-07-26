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
    file_logger.info("Starting Phase 4 Batch 16 - 10: Orthogonal Liquidity & Accruals...")
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
        # Liquidity / Turnover
        ("16_1_Amihud_Illiquidity", "ts_decay_linear(group_rank(ts_mean(abs(returns) / volume, 20), sector), 5)", {}),
        ("16_2_Turnover_Value", "ts_decay_linear(group_rank(1 / ts_mean(sharesout / volume, 20), industry), 5)", {}),
        ("16_3_Volume_Surprise", "ts_decay_linear(rank(-ts_delta(volume, 5) * sign(returns)), 5)", {}),
        ("16_4_Vol_Adj_Reversion", "ts_decay_linear(rank(-(close / ts_mean(close, 20)) * rank(ts_delta(volume, 5))), 5)", {}),
        ("16_5_Liquidity_Trend", "ts_decay_linear(group_rank(ts_delta(volume / sharesout, 10), sector), 5)", {}),
        
        # Advanced Fundamentals (Accruals, Working Capital, ROE, PEG)
        ("16_6_Low_Accruals", "ts_decay_linear(group_rank(-(assets - cash - liabilities), sector), 5)", {}),
        ("16_7_Working_Capital_Ratio", "ts_decay_linear(group_rank(-((assets - cash) / assets), industry), 5)", {}),
        ("16_8_ROE_Quality_Rank", "ts_decay_linear(group_zscore(ts_zscore(income / equity, 63), subindustry), 5)", {}),
        ("16_9_PEG_Yield", "ts_decay_linear(group_rank((income / close) * ts_delta(income, 252), sector), 5)", {}),
        ("16_10_Asset_Turnover", "ts_decay_linear(group_rank(sales / assets, industry), 5)", {})
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
            
            # Record results
            results = locals().get("results", []) # to avoid undefined var if results not initialized globally
            # Actually wait, results is not defined in the main block.
            # I can just log it since we can parse the log later.
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
