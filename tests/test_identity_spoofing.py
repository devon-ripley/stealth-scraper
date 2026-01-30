
import time
import json
import random
from pathlib import Path
from stealth_scraper import create_stealth_browser, StealthLocation, StealthIdentity

def test_geolocation_and_timezone():
    print("\n🌍 Testing Geolocation & Timezone Spoofing (Tokyo)...")
    
    # Configure Tokyo location
    tokyo = StealthLocation.Tokyo()
    
    browser = create_stealth_browser(
        location=tokyo,
        headless=True
    )
    
    # Get local test page path
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"

    with browser:
        print(f"  Navigating to {test_page_path}")
        browser.navigate(test_page_path)
        
        # Verify TZ via JS
        tz = browser.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
        print(f"  Browser Timezone: {tz}")
        
        # Verify Language
        lang = browser.execute_script("return navigator.language")
        print(f"  Browser Language: {lang}")
        
        # Verify Geolocation (Promise-based)
        # Set a script timeout
        browser.driver.set_script_timeout(10)
        
        print("  Requesting Geolocation...")
        geo_script = """
        const callback = arguments[arguments.length - 1];
        navigator.geolocation.getCurrentPosition(
            (pos) => callback({lat: pos.coords.latitude, lon: pos.coords.longitude}),
            (err) => callback({error: err.message}),
            {timeout: 5000}
        );
        """
        try:
            coords = browser.driver.execute_async_script(geo_script)
            print(f"  Browser Geolocation: {coords}")
        except Exception as e:
            coords = {"error": str(e)}
            print(f"  Geolocation Request failed: {e}")
        
        # Assertions (Tokyo: 35.6895, 139.6917)
        if tz == "Asia/Tokyo" and "ja" in lang:
            print("✅ Timezone and Language Spoofing PASSED")
        else:
            print(f"❌ Timezone/Language Spoofing FAILED (Expected ja/Tokyo, got {lang}/{tz})")
            
        if isinstance(coords, dict) and coords.get('lat') is not None:
            if abs(coords['lat'] - 35.6895) < 0.1:
                print("✅ Geolocation Spoofing PASSED")
            else:
                print(f"❌ Geolocation Spoofing FAILED: Unexpected coords {coords}")
        else:
            print(f"❌ Geolocation Spoofing FAILED: {coords}")

def get_fp(s):
    b = create_stealth_browser(identity=StealthIdentity.CONSISTENT, identity_seed=s, headless=True)
    with b:
        # Must navigate for script injection to occur
        b.navigate("about:blank")
        vendor = b.execute_script("return document.createElement('canvas').getContext('webgl').getParameter(37445)")
        return vendor

def test_fingerprint_seed():
    print("\n🎨 Testing Fingerprint Consistency with Seed...")
    
    seed = "test-fingerprint-seed-456"
    
    fp1 = get_fp(seed)
    fp2 = get_fp(seed)
    fp_diff = get_fp("different-seed-" + str(random.random()))
    
    print(f"  Seed {seed} -> Vendor: {fp1}")
    print(f"  Seed {seed} -> Vendor: {fp2}")
    print(f"  Different Seed -> Vendor: {fp_diff}")
    
    if fp1 and fp2 and fp1 == fp2:
        print("✅ Seed Consistency PASSED")
    else:
        print("❌ Seed Consistency FAILED")
        
    if fp1 != fp_diff:
        print("✅ Seed Randomness (between different seeds) PASSED")

if __name__ == "__main__":
    test_geolocation_and_timezone()
    test_fingerprint_seed()
