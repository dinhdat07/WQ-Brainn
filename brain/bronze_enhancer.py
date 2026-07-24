import os
import time
import logging
import sys
import sys
from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="bronze_enhancer.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Bronze Alpha Enhancer...")
    session, _ = sign_in('brain_credentials.txt')
    if not session:
        print("Auth failed")
        return

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

    windows = [20, 60, 90, 120, 252]
    formulas = []
    
    # 1. Valuation based on cash flow (EV / CF)
    # Note: actual_cashflow_per_share_value_quarterly * sharesout might be needed, 
    # but cashflow is an annual field. Let's use cashflow.
    for w in [60, 90, 120]:
        expr = f"ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(-ts_zscore(enterprise_value/cashflow, {w}), subindustry) * ts_rank(-ts_delta(close, 3), 5), 3), 30), 5)"
        formulas.append(expr)

    # 2. Overpriced stocks (Analyst estimates)
    for w in [20, 60, 90, 120]:
        expr = f"ts_decay_linear(ts_zscore(ts_decay_linear(-ts_corr(est_ptp, est_fcf, {w}) * ts_rank(-ts_delta(close, 3), 5), 3), 30), 5)"
        formulas.append(expr)

    # 3. Volatility arbitrage (IV / Historical Volatility)
    for w in [10, 20, 60, 120]:
        # Using implied_volatility_call_120 and parkinson_volatility_120 as base fields
        # but applying a backfill to fix NaNs.
        expr = f"ts_decay_linear(ts_zscore(ts_decay_linear(rank(ts_backfill(implied_volatility_call_{w}, 5) / ts_backfill(parkinson_volatility_{w}, 5)) * ts_rank(-ts_delta(close, 3), 5), 3), 30), 5)"
        formulas.append(expr)

    total = len(formulas)
    file_logger.info(f"Total formulas to process: {total}")
    
    for i, expr in enumerate(formulas, 1):
        file_logger.info(f"[{i}/{total}] Submitting: {expr}")
        payload = {"type": "REGULAR", "settings": settings, "regular": expr}
        
        while True:
            try:
                result = run_simulation(session, payload)
                alpha_id = result.get("alpha") if result else None
                if alpha_id:
                    # Give server time to compute stats before fetching
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
