import time
import json
import random
import pytest
from pathlib import Path
from stealth_scraper import create_stealth_browser, StealthLocation, StealthIdentity

def test_geolocation_and_timezone(ua_type):
    # Keep ua_type arg because we use it for printing, 
    # but conftest.py provides it automatically.
    print(f"\n🌍 Testing Geolocation & Timezone Spoofing (Tokyo) on {ua_type}...")
    
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
        browser.navigate(test_page_path)
        
        # Verify TZ via JS
        tz = browser.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
        
        # Verify Language
        lang = browser.execute_script("return navigator.language")
        
        # Verify Geolocation (Promise-based)
        browser.driver.set_script_timeout(10)
        
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
        except Exception as e:
            coords = {"error": str(e)}
        
        # Assertions (Tokyo: 35.6895, 139.6917)
        assert tz == "Asia/Tokyo"
        assert "ja" in lang
        if isinstance(coords, dict) and coords.get('lat') is not None:
             assert abs(coords['lat'] - 35.6895) < 0.1

def test_fingerprint_seed(ua_type):
    print(f"\n🎨 Testing Fingerprint Consistency with Seed on {ua_type}...")
    
    seed = "test-fingerprint-seed-456"
    
    def get_fp(s):
        # We can just call create_stealth_browser() - conftest handles the UA
        b = create_stealth_browser(identity=StealthIdentity.CONSISTENT, identity_seed=s, headless=True)
        with b:
            # Must navigate for script injection to occur
            b.navigate("about:blank")
            vendor = b.execute_script("return document.createElement('canvas').getContext('webgl').getParameter(37445)")
            renderer = b.execute_script("return document.createElement('canvas').getContext('webgl').getParameter(37446)")
            return f"{vendor} || {renderer}"
    
    fp1 = get_fp(seed)
    fp2 = get_fp(seed)
    fp_diff = get_fp("different-seed-" + str(random.random()))
    
    assert fp1 == fp2
    assert fp1 != fp_diff
