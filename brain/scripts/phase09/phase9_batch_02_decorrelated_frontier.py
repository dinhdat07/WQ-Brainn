import os
import sys
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain1 import sign_in
from brain3 import run_simulation

with open("logs/mutation_optimizer.log", "w") as f:
    f.truncate(0)

logging.basicConfig(filename="logs/mutation_optimizer.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Phase 9 Batch 2 - Decorrelated Institutional Frontier...")
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
        "neutralization": "SUBINDUSTRY",
        "truncation": 0.05,
        "pasteurization": "ON",
        "testPeriod": "P2Y",
        "unitHandling": "VERIFY",
        "nanHandling": "ON",
        "language": "FASTEXPR",
        "visualization": False
    }
    
    tasks = [
        # 1. Sloan Accruals Anomaly: Negative Net Operating Accruals / Assets (Earnings Quality)
        ("P9_2_Sloan_Accruals", 
         "ts_decay_linear(group_rank(-(netinc - ocf) / assets, subindustry), 10)", 
         {}),

        # 2. Cooper Asset Growth Anomaly: Negative Total Asset Expansion
        ("P9_3_Asset_Growth_Anomaly", 
         "ts_decay_linear(group_rank(-ts_delta(assets, 252) / ts_delay(assets, 252), subindustry), 10)", 
         {}),

        # 3. Silver News Bull Trap smoothed with Decay
        ("P9_4_News_Bull_Trap_Decay",
         """
         slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2);
         ts_decay_linear(winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4), 10)
         """,
         {"neutralization": "INDUSTRY"}),

        # 4. Silver PCR Open Interest Triggered IV Spread
        ("P9_5_Silver_PCR_Trigger_Spread",
         "ts_decay_linear(group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry), 10)",
         {}),

        # 5. Analyst Consensus EPS Revision Momentum
        ("P9_6_Analyst_EPS_Revision",
         "ts_decay_linear(group_rank(ts_delta(ts_backfill(est_eps, 60), 20) / (abs(ts_backfill(est_eps, 60)) + 0.01), subindustry), 10)",
         {}),

        # 6. Gross Profitability Margin Expansion x Accrual Quality
        ("P9_7_GPA_Plus_Accrual",
         "ts_decay_linear(group_rank((sales - cogs) / assets, subindustry) + group_rank(-(netinc - ocf) / assets, subindustry), 10)",
         {})
    ]
    
    file_logger.info(f"Total concepts to process in Phase 9 Batch 2: {len(tasks)}")
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}")
        
        settings = base_settings.copy()
        settings.update(overrides)

        payload = {
            "type": "REGULAR",
            "settings": settings,
            "regular": expr.strip()
        }
        
        try:
            body = run_simulation(session, payload)
            alpha_id = body.get("alpha")
            if not alpha_id:
                file_logger.error(f"[{idx}/{len(tasks)}] FAILED. Body: {body}")
                continue
                
            alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
            resp = session.get(alpha_url)
            alpha_data = resp.json()
            is_stats = alpha_data.get("is", {})
                
            sharpe = is_stats.get("sharpe", 0)
            fit = is_stats.get("fitness", 0)
            turnover = is_stats.get("turnover", 0)
            margin = is_stats.get("margin", 0)
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            sim_status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            file_logger.info(f"[{idx}/{len(tasks)}] {sim_status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {turnover} | Margin: {margin}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
