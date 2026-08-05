import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return
        
    submitted_ids = ['88pomANl', '6Xpn9V2L', 'Jjv1g3xO', 'd5RaEvVj', 'bldOZEjr', 'RR1bxvea', 'e7x3P7gO', 'le3WZmdl', 'ZYKo6R78', '2rpzj59P']
    target_ids = ['3qpLxXeO', 'zqNpjPpd', 'wpagOlqp', 'A1GKY6VY']
    
    for tid in target_ids:
        print(f"\nChecking correlations for Candidate {tid}...")
        for sid in submitted_ids:
            try:
                url = f"https://api.worldquantbrain.com/alphas/{tid}/correlations/{sid}"
                res = session.get(url).json()
                if "is" in res:
                    corr = res["is"]
                    print(f"  vs {sid}: {corr:.4f}")
                else:
                    print(f"  vs {sid}: {res}")
            except Exception as e:
                print(f"  vs {sid}: Error {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
