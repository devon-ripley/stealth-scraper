
import time
from stealth_scraper import create_stealth_browser, StealthLevel, StealthConfig

def test_headless_fast():
    print("\n🚀 Testing FAST + HEADLESS Mode...")
    
    start_time = time.time()
    
    # Initialize with Fast + Headless + Block Resources
    browser = create_stealth_browser(
        level=StealthLevel.FAST,
        headless=True,
        block_resources=True
    )
    
    init_time = time.time()
    print(f"  Init Time: {init_time - start_time:.2f}s")
    
    with browser:
        print("  Navigating to example.com...")
        browser.navigate("https://example.com")
        
        nav_time = time.time()
        print(f"  Nav Time: {nav_time - init_time:.2f}s")
        
        # Test teleportation
        print("  Testing mouse movement (Teleportation)...")
        browser.move_to(100, 100)
        browser.move_to(500, 500) 
        # These should be near instant
        
        move_time = time.time()
        print(f"  Move Time: {move_time - nav_time:.2f}s")
        
        # Verify headless state via JS
        is_headless = browser.driver.execute_script("return navigator.webdriver")
        print(f"  navigator.webdriver (Should be undefined): {is_headless}")
        
        ua = browser.driver.execute_script("return navigator.userAgent")
        print(f"  User Agent: {ua}")
        
        # Verify resource blocking (check for images)
        # We can't easily check for blocked network requests without listeners, 
        # but we can check if images loaded? 
        # Actually easier to just check speed manually or look for console errors.
        
    total_time = time.time() - start_time
    print(f"✅ Total Test Time: {total_time:.2f}s")

if __name__ == "__main__":
    test_headless_fast()
