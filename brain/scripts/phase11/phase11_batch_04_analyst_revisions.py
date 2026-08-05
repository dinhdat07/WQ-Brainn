import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_analyst_alphas():
    alphas = []
    
    # 1. Sales Revision
    alphas.append({
        "name": "Analyst_Sales_Rev60",
        "regular": "ts_decay_linear(group_rank(ts_delta(est_sales, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. EPS Revision
    alphas.append({
        "name": "Analyst_EPS_Rev60",
        "regular": "ts_decay_linear(group_rank(ts_delta(est_eps, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 3. EBITDA Revision
    alphas.append({
        "name": "Analyst_EBITDA_Rev60",
        "regular": "ts_decay_linear(group_rank(ts_delta(est_ebitda, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 4. FCF Revision
    alphas.append({
        "name": "Analyst_FCF_Rev60",
        "regular": "ts_decay_linear(group_rank(ts_delta(est_fcf, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 5. Composite Revision
    alphas.append({
        "name": "Analyst_Composite_Rev",
        "regular": "ts_decay_linear(group_rank(ts_delta(est_sales, 60), subindustry) + group_rank(ts_delta(est_eps, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)

    alphas = generate_analyst_alphas()
    
    simulation_data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": ""
    }

    results = []
    for alpha in alphas:
        print(f"\nSimulating: {alpha['name']}")
        sim_payload = simulation_data.copy()
        sim_payload["regular"] = alpha["regular"]
        
        retries = 3
        while retries > 0:
            try:
                sim_result = brain1.run_simulation(session, sim_payload)
                sim_id = sim_result.get("simulation") or sim_result.get("id")
                if sim_id:
                    print(f"Started simulation: {sim_id}")
                    results.append({
                        "name": alpha["name"],
                        "id": sim_id,
                        "formula": alpha["regular"],
                        "settings": sim_payload["settings"]
                    })
                    break
            except Exception as e:
                err = str(e)
                print(f"Error simulating {alpha['name']}: {err}")
                if "CONCURRENT_SIMULATION_LIMIT" in err:
                    time.sleep(30)
                    retries -= 1
                else:
                    break
        time.sleep(2)

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_analyst_revisions_pending.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
