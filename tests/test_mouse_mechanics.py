
import pytest
import time
from stealth_scraper import create_stealth_browser

@pytest.mark.desktop_only
def test_mouse_random_start_and_persistence():
    """
    Verify that:
    1. Mouse starts at a random position (not 0,0).
    2. Mouse position is preserved across page navigations.
    """
    with create_stealth_browser(headless=True, visualize_mouse=False) as browser:
        # 1. Random Start
        # Note: In headless, viewport might be specific, but logic should still apply
        start_pos = browser.mouse.current_pos
        # There is a 1/(1920*1080) chance this fails if random picks 0,0. Acceptable risk.
        assert start_pos != (0, 0), f"Mouse started at {start_pos}, expected random"
        
        # 2. Persistence
        target_x, target_y = 500, 500
        browser.mouse.move_to(target_x, target_y)
        assert browser.mouse.current_pos == (target_x, target_y)
        
        # Navigate
        browser.navigate("about:blank")
        
        # Verify internal persistence
        assert browser.mouse.current_pos == (target_x, target_y), "Mouse position reset after navigation"
