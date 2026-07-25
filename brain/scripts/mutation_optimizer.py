import os
import time
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="logs/mutation_optimizer.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Mutation Optimizer...")
    session, _ = sign_in('brain_credentials.txt')
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
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False,
    }

    # Batch 4: Structural Mutations to Break ZYKo6R78 Correlation
    # We completely abandon the `ts_decay(ts_zscore(ts_decay(A*B, 3), 30), 8)` framework.
    tasks = [
        # 1. Additive Model (Assets + Intraday Reversion)
        {
            "name": "1_Additive_Assets",
            "expr": "ts_decay_linear(group_rank(ts_rank(assets, 60), subindustry) + ts_rank(-(close/open - 1), 5), 8)",
            "neut": "NONE"
        },
        # 2. Conditional Regime (Valuation EV/CF)
        {
            "name": "2_Conditional_EV_CF",
            "expr": "ts_decay_linear(group_rank(-ts_zscore(enterprise_value/cashflow, 63), subindustry) > 0.5 ? ts_rank(-(close/open - 1), 5) : 0, 8)",
            "neut": "NONE"
        },
        # 3. Simple Multiplication without Inner Zscore/Decay (Sales)
        {
            "name": "3_Simple_Mult_Sales",
            "expr": "ts_decay_linear(group_rank(ts_rank(sales, 60), subindustry) * ts_rank(-(close/open - 1), 5), 10)",
            "neut": "NONE"
        },
        # 4. Volatility-Adjusted Reversion (Amihud)
        {
            "name": "4_VolAdjusted_Amihud",
            "expr": "ts_decay_linear(group_rank(ts_rank(abs(returns) / volume, 60), subindustry) / (1 + ts_std_dev(returns, 20)), 8)",
            "neut": "NONE"
        },
        # 5. Analyst Estimate + Momentum (Additive)
        {
            "name": "5_Additive_Analyst_Corr",
            "expr": "ts_decay_linear(group_rank(-ts_corr(est_ptp, est_fcf, 252), subindustry) + ts_rank(-returns, 10), 8)",
            "neut": "NONE"
        }
    ]

    total = len(tasks)
    file_logger.info(f"Total concepts to process: {total}")
    
    for i, t in enumerate(tasks, 1):
        file_logger.info(f"[{i}/{total}] Submitting {t['name']}: {t['expr']}")
        settings = dict(base_settings)
        settings["neutralization"] = t["neut"]
        
        payload = {"type": "REGULAR", "settings": settings, "regular": t["expr"]}
        
        while True:
            try:
                result = run_simulation(session, payload)
                if result and result.get("status") == "ERROR":
                    file_logger.error(f"[{i}/{total}] SIMULATION ERROR: {result.get('message')}")
                    break
                    
                alpha_id = result.get("alpha") if result else None
                if alpha_id:
                    time.sleep(3)
                    resp = session.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
                    if resp.status_code == 200:
                        stats = resp.json().get('is', {})
                        if stats:
                            sharpe = round(float(stats.get('sharpe', 0)), 2)
                            fitness = round(float(stats.get('fitness', 0)), 2)
                            if sharpe > 1.25 and fitness > 1.0:
                                file_logger.info(f"[{i}/{total}] \U0001f680 SUBMITTABLE! ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                            else:
                                file_logger.info(f"[{i}/{total}] SUCCESS (Rejected) ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                break
            except Exception as e:
                err_msg = str(e)
                if '429' in err_msg or 'Too Many Requests' in err_msg:
                    file_logger.warning(f"[Run] Hit concurrency limit 429. Sleeping 15s...")
                    time.sleep(15)
                else:
                    file_logger.error(f"[{i}/{total}] EXCEPTION: {e}")
                    break

if __name__ == "__main__":
    main()
