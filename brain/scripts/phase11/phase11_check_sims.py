import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def check_pending(batch_name):
    path = f'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/{batch_name}_pending.json'
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        pending = json.load(f)
    return pending

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print('Login failed!')
        return

    all_pending = []
    for b in ['phase11_batch01', 'phase11_batch02', 'phase11_batch03']:
        pending = check_pending(b)
        for p in pending:
            p['batch'] = b
        all_pending.extend(pending)

    print(f'Checking {len(all_pending)} pending simulations...')
    
    finished = []
    
    for p in all_pending:
        sim_id = p['id']
        url = f'https://api.worldquantbrain.com/simulations/{sim_id}'
        try:
            resp = session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get('status')
                print(f'{p["name"]}: {status}')
                if status == 'COMPLETE':
                    alpha_id = data.get('alpha')
                    if alpha_id:
                        print(f' -> Alpha ID: {alpha_id}')
                        p['alpha_id'] = alpha_id
                    finished.append(p)
                elif status == 'ERROR':
                    print(f' -> Error: {data.get("message")}')
            else:
                print(f'{p["name"]}: Error {resp.status_code}')
        except Exception as e:
            print(f'{p["name"]}: Error {e}')
        time.sleep(1)

    print(f'\nFound {len(finished)} completed simulations. Retrieving stats...')
    
    results = []
    for f in finished:
        if 'alpha_id' not in f:
            continue
        alpha_id = f['alpha_id']
        url = f'https://api.worldquantbrain.com/alphas/{alpha_id}'
        try:
            resp = session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                is_stats = data.get('is', {})
                results.append({
                    'name': f['name'],
                    'batch': f['batch'],
                    'id': alpha_id,
                    'sharpe': is_stats.get('sharpe', 0),
                    'fitness': is_stats.get('fitness', 0),
                    'turnover': is_stats.get('turnover', 0),
                    'returns': is_stats.get('returns', 0),
                    'drawdown': is_stats.get('drawdown', 0),
                    'margin': is_stats.get('margin', 0)
                })
        except Exception as e:
            pass
        time.sleep(1)
        
    print('\nRESULTS:')
    results.sort(key=lambda x: x.get('sharpe', 0) if x.get('sharpe') is not None else -99, reverse=True)
    for r in results:
        print(f"{r['name']} ({r['id']}): Sharpe: {r['sharpe']:.2f}, Fit: {r['fitness']:.2f}, Trn: {r['turnover']:.2%}, Ret: {r['returns']:.2%}, DD: {r['drawdown']:.2%}")
        
    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_results.json', 'w') as out:
        json.dump(results, out, indent=4)

if __name__ == '__main__':
    main()
