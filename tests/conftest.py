import pytest
from typing import Tuple
from stealth_scraper.config import StealthConfig, HumanBehaviorConfig, StealthLevel
import stealth_scraper.browser
import stealth_scraper

def pytest_addoption(parser):
    parser.addoption(
        "--browser-type", 
        action="store", 
        default="all", 
        help="Type of browser to test: mobile, desktop, or all"
    )

@pytest.fixture(params=["mobile", "desktop"])
def ua_type(request):
    """Fixture to provide the current device type being tested."""
    option = request.config.getoption("--browser-type")
    if option == "all":
        return request.param
    elif option == request.param:
        return request.param
    else:
        pytest.skip(f"Skipping {request.param} as browser-type is set to {option}")

@pytest.fixture(autouse=True)
def _apply_stealth_overrides(monkeypatch, ua_type):
    """
    Universally apply device-specific defaults by wrapping get_stealth_config.
    """
    mobile_ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
    desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    
    target_ua = mobile_ua if ua_type == "mobile" else desktop_ua
    is_mobile = (ua_type == "mobile")
    
    # Target the actual source of the function
    original_get_config = stealth_scraper.browser.get_stealth_config
    
    def wrapped_get_config(level: StealthLevel) -> Tuple[HumanBehaviorConfig, StealthConfig]:
        behavior, stealth = original_get_config(level)
        # Force the device type
        stealth.user_agent = target_ua
        stealth.is_mobile = is_mobile
        if is_mobile:
            stealth.randomize_viewport = True
        return behavior, stealth
    
    # Monkeypatch the function in all locations it might be accessed
    monkeypatch.setattr(stealth_scraper.browser, "get_stealth_config", wrapped_get_config)
    monkeypatch.setattr(stealth_scraper, "get_stealth_config", wrapped_get_config)
    
    # Also patch the class attributes as a safety fallback
    monkeypatch.setattr(StealthConfig, "user_agent", target_ua)
    monkeypatch.setattr(StealthConfig, "is_mobile", is_mobile)

@pytest.fixture
def stealth_config(ua_type):
    """Legacy helper for tests that explicitly want a config object."""
    from stealth_scraper import get_stealth_config, StealthLevel
    _, config = get_stealth_config(StealthLevel.MEDIUM)
    return config
