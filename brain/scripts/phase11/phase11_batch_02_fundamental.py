import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_fund_alphas():
    alphas = []
    
    # 1. Fundamental Quality (ROA) + Momentum
    # Buy companies with high ROA and positive momentum
    alphas.append({
        "name": "Fund_ROA_Mom",
        "regular": "rank(net_income / assets) * rank(ts_step(120))", # Wait ts_step is not momentum. ts_mean(returns, 120) is momentum
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # Let's fix that:
    alphas.append({
        "name": "Fund_Quality_Mom",
        "regular": "rank(operating_income / assets) * rank(ts_mean(returns, 252))",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. Pure Fundamental Value: Earnings Yield
    alphas.append({
        "name": "Fund_Value_EY",
        "regular": "rank(net_income / market_cap)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 3. Fundamental Growth
    alphas.append({
        "name": "Fund_Growth_Sales",
        "regular": "rank(sales / ts_delay(sales, 252))",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_fund_alphas()
    print(f"Generated {len(alphas)} Fundamental Alphas to simulate.")

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
            else:
                print(f"Failed to start simulation for {alpha['name']}")
                print(sim_result)
        except Exception as e:
            print(f"Error simulating {alpha['name']}: {e}")
            
        time.sleep(2)

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_fund_pending.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
