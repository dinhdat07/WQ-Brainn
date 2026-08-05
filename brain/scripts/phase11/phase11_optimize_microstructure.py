import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_microstructure_alphas():
    alphas = []
    
    # 1. Alpha 41 variant
    alphas.append({
        "name": "Micro_A41_HL_VWAP",
        "regular": "ts_decay_linear(rank((high * low)^0.5 - vwap), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. Alpha 101 variant
    alphas.append({
        "name": "Micro_A101_IntradayMom",
        "regular": "ts_decay_linear(rank(-1 * (close - open) / ((high - low) + 0.001)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 3. Alpha 42 variant
    alphas.append({
        "name": "Micro_A42_VWAP_Close",
        "regular": "ts_decay_linear(rank(vwap - close), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 4. Alpha 12 variant
    alphas.append({
        "name": "Micro_A12_Price_Volume",
        "regular": "ts_decay_linear(rank(sign(delta(volume, 1)) * -1 * delta(close, 1)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 5. Alpha 53 variant (CLV)
    alphas.append({
        "name": "Micro_A53_CLV",
        "regular": "ts_decay_linear(rank(-1 * ((close - low) - (high - close)) / ((high - low) + 0.001)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 6. Alpha 60 variant (Volume-weighted CLV)
    alphas.append({
        "name": "Micro_A60_Volume_CLV",
        "regular": "ts_decay_linear(rank(-1 * (((close - low) - (high - close)) / ((high - low) + 0.001)) * volume), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_microstructure_alphas()
    print(f"Generated {len(alphas)} Microstructure Alphas to simulate.")

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

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_microstructure_pending.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("All submitted successfully.")

if __name__ == "__main__":
    main()
