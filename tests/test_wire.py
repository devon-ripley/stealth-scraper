import os
import time
from dotenv import load_dotenv
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.by import By

load_dotenv()

def main():
    print("=" * 50)
    print("Selenium Wire + Undetected Chrome Proxy Test")
    print("=" * 50)
    
    username = os.getenv("DATAIMPULSE_USERNAME")
    password = os.getenv("DATAIMPULSE_PASSWORD")
    host = "gw.dataimpulse.com"
    port = 823
    
    if not username or not password:
        print("❌ Credentials missing in .env")
        return

    # Configure proxy
    proxy_url = f"http://{username}:{password}@{host}:{port}"
    seleniumwire_options = {
        'proxy': {
            'http': proxy_url,
            'https': proxy_url,
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    
    print(f"Testing proxy: {host}:{port}")
    
    print("🚀 Starting browser...")
    try:
        driver = uc.Chrome(
            seleniumwire_options=seleniumwire_options,
            headless=False,
            use_subprocess=True
        )
        
        print("\n🔍 Checking IP address...")
        driver.get("https://httpbin.org/ip")
        time.sleep(3)
        
        try:
            body = driver.find_element(By.TAG_NAME, "pre").text
            print(f"   Response: {body}")
        except:
            print(f"   Response body: {driver.find_element(By.TAG_NAME, 'body').text}")
            
        print("\n🌍 Checking IP location...")
        driver.get("https://ipinfo.io/json")
        time.sleep(3)
        
        try:
            body = driver.find_element(By.TAG_NAME, "pre").text
            print(f"   Location info: {body}")
        except:
            print(f"   Location info: {driver.find_element(By.TAG_NAME, 'body').text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()
