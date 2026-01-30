
from stealth_scraper import StealthBrowser, StealthConfig
import time
import random

def test_stealth_mouse_visualization():
    """Test that the mouse visualization works when enabled."""
    print("Testing mouse visualization...")
    
    # Enable visualization
    stealth_config = StealthConfig(
        visualize_mouse=True,
        min_page_load_wait=1.0,  # Speed up test
        max_page_load_wait=2.0
    )
    
    with StealthBrowser(stealth_config=stealth_config) as browser:
        print("Navigating to example.com...")
        browser.navigate("https://example.com")
        
        # Check if debug cursor exists
        print("Checking for cursor element...")
        cursor_found = False
        for _ in range(10): # try for 5 seconds
            try:
                browser.driver.find_element("id", "stealth-cursor-tracker")
                print("SUCCESS: Cursor tracker element found!")
                cursor_found = True
                break
            except:
                time.sleep(0.5)
        
        if not cursor_found:
            print("FAILURE: Cursor tracker element NOT found after 5s!")
            return

        print("Performing random movements to visualize...")
        for i in range(5):
            print(f"Movement {i+1}/5")
            browser.random_mouse_movement()
            time.sleep(0.5)
            
        print("Test complete. You should have seen a red dot moving.")

if __name__ == "__main__":
    test_stealth_mouse_visualization()
