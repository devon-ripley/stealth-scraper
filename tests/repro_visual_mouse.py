
import pytest
import time
from pathlib import Path
from stealth_scraper import create_stealth_browser, StealthConfig
from selenium.webdriver.common.by import By

def log_result(msg):
    with open("repro_results.txt", "a") as f:
        f.write(msg + "\n")

def test_visual_mouse_present(request):
    """Verify that the visual mouse element exists in the DOM when enabled."""
    node_id = request.node.name 
    log_result(f"--- RUNNING: {node_id} ---")

    # 1. Test HTTP
    url = "https://example.com"
    log_result(f"Checking HTTP: {url}")
    try:
        # Correctly passing visualize_mouse as kwarg
        with create_stealth_browser(visualize_mouse=True, headless=False) as browser:
            browser.navigate(url)
            time.sleep(2)
            try:
                browser.driver.find_element(By.ID, "stealth-cursor-tracker")
                log_result("HTTP Result: SUCCESS (Element found)")
            except:
                log_result("HTTP Result: FAILURE (Element NOT found)")
    except Exception as e:
        log_result(f"HTTP Result: CRASH ({e})")

    # 2. Test FILE
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"
    log_result(f"Checking FILE: {test_page_path}")
    try:
        with create_stealth_browser(visualize_mouse=True, headless=False) as browser:
            browser.navigate(test_page_path)
            time.sleep(2)
            try:
                browser.driver.find_element(By.ID, "stealth-cursor-tracker")
                log_result("FILE Result: SUCCESS (Element found)")
            except:
                log_result("FILE Result: FAILURE (Element NOT found)")
    except Exception as e:
        log_result(f"FILE Result: CRASH ({e})")
