import sys
import json
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
session, _ = brain1.sign_in(credentials_path)

resp = session.get("https://api.worldquantbrain.com/simulations/1bcfPd7z55jPbEDt5Hj5iYT")
print(json.dumps(resp.json(), indent=4))
