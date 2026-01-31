import pytest
import time
from pathlib import Path
from stealth_scraper import create_stealth_browser, StealthLevel, get_stealth_config
from selenium.webdriver.common.by import By

def test_local_mechanics_demo():
    """Test core mechanics on a local test page."""
    # Use MEDIUM behavior for broad compatibility in tests
    behavior, _ = get_stealth_config(StealthLevel.MEDIUM)
    
    # Get local test page path
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"
    
    with create_stealth_browser(headless=True) as browser:
        browser.navigate(test_page_path)
        
        # 1. Reading
        browser.simulate_reading()
        
        # 2. Form Interaction
        username = browser.wait_for_element(By.ID, "username")
        browser.type_into(username, "stealth_tester")
        
        # 3. Mouse Movement
        hover_box = browser.wait_for_element(By.ID, "hover-box")
        browser.mouse.move_to_element(hover_box)
        
        # 4. Dynamic Content
        btn = browser.wait_for_element(By.ID, "show-hidden-btn")
        browser.click_element(btn)
        
        hidden_div = browser.wait_for_element(By.ID, "dynamic-area", condition="visible")
        assert "hidden" in hidden_div.text.lower()
