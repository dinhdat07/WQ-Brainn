import os
import time
import logging
import sys

# Add parent directory to path so we can import brain1 and brain3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="logs/orthogonal_generator.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Orthogonal Generator...")
    session, _ = sign_in('brain_credentials.txt')
    if not session:
        print("Auth failed")
        return

    # Base settings for these new orthogonal models
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

    # The 4 strictly orthogonal concepts
    tasks = [
        {
            "name": "1_News_Sentiment_Momentum",
            "expr": "ts_decay_linear(group_rank(ts_sum(mean_composite_sentiment_score, 20), subindustry), 10)",
            "neut": "NONE"
        },
        {
            "name": "1B_News_Sentiment_Contrarian",
            "expr": "ts_decay_linear(group_rank(-ts_sum(mean_composite_sentiment_score, 20), subindustry), 10)",
            "neut": "NONE"
        },
        {
            "name": "2_Options_Fear_Reversion",
            "expr": "ts_decay_linear(group_rank(ts_delta(pcr_vol_10, 5), subindustry), 10)",
            "neut": "NONE"
        },
        {
            "name": "3_Analyst_EBIT_Revisions",
            "expr": "ts_decay_linear(group_rank(ts_delta(anl4_fs_detail_estimate_1qf_v4_nd_ebit_mean, 20), subindustry), 10)",
            "neut": "NONE"
        },
        {
            "name": "4_Volume_Exhaustion_Reversion",
            "expr": "ts_decay_linear(group_rank(ts_delta(volume, 5) * -ts_delta(close, 2), subindustry), 5)",
            "neut": "NONE"
        }
    ]

    total = len(tasks)
    file_logger.info(f"Total orthogonal concepts to process: {total}")
    
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
