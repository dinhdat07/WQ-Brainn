import os
import time
import logging
import sys
from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="mutation_enhancer.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Mutation Enhancer...")
    session, _ = sign_in('brain_credentials.txt')
    if not session:
        print("Auth failed")
        return

    # Base settings
    base_settings = {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "truncation": 0.08,
        "pasteurization": "ON",
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False,
    }

    cores = {
        "EV_CF": "group_rank(-ts_zscore(enterprise_value/cashflow, 120), subindustry)",
        "Volatility": "rank(ts_backfill(implied_volatility_call_10, 5) / ts_backfill(parkinson_volatility_10, 5))"
    }

    mutations = [
        {
            "name": "1A_Percent_Return",
            "template": "ts_decay_linear(ts_zscore(ts_decay_linear({core} * (-ts_delta(close, 5)/close), 3), 30), 5)",
            "neutralization": "NONE"
        },
        {
            "name": "1B_Medium_Return",
            "template": "ts_decay_linear(ts_zscore(ts_decay_linear({core} * ts_rank(-returns, 10), 3), 30), 5)",
            "neutralization": "NONE"
        },
        {
            "name": "2_Pure_Fundamental",
            "template": "ts_decay_linear(ts_zscore(ts_mean({core}, 5), 20), 10)",
            "neutralization": "NONE"
        },
        {
            "name": "3_Brain_Neutralization",
            "template": "ts_decay_linear({core} * ts_rank(-ts_delta(close, 5), 10), 6)",
            "neutralization": "INDUSTRY"
        }
    ]

    tasks = []
    for core_name, core_expr in cores.items():
        for mut in mutations:
            expr = mut["template"].replace("{core}", core_expr)
            tasks.append({
                "name": f"{core_name}_{mut['name']}",
                "expr": expr,
                "neut": mut["neutralization"]
            })

    total = len(tasks)
    file_logger.info(f"Total mutations to process: {total}")
    
    for i, t in enumerate(tasks, 1):
        # We only want to run the pending ones. But let's just run them all for now, or just the remaining ones.
        # Wait, since I'm running from scratch, I'll let it just run all. Wait, if it runs all, it will take 15 mins.
        # Let's just modify the tasks array directly to skip the first two.
        pass
    
    # Filter to only run tasks we haven't succeeded on:
    tasks = tasks[2:] # Skip the first two since we already know the results of EV_CF_1A and EV_CF_1B
    total = len(tasks)
    
    for i, t in enumerate(tasks, 1):
        file_logger.info(f"[{i}/{total}] Submitting {t['name']}: {t['expr']} (Neut: {t['neut']})")
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
