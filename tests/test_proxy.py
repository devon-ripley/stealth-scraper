"""
Sample script demonstrating proxy usage with StealthBrowser.
Loads credentials from .env file.

Usage:
    1. Copy .env.example to .env and fill in your DataImpulse credentials
    2. Activate venv: .venv\Scripts\Activate.ps1
    3. Run: python test_proxy.py
"""

import os
from dotenv import load_dotenv
from stealth_scraper import StealthBrowser, ProxyConfig
from selenium.webdriver.common.by import By

# Load environment variables from .env file
load_dotenv()


def get_proxy_config():
    """Create ProxyConfig from environment variables."""
    username = os.getenv("DATAIMPULSE_USERNAME", "")
    password = os.getenv("DATAIMPULSE_PASSWORD", "")
    city = os.getenv("DATAIMPULSE_CITY", "") or None  # Convert empty string to None
    
    if not username or not password:
        print("⚠️  Warning: DATAIMPULSE_USERNAME or DATAIMPULSE_PASSWORD not set in .env")
        print("   Proxy will be disabled. Running without proxy...")
        return None
    
    return ProxyConfig(
        enabled=True,
        username=username,
        password=password,
        country="us",
        city=city
    )


def test_ip_address(browser):
    """Check current IP address using httpbin."""
    print("\n🔍 Checking IP address...")
    browser.navigate("https://httpbin.org/ip")
    browser.random_pause(2.0, 4.0)
    
    try:
        if "pre" in browser.driver.page_source:
             body = browser.driver.find_element(By.TAG_NAME, "pre").text
        else:
             body = browser.driver.find_element(By.TAG_NAME, "body").text
        
        if not body.strip():
            print(f"   ⚠️  Empty body. Page title: {browser.driver.title}")
            print(f"   Source snippet: {browser.get_page_source()[:500]}")
    except Exception as e:
        print(f"   ❌ Error getting content: {e}")
    else:
        print(f"   Response: {body}")


def test_ip_location(browser):
    """Check IP geolocation."""
    print("\n🌍 Checking IP location...")
    browser.navigate("https://ipinfo.io/json")
    browser.random_pause(2.0, 4.0)
    
    try:
        body = browser.driver.find_element(By.TAG_NAME, "body").text
        print(f"   Location info: {body}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    print("=" * 50)
    print("Stealth Scraper - Proxy Test")
    print("=" * 50)
    
    # Get proxy configuration
    proxy_config = get_proxy_config()
    
    if proxy_config:
        print(f"\n✅ Proxy enabled")
        print(f"   Country: {proxy_config.country}")
        print(f"   City: {proxy_config.city or '(not set - country only)'}")
    else:
        print("\n⚠️  Running without proxy")
    
    # Start browser with proxy
    print("\n🚀 Starting browser...")
    
    with StealthBrowser(proxy_config=proxy_config) as browser:
        test_ip_address(browser)
        test_ip_location(browser)
        
        print("\n✅ Test complete!")
        print("   Check the IP address above to verify proxy is working.")
        
        # Keep browser open for a moment to see results
        browser.random_pause(3.0, 5.0)


if __name__ == "__main__":
    main()
