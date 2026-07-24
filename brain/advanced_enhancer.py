import sys
import logging
import json
from typing import Dict, Any

from brain1 import sign_in
from brain3 import run_simulation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting ADVANCED ENHANCER Alpha Generator")
    sess, _ = sign_in('brain_credentials.txt')
    
    formulas = []
    
    # Fundamental Variables that performed well
    fundamental_vars = [
        "fnd6_cptmfmq_oibdpq",
        "assets",
        "actual_sales_value_quarterly"
    ]
    
    # We found that ts_decay_linear(group_rank(...) * ts_rank(-ts_delta(close, D1), D2), D3) got Sharpe ~1.04
    # Let's wrap this in rank() or ts_zscore() and try multiple combinations.
    
    for var in fundamental_vars:
        for d1 in [3, 5]:
            for d2 in [5, 10]:
                for d3 in [3, 5]:
                    base_expr_sector = f"ts_decay_linear(group_rank(ts_rank({var}, 60), sector) * ts_rank(-ts_delta(close, {d1}), {d2}), {d3})"
                    base_expr_sub = f"ts_decay_linear(group_rank(ts_rank({var}, 60), subindustry) * ts_rank(-ts_delta(close, {d1}), {d2}), {d3})"
                    
                    formulas.append(f"rank({base_expr_sector})")
                    formulas.append(f"ts_zscore({base_expr_sector}, 20)")
                    
                    formulas.append(f"rank({base_expr_sub})")
                    formulas.append(f"ts_zscore({base_expr_sub}, 20)")

    total = len(formulas)
    logger.info(f"Generated {total} advanced formulas. Executing batch...")
    
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
            result = run_simulation(sess, payload)
            alpha_id = result.get("alpha") if result else None
            if alpha_id:
                # Fetch stats
                resp = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
                if resp.status_code == 200:
                    data = resp.json()
                    sharpe = data.get("is", {}).get("sharpe")
                    fitness = data.get("is", {}).get("fitness")
                    turnover = data.get("is", {}).get("turnover")
                    
                    try:
                        sharpe_val = float(sharpe) if sharpe is not None else 0.0
                        fitness_val = float(fitness) if fitness is not None else 0.0
                    except ValueError:
                        sharpe_val, fitness_val = 0.0, 0.0

                    if sharpe_val > 1.25 and fitness_val > 1.0:
                        logger.info(f"[{i}/{total}] => ⭐ SUPER ALPHA ⭐ ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness} | TO: {turnover}")
                    else:
                        logger.info(f"[{i}/{total}] => SUCCESS (Rejected by Filter) ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                        
                    results_summary.append((alpha_id, sharpe_val, fitness_val, turnover, expr))
                else:
                    logger.info(f"[{i}/{total}] => SUCCESS! ID: {alpha_id} (Stats unavail)")
            else:
                error_msg = result.get('message', 'Unknown error') if result else 'No result returned'
                logger.error(f"[{i}/{total}] => ERROR / REJECTED: {error_msg}")
        except Exception as e:
            logger.error(f"[{i}/{total}] => EXCEPTION: {e}")

    logger.info("=== BATCH COMPLETE ===")
    logger.info("🔥 TOP SUBMITTABLE ADVANCED ALPHAS (Sharpe > 1.25 & Fitness > 1.0) 🔥")
    
    results_summary.sort(key=lambda x: x[2], reverse=True)
    count = 0
    for res in results_summary:
        if res[1] > 1.25 and res[2] > 1.0:
            logger.info(f"✅ ID: {res[0]} | Sharpe: {res[1]} | Fit: {res[2]} | TO: {res[3]}")
            logger.info(f"   Formula: {res[4]}")
            count += 1
            
    if count == 0:
        logger.info("No alphas passed the strict submittable filter. Try different parameters or logic.")
        logger.info("Next best alphas:")
        for res in results_summary[:3]:
            logger.info(f"ID: {res[0]} | Sharpe: {res[1]} | Fit: {res[2]} | TO: {res[3]}")

if __name__ == "__main__":
    main()
