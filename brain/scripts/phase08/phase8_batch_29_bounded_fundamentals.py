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
    file_logger.info("Starting Phase 8.11 Batch 29 - Bounded Fundamentals (Fix Outlier Concentration)...")
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
        "truncation": 0.03,  # Set strict 3% truncation
        "pasteurization": "ON",
        "testPeriod": "P2Y",
        "unitHandling": "VERIFY",
        "nanHandling": "ON",
        "language": "FASTEXPR",
        "visualization": False
    }
    
    vol_arb = "rank(implied_volatility_call_120 / parkinson_volatility_120)"
    
    tasks = [
        # 1. Rank(Fundamental) * Rank(VolArb)
        ("29_1_RankFund_RankVol", f"ts_decay_linear(rank(rank(sales / assets) * {vol_arb}), 5)", {}),
        # 2. GroupRank(Fundamental) * Rank(VolArb)
        ("29_2_GroupRankFund_RankVol", f"ts_decay_linear(rank(group_rank(sales / assets, subindustry) * {vol_arb}), 5)", {}),
        # 3. Additive bounded: group_rank(fund) + rank(vol_arb)
        ("29_3_Add_Bounded", f"ts_decay_linear(group_rank(sales / assets, subindustry) + {vol_arb}, 5)", {}),
        # 4. GPA Bounded: group_rank(GPA) * Rank(VolArb)
        ("29_4_GPA_Bounded", f"ts_decay_linear(rank(group_rank((sales - cogs) / assets, subindustry) * {vol_arb}), 5)", {}),
        # 5. ZScore + Clip before multiply
        ("29_5_ZScoreClip_Vol", f"ts_decay_linear(rank(group_zscore(sales / assets, subindustry) * {vol_arb}), 5)", {"truncation": 0.02}),
        # 6. Rank Fund * Rank Vol with decay 10
        ("29_6_RankFund_RankVol_D10", f"ts_decay_linear(rank(group_rank(sales / assets, subindustry) * {vol_arb}), 10)", {})
    ]
    
    file_logger.info(f"Total concepts to process: {len(tasks)}")
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}: {expr} with overrides {overrides}")
        
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
