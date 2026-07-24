import os
import json
import time
import re
import logging
from brain1 import sign_in
from brain3 import run_simulation

# Configure logging
logging.basicConfig(filename="ultimate_enhancer.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    session, _ = sign_in('brain_credentials.txt')
    if not session:
        logger.error("Authentication failed. Exiting.")
        return

    # Let's combine the best performing fundamental data with zscore
    fundamental_fields = [
        "actual_cashflow_per_share_value_quarterly"
    ]
    
    price_windows = [
        ("3", "5"),
        ("5", "5"),
        ("5", "10")
    ]
    
    decays = ["3", "5"]
    zscore_windows = ["20", "30"]
    group_fields = ["subindustry", "sector"]
    
    formulas = []
    
    # Base combo: ts_zscore around rank
    for field in fundamental_fields:
        for p1, p2 in price_windows:
            for d in decays:
                for grp in group_fields:
                    for z in zscore_windows:
                        # Variant 1: Pure Zscore around fundamental * momentum
                        formulas.append(
                            f"ts_zscore(ts_decay_linear(group_rank(ts_rank(ts_delta({field}, 60), 60), {grp}) * ts_rank(-ts_delta(close, {p1}), {p2}), {d}), {z})"
                        )
                        # Variant 2: Add extra decay outside Zscore to reduce turnover
                        formulas.append(
                            f"ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(ts_delta({field}, 60), 60), {grp}) * ts_rank(-ts_delta(close, {p1}), {p2}), {d}), {z}), 3)"
                        )
    
    total = len(formulas)
    logger.info(f"Generated {total} ULTIMATE combinations.")

    settings = {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "neutralization": "NONE",
        "truncation": 0.08,
        "pasteurization": "ON",
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False,
    }

    results_summary = []

    for i, expr in enumerate(formulas, 1):
        logger.info(f"[{i}/{total}] Submitting: {expr}")
        payload = {"type": "REGULAR", "settings": settings, "regular": expr}
        
        try:
            result = run_simulation(session, payload)
            alpha_id = result.get("alpha") if result else None
            
            if alpha_id:
                # Fetch stats
                resp = session.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
                if resp.status_code == 200:
                    alpha_data = resp.json()
                    stats = alpha_data.get('is', {})
                    if stats:
                        sharpe_val = float(stats.get('sharpe', 0))
                        fitness_val = float(stats.get('fitness', 0))
                        turnover = float(stats.get('turnover', 0))
                        
                        sharpe = round(sharpe_val, 2)
                        fitness = round(fitness_val, 2)
                        
                        if sharpe > 1.25 and fitness > 1.0:
                            logger.info(f"[{i}/{total}] => \U0001f680 SUBMITTABLE! ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                        else:
                            logger.info(f"[{i}/{total}] => SUCCESS (Rejected by Filter) ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                            
                        results_summary.append((alpha_id, sharpe_val, fitness_val, turnover, expr))
                    else:
                        logger.info(f"[{i}/{total}] => SUCCESS! ID: {alpha_id} (Stats unavail)")
                else:
                    logger.info(f"[{i}/{total}] => SUCCESS! ID: {alpha_id} (Failed to fetch stats)")
            else:
                error_msg = result.get('message', 'Unknown error') if result else 'No result returned'
                logger.error(f"[{i}/{total}] => ERROR / REJECTED: {error_msg}")
        except Exception as e:
            logger.error(f"[{i}/{total}] => EXCEPTION: {e}")

    logger.info("=== BATCH COMPLETE ===")
    logger.info("🔥 TOP SUBMITTABLE ULTIMATE ALPHAS (Sharpe > 1.25 & Fitness > 1.0) 🔥")
    
    results_summary.sort(key=lambda x: x[1], reverse=True)  # Sort by Sharpe this time
    count = 0
    for res in results_summary:
        if res[1] > 1.25 and res[2] > 1.0:
            logger.info(f"✅ ID: {res[0]} | Sharpe: {res[1]} | Fit: {res[2]} | TO: {res[3]}")
            logger.info(f"   Formula: {res[4]}")
            count += 1
            
    if count == 0:
        logger.info("No alphas passed the strict submittable filter. Try different parameters or logic.")
        logger.info("Next best alphas (by Sharpe):")
        for res in results_summary[:5]:
            logger.info(f"ID: {res[0]} | Sharpe: {res[1]} | Fit: {res[2]} | TO: {res[3]}")

if __name__ == "__main__":
    main()
