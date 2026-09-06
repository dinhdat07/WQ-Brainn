import requests
import json

with open('e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt') as f:
    creds = json.load(f)
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.post('https://api.worldquantbrain.com/authentication')

for alpha_id in ['le8JY1xA', 'N1QkG89g', 'blR7gg3p', '4c67FE8YL4rfcgOeAqGJbMV']:
    if len(alpha_id) > 10:
        # it's a simulation ID, get the alpha ID first
        resp = session.get(f'https://api.worldquantbrain.com/simulations/{alpha_id}')
        if resp.status_code == 200:
            data = resp.json()
            if 'alpha' in data:
                alpha_id = data['alpha']
            else:
                print(f"Simulation {alpha_id} not ready.")
                continue

    resp = session.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
    if resp.status_code == 200:
        data = resp.json()
        is_metrics = data.get('is', {})
        print(f"Alpha: {alpha_id}")
        print(f"Sharpe: {is_metrics.get('sharpe')}")
        print(f"Fitness: {is_metrics.get('fitness')}")
        print(f"Sub-universe Sharpe: {is_metrics.get('subUniverseSharpe')}")
        print("---")
    else:
        print(f"Failed to get {alpha_id}")
