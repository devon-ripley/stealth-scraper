import time
import pytest
from pathlib import Path
from stealth_scraper import create_stealth_browser, CustomStealthLevel, StealthLevel
from selenium.webdriver.common.by import By

def test_typo_simulation(ua_type):
    print(f"\n⌨️ Testing Typo Simulation on {ua_type}...")
    
    # Create a custom level with 100% typo chance
    custom_typo = CustomStealthLevel(
        base=StealthLevel.MEDIUM,
        typo_chance=1.0,
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
        
        test_text = "stealth_master"
        browser.type_into(username, test_text)
        
        # Verify it ended up correct despite typos
        final_val = username.get_attribute("value")
        assert final_val == test_text

def test_window_switching_and_shortcuts():
    # Automatically runs twice due to conftest.py
    browser = create_stealth_browser(level=StealthLevel.LOW, headless=True)
    
    with browser:
        browser.navigate("about:blank")
        browser.simulate_window_switching()
        browser.simulate_shortcut(['Control', 'a'])
        # Pass if no exceptions
