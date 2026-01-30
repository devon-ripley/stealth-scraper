
import time
from pathlib import Path
from stealth_scraper import create_stealth_browser, CustomStealthLevel, StealthLevel
from selenium.webdriver.common.by import By

def test_typo_simulation():
    print("\n⌨️ Testing Typo Simulation (Forced)...")
    
    # Create a custom level with 100% typo chance and very slow typing to observe/ensure it triggers
    custom_typo = CustomStealthLevel(
        base=StealthLevel.MEDIUM,
        typo_chance=1.0, # 100% chance
        min_typing_delay=0.1,
        max_typing_delay=0.2
    )
    
    browser = create_stealth_browser(level=custom_typo, headless=True)
    
    # Use local test page
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"
    
    with browser:
        browser.navigate(test_page_path)
        username = browser.wait_for_element(By.ID, "username")
        
        # Type something
        test_text = "stealth"
        print(f"  Typing '{test_text}' with 100% typo chance...")
        browser.type_into(username, test_text)
        
        # Verify the final text is correct (since it should correct itself)
        final_val = username.get_attribute("value")
        print(f"  Final value: '{final_val}'")
        
        if final_val == test_text:
            print("✅ Typo Simulation & Correction PASSED")
        else:
            print(f"❌ Typo Simulation FAILED: Expected {test_text}, got {final_val}")

def test_window_switching_and_shortcuts():
    print("\n🪟 Testing Window Switching & Shortcuts...")
    
    browser = create_stealth_browser(level=StealthLevel.LOW, headless=True)
    
    with browser:
        browser.navigate("about:blank")
        
        # 1. Test Window Switching (Focus/Blur)
        # We can't easily verify the result without a page that listens for visibilitychange
        # but we can verify it doesn't crash the driver
        print("  Simulating window switching...")
        browser.simulate_window_switching()
        print("  ✅ Window switching completed without error")
        
        # 2. Test Shortcuts
        # Select all (Control+a) then delete doesn't work on about:blank
        # but we can try to send it to the body
        print("  Simulating shortcut Control+a...")
        browser.simulate_shortcut(['Control', 'a'])
        print("  ✅ Shortcut simulation completed without error")

if __name__ == "__main__":
    test_typo_simulation()
    test_window_switching_and_shortcuts()
