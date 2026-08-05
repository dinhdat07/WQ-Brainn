import sys
import json
import time
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)

    # 1. Check LLGevNeL stats
    print("Checking Alpha LLGevNeL (A6):")
    resp = session.get("https://api.worldquantbrain.com/alphas/LLGevNeL")
    if resp.status_code == 200:
        data = resp.json()
        sharpe = data.get("is", {}).get("sharpe", 0)
        fitness = data.get("is", {}).get("fitness", 0)
        turnover = data.get("is", {}).get("turnover", 0)
        print(f"  Sharpe: {sharpe}, Fitness: {fitness}, Turnover: {turnover}")
    else:
        print(f"  Error: {resp.status_code}")

    # 2. Check JjGlAnZW (A41) stats
    print("Checking Alpha JjGlAnZW (A41):")
    resp = session.get("https://api.worldquantbrain.com/alphas/JjGlAnZW")
    if resp.status_code == 200:
        data = resp.json()
        sharpe = data.get("is", {}).get("sharpe", 0)
        fitness = data.get("is", {}).get("fitness", 0)
        turnover = data.get("is", {}).get("turnover", 0)
        print(f"  Sharpe: {sharpe}, Fitness: {fitness}, Turnover: {turnover}")

    # 3. Resubmit A54
    settings = {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "neutralization": "MARKET",
        "truncation": 0.08,
        "pasteurization": "ON",
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "maxTrade": "OFF",
        "maxPosition": "OFF",
        "language": "FASTEXPR",
        "visualization": False
    }

    alphas = {
        "Phase12_Batch09_A54_VRP": "-(ts_decay_linear(ts_mean((-1 * (low - close) / (low - high + (close * 0.0001))) * ((open / close)^5), 20) * group_rank(ts_backfill(implied_volatility_mean_60, 60) / parkinson_volatility_60, subindustry), 80))"
    }

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_09_results.json', 'r') as f:
        results = json.load(f)

    for name, expr in alphas.items():
        print(f"\nSubmitting {name}...")
        data = {
            "type": "REGULAR",
            "settings": settings,
            "regular": expr
        }
        
        url = "https://api.worldquantbrain.com/simulations"
        resp = session.post(url, json=data)
        if resp.status_code == 201:
            sim_id = resp.headers.get("Location", "").split("/")[-1]
            print(f"-> Submitted successfully. ID: {sim_id}")
            results[name] = {"id": sim_id, "status": "simulating"}
        else:
            print(f"-> Error {resp.status_code}: {resp.text}")

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_09_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
