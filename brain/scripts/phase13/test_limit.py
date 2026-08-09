import os, sys, time, json
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1
session, _ = brain1.sign_in('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt')

payload = {
    'type': 'REGULAR',
    'settings': {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': 0, 'neutralization': 'SUBINDUSTRY', 'truncation': 0.08,
        'pasteurization': 'ON', 'unitHandling': 'VERIFY', 'nanHandling': 'OFF',
        'language': 'FASTEXPR', 'visualization': False
    },
    'regular': 'close / open'
}

print("Waiting for limit to clear...")
while True:
    try:
        resp = session.post(brain1.SIMULATE_URL, json=payload, timeout=30)
        if resp.status_code == 201:
            print("Successfully submitted! Limit is clear.")
            break
        elif resp.status_code == 429:
            err = resp.json().get("detail", "")
            if err == "CONCURRENT_SIMULATION_LIMIT_EXCEEDED":
                print(".", end="", flush=True)
            else:
                print(f"\nOther 429: {resp.text}")
        else:
            print(f"\nOther Error: {resp.status_code} {resp.text}")
            break
    except Exception as e:
        print(f"\nException: {e}")
    time.sleep(10)
