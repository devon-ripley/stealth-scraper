import pytest
from stealth_scraper import create_stealth_browser, StealthLevel

def test_ua_property_consistency(ua_type):
    """
    Verify that browser properties match the device type.
    Note: 'ua_type' is automatically provided by conftest.py, 
    and the browser is automatically configured for that type.
    """
    # Simply use create_stealth_browser() - the identity is magically swapped by conftest.py
    with create_stealth_browser(level=StealthLevel.MEDIUM) as browser:
        browser.navigate("https://example.com")
        
        actual_ua = browser.execute_script("return navigator.userAgent")
        is_actually_mobile = (ua_type == "mobile")
        
        # Verify consistent identity
        if is_actually_mobile:
            assert "Mobile" in actual_ua or "Android" in actual_ua
        
        # Check Plugins
        plugin_count = browser.execute_script("return navigator.plugins.length")
        if is_actually_mobile:
            assert plugin_count == 0
        else:
            assert plugin_count > 0
            
        # Check Platform
        platform = browser.execute_script("return navigator.platform")
        if is_actually_mobile:
            assert platform == "Linux armv8l"
        else:
            assert any(x in platform for x in ["Win", "Mac", "Linux x86"])

        # Check Viewport Size
        width = browser.execute_script("return window.innerWidth")
        if is_actually_mobile:
            assert width <= 500
        else:
            assert width > 1000

        # Check Touch Points
        touch_points = browser.execute_script("return navigator.maxTouchPoints")
        if is_actually_mobile:
            assert touch_points > 0
        else:
            assert touch_points == 0

def test_language_header_consistency():
    """Verify that Accept-Language header matches navigator.languages."""
    # This test doesn't even need 'ua_type' arg, but it will still run twice!
    with create_stealth_browser(level=StealthLevel.MEDIUM) as browser:
        browser.network.start_capture()
        browser.navigate("https://www.google.com")
        
        # Get captured headers
        traffic = browser.network.get_traffic()
        request_headers = {}
        for event in traffic:
            if 'params' in event and 'request' in event['params']:
                if 'headers' in event['params']['request']:
                    url = event['params']['request'].get('url', '')
                    # Skip chrome:// internal requests
                    if not url.startswith('chrome'):
                        request_headers = event['params']['request']['headers']
                        break
        
        accept_lang = request_headers.get('accept-language', '') or request_headers.get('Accept-Language', '')
        nav_langs_list = browser.execute_script("return navigator.languages")
        
        # Check first language
        first_nav_lang = nav_langs_list[0]
        assert first_nav_lang in accept_lang
