import json, requests, time
API_BASE = 'https://api.worldquantbrain.com'
with open('e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt') as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.post(f'{API_BASE}/authentication')

for sim_id in ['19CPeBdYq53lc7Hbe5tRptZ', 'SxWTl2HV4gr9xokyTchoqf', '2zzmhr5ju5a8aK98NNlO0d3', '24RRjSeEe4jM9BeASNh8KRO']:
    resp = session.get(f'{API_BASE}/simulations/{sim_id}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'\n--- SIM {sim_id} ---')
        print(f'Status: {data.get("status")}')
        if 'alpha' in data:
            alpha_id = data['alpha']
            print(f'Alpha ID: {alpha_id}')
            alpha_resp = session.get(f'{API_BASE}/alphas/{alpha_id}')
            if alpha_resp.status_code == 200:
                is_metrics = alpha_resp.json().get('is', {})
                print(f'Sharpe: {is_metrics.get("sharpe")}')
                print(f'Fitness: {is_metrics.get("fitness")}')
                print(f'Turnover: {is_metrics.get("turnover")}')
                for check in is_metrics.get('checks', []):
                    if check.get('name') in ['LOW_SHARPE', 'LOW_SUB_UNIVERSE_SHARPE', 'SELF_CORRELATION']:
                        print(f"Check {check.get('name')}: {check.get('result')} ({check.get('value', '')})")
    else:
        print(f"Failed to get {sim_id}: {resp.status_code} {resp.text}")
