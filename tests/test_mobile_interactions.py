
import pytest
import time
from stealth_scraper import create_stealth_browser

@pytest.mark.mobile_only
def test_mobile_touch_interactions():
    """
    Verify that:
    1. Scrolling uses Touch Events (changes scrollY).
    2. Clicking uses Touch Events (triggers element interactions).
    """
    # Force mobile config
    with create_stealth_browser(headless=True, is_mobile=True) as browser:
        # Load a blank page we can inject into
        browser.navigate("about:blank")
        
        # Setup test environment with JS
        browser.driver.execute_script("""
            // Make body scrollable
            document.body.style.height = '5000px';
            document.body.style.width = '100%';
            
            // Add a test button
            var btn = document.createElement('button');
            btn.id = 'test-btn';
            btn.innerHTML = 'Tap Me';
            btn.style.position = 'absolute';
            btn.style.top = '100px';
            btn.style.left = '100px';
            btn.style.width = '200px';
            btn.style.height = '100px';
            document.body.appendChild(btn);
            
            // Add event listeners to track Touch vs Mouse
            window.lastEventType = 'none';
            btn.addEventListener('touchstart', function() { window.lastEventType = 'touchstart'; });
            btn.addEventListener('mousedown', function() { if(window.lastEventType !== 'touchstart') window.lastEventType = 'mousedown'; });
            btn.addEventListener('click', function() { 
                document.body.setAttribute('data-clicked', 'true');
            });
        """)
        
        # 1. Test Touch Scroll
        initial_y = browser.driver.execute_script("return window.pageYOffset;")
        browser.scroll.scroll_to(500)
        time.sleep(1)
        new_y = browser.driver.execute_script("return window.pageYOffset;")
        
        # Should have scrolled significantly (it might not be exactly 500 due to swipe mechanics, but should be > 0)
        assert new_y > 0, f"Page did not scroll. Y={new_y}"
        
        # 2. Test Touch Tap
        # Scroll back up to ensure button is in view/easy to hit? 
        # browser.scroll.scroll_to(0) 
        # Actually, click_element handles scrolling.
        
        btn = browser.driver.find_element("id", "test-btn")
        browser.click_element(btn)
        time.sleep(0.5)
        
        # Verify Click
        is_clicked = browser.driver.execute_script("return document.body.getAttribute('data-clicked');")
        assert is_clicked == "true", "Button was not clicked"
        
        # Verify Event Type (Advanced: check if touchstart fired)
        # Note: In CDP dispatchTouchEvent, 'touchstart' should fire.
        last_event = browser.driver.execute_script("return window.lastEventType;")
        assert last_event == "touchstart", f"Expected touchstart event, got {last_event}"
