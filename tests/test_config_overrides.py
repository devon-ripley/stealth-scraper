from stealth_scraper import create_stealth_browser, StealthLevel, CustomStealthLevel, StealthIdentity

def test_custom_level():
    # Automatically runs twice (Mobile/Desktop)
    custom_fast = CustomStealthLevel(
        base=StealthLevel.HIGH,
        max_mouse_speed=0.0,
        block_resources=True,
        identity=StealthIdentity.CONSISTENT
    )
    
    browser = create_stealth_browser(
        level=custom_fast,
        headless=True
    )
    
    assert browser.behavior_config.max_mouse_speed == 0.0
    assert browser.stealth_config.block_resources is True
    assert browser.stealth_config.identity == StealthIdentity.CONSISTENT

def test_factory_precedence():
    custom_fast = CustomStealthLevel(
        base=StealthLevel.HIGH,
        headless=True
    )
    
    browser_override = create_stealth_browser(
        level=custom_fast,
        headless=False # Should win
    )
    
    assert browser_override.stealth_config.headless is False
