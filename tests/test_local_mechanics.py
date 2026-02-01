import pytest
import time
from pathlib import Path
from stealth_scraper import create_stealth_browser, StealthLevel, get_stealth_config
from selenium.webdriver.common.by import By

@pytest.mark.desktop_only
def test_local_mechanics_desktop():
    """Test core mechanics on desktop with visual mouse."""
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"
    
    # Force desktop UA for this test path if needed, but create_stealth_browser should typically handle it based on pytest flags
    # However, create_stealth_browser defaults to device based on UA.
    
    with create_stealth_browser(headless=False, visualize_mouse=True) as browser:
        # Assert not mobile
        if browser._is_mobile:
             pytest.skip("Skipping desktop test on mobile configuration")

        browser.navigate(test_page_path)
        
        # Verify Visual Mouse is Present
        assert browser.driver.find_elements(By.ID, "stealth-cursor-tracker"), "Visual mouse should be present on Desktop"

        # 1. Reading
        browser.simulate_reading()
        
        # 2. Form Interaction
        username = browser.wait_for_element(By.ID, "username")
        browser.type_into(username, "stealth_tester")
        
        # 3. Mouse Movement
        hover_box = browser.wait_for_element(By.ID, "hover-box")
        browser.mouse.move_to_element(hover_box)

@pytest.mark.mobile_only
def test_local_mechanics_mobile():
    """Test core mechanics on mobile (NO visual mouse)."""
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"
    
    # We need to ensure we are in mobile mode. 
    # The pytest fixtures typically handle this via --browser-type.
    # We will check browser._is_mobile to fail fast.
    
    with create_stealth_browser(headless=False, visualize_mouse=True, is_mobile=True) as browser:
        browser.navigate(test_page_path)
        
        # Verify Visual Mouse is ABSENT
        assert not browser.driver.find_elements(By.ID, "stealth-cursor-tracker"), "Visual mouse should NOT be present on Mobile"
        
        # 1. Reading
        browser.simulate_reading()

