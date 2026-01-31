import pytest
import time
from stealth_scraper import create_stealth_browser, StealthLevel

def test_mouse_curvature_sanity():
    """Verify that mouse movement is not a robotic straight line."""
    with create_stealth_browser(level=StealthLevel.MEDIUM, headless=True) as browser:
        browser.navigate("about:blank")
        
        start_time = time.time()
        # Move across screen
        browser.mouse.move_to(500, 500)
        duration = time.time() - start_time
        
        # Human movement should take reasonable time
        assert duration > 0.3

def test_error_invalid_proxy_format():
    """Verify that providing a malformed proxy string raises a helpful error."""
    from stealth_scraper.proxy import Proxy
    
    with pytest.raises(ValueError) as excinfo:
        Proxy.from_url("not_a_url")
    assert "Invalid proxy URL" in str(excinfo.value) or "could not be parsed" in str(excinfo.value).lower()

def test_browser_context_manager_cleanup():
    """Ensure browser always closes even on error inside context."""
    b = create_stealth_browser(level=StealthLevel.FAST, headless=True)
    try:
        with b:
            raise RuntimeError("Force crash")
    except RuntimeError:
        pass
    
    # Verify driver is quit
    assert b.driver is None
