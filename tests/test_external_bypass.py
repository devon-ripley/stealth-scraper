import pytest
import time
import os
from stealth_scraper import StealthBrowser, StealthConfig, create_stealth_browser
from selenium.webdriver.common.by import By

@pytest.fixture(autouse=True)
def setup_dirs():
    if not os.path.exists("test_results"):
        os.makedirs("test_results")

def test_easy_target():
    """Test basic navigation on a simple static site."""
    with create_stealth_browser(headless=True) as browser:
        browser.navigate("http://books.toscrape.com/")
        assert "All products" in browser.driver.title

def test_medium_target():
    """Test AJAX/JS rendering capabilities."""
    with create_stealth_browser(headless=True) as browser:
        browser.navigate("https://www.scrapethissite.com/pages/ajax-javascript/")
        browser.wait_for_element(By.LINK_TEXT, "2015", timeout=10)
        assert "Oscar Winning Films" in browser.get_page_source()

def test_hard_target_fingerprint(ua_type):
    """Test vs bot detection/fingerprinting site."""
    print(f"\n🏃 Testing Hard Target (Fingerprint) on {ua_type}...")
    with create_stealth_browser(headless=True) as browser:
        browser.navigate("https://bot.sannysoft.com/")
        time.sleep(5)
        browser.save_screenshot(f"test_results/sannysoft_{ua_type}.png")

def test_human_behavior():
    """Test human-like interactions."""
    with create_stealth_browser(headless=True) as browser:
        browser.navigate("https://quotes.toscrape.com/login")
        
        # Move
        browser.random_mouse_movement()
        
        # Type
        username_input = browser.wait_for_element(By.ID, "username")
        browser.type_into(username_input, "test_user_human")
        assert "test_user" in username_input.get_attribute("value")
        
        # Scroll
        browser.navigate("https://quotes.toscrape.com/")
        start_y = browser.execute_script("return window.scrollY")
        browser.scroll.scroll_page("down", 0.5)
        time.sleep(1)
        end_y = browser.execute_script("return window.scrollY")
        assert end_y >= start_y
