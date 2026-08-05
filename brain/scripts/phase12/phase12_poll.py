import os
import sys
import json
import time
import requests

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)

    pending_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_01_pending.json'
    
    if not os.path.exists(pending_file):
        print(f"No pending file found at {pending_file}")
        return

    with open(pending_file, 'r') as f:
        pending_alphas = json.load(f)

    print(f"Polling {len(pending_alphas)} alphas...")

    completed = []
    
    while pending_alphas:
        remaining = []
        for alpha in pending_alphas:
            progress_url = alpha.get("progress_url")
            if not progress_url:
                print(f"[{alpha['name']}] Missing progress_url.")
                continue
                
            try:
                r = session.get(progress_url, timeout=30)
                try:
                    res = r.json()
                except:
                    res = {}
                
                status = str(res.get("status") or res.get("state") or "").upper()
                
                if status in ["ERROR", "FAILED"]:
                    print(f"[{alpha['name']}] FAILED: {res}")
                elif status in ["COMPLETED", "WARNING", "DONE", "COMPLETE"] or (r.status_code == 200 and ("alpha" in res or "result" in res)):
                    alpha_id = res.get("alpha")
                    if not alpha_id and "id" in res:
                        alpha_id = res["id"]
                        
                    if alpha_id:
                        alpha["id"] = alpha_id
                        # Get details
                        details = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}").json()
                        is_metrics = details.get("is", {})
                        sharpe = is_metrics.get("sharpe", 0)
                        fitness = is_metrics.get("fitness", 0)
                        turnover = is_metrics.get("turnover", 0)
                        margin = is_metrics.get("margin", 0)
                        
                        print(f"[{alpha['name']}] DONE | ID: {alpha_id} | Sharpe: {sharpe} | Fitness: {fitness} | TO: {turnover}")
                        alpha["metrics"] = {
                            "sharpe": sharpe,
                            "fitness": fitness,
                            "turnover": turnover,
                            "margin": margin,
                        }
                        completed.append(alpha)
                    else:
                        print(f"[{alpha['name']}] COMPLETED but no alpha ID found: {res}")
                else:
                    remaining.append(alpha)
            except Exception as e:
                print(f"Error polling {alpha['name']}: {e}")
                remaining.append(alpha)
        
        pending_alphas = remaining
        if pending_alphas:
            time.sleep(10)

    # Save results
    results_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_01_results.json'
    with open(results_file, 'w') as f:
        json.dump(completed, f, indent=4)
        
    print("\n--- DONE ---")
    for a in sorted(completed, key=lambda x: x.get("metrics", {}).get("sharpe", 0), reverse=True):
        m = a["metrics"]
        print(f"{a['name']} | ID: {a['id']} | Sharpe: {m['sharpe']} | Fitness: {m['fitness']} | TO: {m['turnover']} | Margin: {m['margin']}")

if __name__ == "__main__":
    main()
