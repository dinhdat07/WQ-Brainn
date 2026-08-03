import os
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain1 import sign_in
import requests

session, _ = sign_in('brain_credentials.txt')

urls = [
    'https://api.worldquantbrain.com/simulations/4F29rUbXW58Z9PiiVIEA2tR',
    'https://api.worldquantbrain.com/simulations/31FSNQg1b4SUbnfm0Mki0Wq',
    'https://api.worldquantbrain.com/simulations/4eaENdbqW4N4aP6jFEYL3C8',
    'https://api.worldquantbrain.com/simulations/3x53LUlr4CecAi9KvG3Gbd',
    'https://api.worldquantbrain.com/simulations/33earKbTI4Ry9IIStt4J1JD',
    'https://api.worldquantbrain.com/simulations/20271S66o50Mbno8GAT4dns',
    'https://api.worldquantbrain.com/simulations/2hi2g7esB5a18RzkZrsETxu'
]

for i, url in enumerate(urls, 1):
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        alpha_id = data.get('alpha')
        if alpha_id:
            a_resp = session.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
            a_data = a_resp.json()
            is_stats = a_data.get('is', {})
            sharpe = is_stats.get('sharpe')
            fit = is_stats.get('fitness')
            to = is_stats.get('turnover')
            print(f'Model {i}: Alpha {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {to}')
        else:
            print(f'Model {i}: No alpha ID. Status: {data.get("status")}')
    else:
        print(f'Model {i}: Failed to fetch {resp.status_code}')
