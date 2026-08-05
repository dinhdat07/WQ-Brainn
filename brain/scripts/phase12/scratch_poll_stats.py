import sys
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1
credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
session, _ = brain1.sign_in(credentials_path)
resp = session.get("https://api.worldquantbrain.com/alphas/QPGexAlr")
if resp.status_code == 200:
    data = resp.json()
    sharpe = data.get("is", {}).get("sharpe", 0)
    fitness = data.get("is", {}).get("fitness", 0)
    turnover = data.get("is", {}).get("turnover", 0)
    print(f"Sharpe: {sharpe}, Fitness: {fitness}, Turnover: {turnover}")
