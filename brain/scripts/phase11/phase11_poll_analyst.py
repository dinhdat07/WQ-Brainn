import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    
    pending_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_analyst_revisions_pending.json'
    if not os.path.exists(pending_file):
        print("No pending simulations found.")
        return
        
    with open(pending_file, 'r') as f:
        pending = json.load(f)
        
    print(f"Checking {len(pending)} simulations...")
    completed = []
    
    for item in pending:
        sim_id = item['id']
        while True:
            progress = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}").json()
            status = progress.get('status')
            if status in ['ERROR', 'FAIL']:
                print(f"{item['name']} ({sim_id}): {status}")
                break
            elif status in ['COMPLETE', 'WARNING']:
                print(f"{item['name']} ({sim_id}): {status}")
                if status == 'WARNING':
                    print(f"  Warning: {progress.get('message')}")
                
                alpha_id = progress.get('alpha')
                if alpha_id:
                    alpha_data = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}").json()
                    is_metrics = alpha_data.get('is', {})
                    
                    print(f"  -> Alpha ID: {alpha_id}")
                    print(f"  -> Sharpe: {is_metrics.get('sharpe', 'N/A')}")
                    print(f"  -> Fitness: {is_metrics.get('fitness', 'N/A')}")
                    print(f"  -> Turnover: {is_metrics.get('turnover', 'N/A')}")
                    print(f"  -> Margin: {is_metrics.get('margin', 'N/A')}")
                    
                    item['alpha_id'] = alpha_id
                    item['metrics'] = is_metrics
                else:
                    print(f"  -> Completed, but no alpha ID generated (probably error).")
                    
                completed.append(item)
                break
            else:
                print(f"{item['name']}: {progress.get('progress', 0) * 100:.1f}%")
                time.sleep(10)

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_analyst_revisions_results.json', 'w') as f:
        json.dump(completed, f, indent=4)
        
    print("Done checking all.")

if __name__ == "__main__":
    main()
