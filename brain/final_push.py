import os
import json
import time
import logging
from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="final_push.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
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

    formulas = [
        # Base (Sharpe 1.22, Fit 0.98)
        "ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 20)",
        
        # Add ts_decay_linear on the outside (should increase fit, might lower/raise sharpe)
        "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 20), 2)",
        "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 20), 3)",
        "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 20), 5)",
        
        # Change inner decay (more inner smoothing)
        "ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 8), 20)",
        "ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 10), 20)",
        
        # Combine both
        "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 8), 20), 3)",
        
        # Try rank instead of group_rank on the fundamental
        "ts_zscore(ts_decay_linear(rank(ts_rank(fnd6_cptmfmq_oibdpq, 60)) * ts_rank(-ts_delta(close, 5), 5), 5), 20)",
        "ts_decay_linear(ts_zscore(ts_decay_linear(rank(ts_rank(fnd6_cptmfmq_oibdpq, 60)) * ts_rank(-ts_delta(close, 5), 5), 5), 20), 3)",
        
        # Sector neutralization instead of subindustry (in settings) -> wait, settings is already SUBINDUSTRY
        # The base formula uses group_rank(..., sector). What if we use group_rank(..., industry)
        "ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), industry) * ts_rank(-ts_delta(close, 5), 5), 5), 20)",
        
        # Change z-score window
        "ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 40)",
        "ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 60)",
        "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(fnd6_cptmfmq_oibdpq, 60), sector) * ts_rank(-ts_delta(close, 5), 5), 5), 40), 3)"
    ]

    total = len(formulas)
    for i, expr in enumerate(formulas, 1):
        file_logger.info(f"[{i}/{total}] Submitting: {expr}")
        payload = {"type": "REGULAR", "settings": settings, "regular": expr}
        try:
            result = run_simulation(session, payload)
            alpha_id = result.get("alpha") if result else None
            if alpha_id:
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
        except Exception as e:
            file_logger.error(f"[{i}/{total}] EXCEPTION: {e}")

if __name__ == "__main__":
    main()
