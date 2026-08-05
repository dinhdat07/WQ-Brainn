import sys
import json
import time
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)
    
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

    # Replace correlation with ts_corr
    alphas = {
        "Phase12_Batch09_A6_IVSkew": "-(ts_decay_linear(ts_corr(close, volume, 60) * group_zscore(ts_backfill(implied_volatility_put_60 - implied_volatility_call_60, 60), subindustry), 80))"
    }
    
    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_09_results.json', 'r') as f:
        results = json.load(f)
    
    for name, expr in alphas.items():
        print(f"Submitting {name}...")
        data = {
            "type": "REGULAR",
            "settings": settings,
            "regular": expr
        }
        
        url = "https://api.worldquantbrain.com/simulations"
        
        retries = 3
        while retries > 0:
            resp = session.post(url, json=data)
            if resp.status_code == 201:
                sim_id = resp.headers.get("Location", "").split("/")[-1]
                print(f"-> Submitted successfully. ID: {sim_id}")
                results[name] = {"id": sim_id, "status": "simulating"}
                break
            elif resp.status_code == 429:
                print("-> 429 Too Many Requests. Retrying in 30 seconds...")
                time.sleep(30)
                retries -= 1
            else:
                print(f"-> Error {resp.status_code}: {resp.text}")
                results[name] = {"id": None, "status": f"ERROR_{resp.status_code}"}
                break
        
        time.sleep(3)
        
    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_09_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
