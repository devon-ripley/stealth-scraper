import pytest
import time
from stealth_scraper import create_stealth_browser, StealthLevel

def test_headless_fast():
    print("\n🚀 Testing FAST + HEADLESS Mode...")
    
    start_time = time.time()
    
    # Defaults are magic-swapped by conftest.py, but we can still specify level
    with create_stealth_browser(level=StealthLevel.FAST, headless=True, block_resources=True) as browser:
        browser.navigate("https://example.com")
        
        # Test teleportation (FAST level should have 0.0 mouse speed)
        browser.mouse.move_to(100, 100)
        browser.mouse.move_to(500, 500)
        
        # Verify webdriver is masked
        is_webdriver = browser.execute_script("return navigator.webdriver")
        assert is_webdriver is False
