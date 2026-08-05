import json
import sys
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    sess, _ = brain1.sign_in('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt')

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_all_pending.json', 'r') as f:
        data = json.load(f)

    print(f"{'Name':<30} | {'Status':<10} | {'Alpha ID':<8} | {'Sharpe':<6} | {'Fitness':<7} | {'Returns':<7}")
    print('-'*85)

    for row in data:
        name = row['name']
        res = row.get('sim_result', {})
        status = res.get('status') or res.get('state')
        alpha_id = res.get('alpha')
        
        if status == 'COMPLETE' and isinstance(alpha_id, str):
            url = f'https://api.worldquantbrain.com/alphas/{alpha_id}'
            alpha_res = sess.get(url).json()
            is_stats = alpha_res.get('is', {})
            if not is_stats:
                print(f"{name:<30} | {status:<10} | {alpha_id:<8} | {'N/A':<6} | {'N/A':<7} | {'N/A':<7}")
                continue
                
            sharpe = is_stats.get('sharpe', 0)
            fitness = is_stats.get('fitness', 0)
            returns = is_stats.get('returns', 0)
            print(f"{name:<30} | {status:<10} | {alpha_id:<8} | {sharpe:6.2f} | {fitness:7.2f} | {returns:6.2%}")
        else:
            print(f"{name:<30} | {status:<10} | {'N/A':<8} | {'N/A':<6} | {'N/A':<7} | {'N/A':<7}")
            if status in ['ERROR', 'WARNING']:
                print(f"  -> Message: {res.get('message', '')}")

if __name__ == '__main__':
    main()
