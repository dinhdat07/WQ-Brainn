import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_smooth_alphas():
    alphas = []
    
    # 1. Mean 10
    alphas.append({
        "name": "V_Mean10",
        "regular": "ts_mean(rank(-returns / ts_std_dev(returns, 10)) * rank(ts_backfill(snt_social_value, 30)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. Mean 20
    alphas.append({
        "name": "V_Mean20",
        "regular": "ts_mean(rank(-returns / ts_std_dev(returns, 10)) * rank(ts_backfill(snt_social_value, 30)), 20)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 3. Decay 20
    alphas.append({
        "name": "V_Decay20",
        "regular": "ts_decay_linear(rank(-returns / ts_std_dev(returns, 10)) * rank(ts_backfill(snt_social_value, 30)), 20)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 4. Smooth Returns 3 + Decay 5
    alphas.append({
        "name": "V_SmoothRet3",
        "regular": "ts_decay_linear(rank(ts_mean(-returns / ts_std_dev(returns, 10), 3)) * rank(ts_backfill(snt_social_value, 30)), 5)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 5. Smooth Returns 5 + Decay 10
    alphas.append({
        "name": "V_SmoothRet5_Decay10",
        "regular": "ts_decay_linear(rank(ts_mean(-returns / ts_std_dev(returns, 10), 5)) * rank(ts_backfill(snt_social_value, 30)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_smooth_alphas()
    print(f"Generated {len(alphas)} Smooth Alphas to simulate.")

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
        sim_payload["settings"] = {**simulation_data["settings"], **alpha["settings"]}
        
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
                        "settings": sim_payload["settings"],
                        "sim_result": sim_result
                    })
                    break
                else:
                    print(f"Failed to start simulation for {alpha['name']}")
                    print(sim_result)
                    break
            except Exception as e:
                err = str(e)
                print(f"Error simulating {alpha['name']}: {err}")
                if "CONCURRENT_SIMULATION_LIMIT_EXCEEDED" in err:
                    print("Concurrent limit hit! Waiting 30s to retry...")
                    time.sleep(30)
                    retries -= 1
                else:
                    break
            
        time.sleep(2)

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_smooth_pending.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("All submitted successfully.")

if __name__ == "__main__":
    main()
