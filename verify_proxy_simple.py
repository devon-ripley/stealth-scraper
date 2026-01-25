import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

username = os.getenv("DATAIMPULSE_USERNAME")
password = os.getenv("DATAIMPULSE_PASSWORD")
host = "gw.dataimpulse.com"
port = 823

if not username or not password:
    print("❌ Credentials missing in .env")
    exit(1)

# Build proxy URL
# DataImpulse format: http://username:password@host:port
# (Note: requests handles auth in URL)
proxy_url = f"http://{username}:{password}@{host}:{port}"

print(f"Testing proxy: {host}:{port}")
print(f"Username: {username[:3]}...")

proxies = {
    "http": proxy_url,
    "https": proxy_url,
}

try:
    print("\nRequesting httpbin.org/ip...")
    response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Proxy works with Requests!")
    else:
        print("❌ Proxy returned non-200 status")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
