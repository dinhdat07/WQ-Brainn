import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_sent_mom_alphas():
    alphas = []
    
    # 1. Sentiment Trend (Slope)
    # Buy stocks where sentiment is increasing over the last 20 days
    alphas.append({
        "name": "Sent_Slope_20",
        "regular": "ts_decay_linear(ts_regression(snt_social_value, ts_step(1), 20, rettype = 2), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. Sentiment Momentum vs Price Momentum
    # Buy if sentiment is high AND price momentum is high
    alphas.append({
        "name": "Sent_Price_Mom",
        "regular": "group_rank(snt_social_value, subindustry) * group_rank(ts_mean(returns, 120), subindustry)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 3. Sentiment Breakout
    # Buy if sentiment today is much higher than 20-day average
    alphas.append({
        "name": "Sent_Breakout",
        "regular": "ts_decay_linear(snt_social_value - ts_mean(snt_social_value, 20), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)

    alphas = generate_sent_mom_alphas()
    
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
        except Exception as e:
            print(f"Error simulating {alpha['name']}: {e}")
        time.sleep(2)

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_sent_mom_pending.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
