import sys
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
session, _ = brain1.sign_in(credentials_path)

resp = session.get("https://api.worldquantbrain.com/users/me")
print(f"Status: {resp.status_code}")
print(f"Text: {resp.text[:200]}")
