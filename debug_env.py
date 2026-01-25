import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("DATAIMPULSE_USERNAME")
password = os.getenv("DATAIMPULSE_PASSWORD")

print(f"Username present: {bool(username)}")
if username:
    print(f"Username length: {len(username)}")
    print(f"Username start: {username[:3]}...")

print(f"Password present: {bool(password)}")
if password:
    print(f"Password length: {len(password)}")
