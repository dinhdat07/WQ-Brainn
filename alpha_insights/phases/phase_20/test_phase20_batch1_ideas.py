import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

def simulate(expression, universe="TOP3000", delay=1, neutralization="SUBINDUSTRY", truncation=0.08, paste_id=None):
    data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": universe,
            "delay": delay,
            "decay": 0,
            "neutralization": neutralization,
            "truncation": truncation,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": expression
    }
    
    while True:
        try:
            response = session.post(f"{API_BASE}/simulations", json=data, timeout=10)
            if response.status_code == 201:
                sim_id = response.headers.get("Location").split("/")[-1]
                print(f"Simulation started for {expression[:30]}... ID: {sim_id}")
                return sim_id
            elif response.status_code == 429 or response.status_code == 403:
                print(f"Rate limited (simulate). Waiting...")
                time.sleep(10)
            else:
                print(f"Error starting simulation: {response.status_code}")
                print(response.text)
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed in simulate: {e}")
            time.sleep(10)

def check_status(sim_id):
    while True:
        try:
            resp = session.get(f"{API_BASE}/simulations/{sim_id}", timeout=10)
            if resp.status_code == 200:
                if "status" in resp.json():
                    status = resp.json()["status"]
                    if status == "WARNING" or status == "ERROR":
                        print(f"Simulation failed: {status}")
                        return None
                    if status == "DONE":
                        alpha_id = resp.json().get("alpha")
                        return alpha_id
            elif resp.status_code == 403 or resp.status_code == 429: # Too many requests
                time.sleep(5)
                continue
            else:
                print(f"Error checking status: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        time.sleep(2)

def print_metrics(alpha_id):
    resp = session.get(f"{API_BASE}/alphas/{alpha_id}")
    if resp.status_code == 200:
        is_metrics = resp.json().get("is", {})
        checks = is_metrics.get("checks", [])
        print("\n=== METRICS ===")
        print(f"Alpha ID: {alpha_id}")
        print(f"Sharpe: {is_metrics.get('sharpe')}")
        print(f"Fitness: {is_metrics.get('fitness')}")
        print(f"Turnover: {is_metrics.get('turnover')}")
        print(f"Margin: {is_metrics.get('margin')}")
        print(f"Drawdown: {is_metrics.get('drawdown')}")
        for check in checks:
            print(f"Check {check.get('name')}: {check.get('result')}")
    else:
        print(f"Error getting alpha metrics: {resp.status_code}")

expr1 = "ts_decay_linear(ts_corr(returns, ts_delta(anl4_afv4_eps_mean, 20), 20), 10)"
expr2 = "ts_decay_linear(rank(-ts_delta(close, 5)) * rank(ts_delta(ts_sum(mean_composite_sentiment_score, 10), 5)), 10)"
expr3 = "ts_decay_linear(group_neutralize(est_cashflow_op / cap, market) + group_neutralize(-returns, market), 10)"
expr4 = "ts_decay_linear(-group_neutralize(ts_mean(returns, 20), sector), 10)"

print("Testing Idea 1: Short Interest")
sim1 = simulate(expr1, neutralization="MARKET")
time.sleep(5)
print("Testing Idea 2: News Sentiment Divergence")
sim2 = simulate(expr2, neutralization="MARKET")
time.sleep(5)
print("Testing Idea 3: Deep Fundamental Yield")
sim3 = simulate(expr3, neutralization="MARKET")
time.sleep(5)
print("Testing Idea 4: Cross-Sectional Industry Momentum")
sim4 = simulate(expr4, neutralization="MARKET")

sims = [sim1, sim2, sim3, sim4]
for sim in sims:
    if sim:
        alpha_id = check_status(sim)
        if alpha_id:
            print_metrics(alpha_id)
