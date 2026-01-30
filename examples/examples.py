"""
Example usage of the Ultimate Stealth Web Scraper.
"""

from stealth_scraper import (
    StealthBrowser,
    HumanBehaviorConfig,
    StealthConfig,
    create_stealth_browser,
)
from selenium.webdriver.common.by import By
import time


def example_basic_usage():
    """Basic usage with default settings."""
    with StealthBrowser() as browser:
        browser.navigate("https://example.com")
        
        # Random pause like a human would
        browser.random_pause()
        
        # Simulate reading the page
        browser.simulate_reading()
        
        # Get content
        content = browser.get_page_source()
        print(f"Page length: {len(content)} characters")


def example_form_interaction():
    """Example interacting with forms."""
    # Custom behavior for slower, more careful interaction
    behavior = HumanBehaviorConfig(
        min_typing_delay=0.08,
        max_typing_delay=0.3,
        typo_chance=0.03,  # Slightly higher typo rate
        min_mouse_speed=0.8,
        max_mouse_speed=2.5,
    )
    
    with StealthBrowser(behavior_config=behavior) as browser:
        browser.navigate("https://example.com/login")
        
        # Find and interact with form elements
        try:
            username_field = browser.wait_for_element(
                By.ID, "username", 
                timeout=10, 
                condition="visible"
            )
            browser.type_into(username_field, "myusername")
            
            browser.random_pause()
            
            password_field = browser.wait_for_element(
                By.ID, "password",
                condition="visible"
            )
            browser.type_into(password_field, "mypassword")
            
            browser.random_pause()
            
            submit_btn = browser.wait_for_element(
                By.CSS_SELECTOR, "button[type='submit']",
                condition="clickable"
            )
            browser.click_element(submit_btn)
            
        except Exception as e:
            print(f"Error: {e}")


def example_navigation_and_scraping():
    """Example navigating multiple pages and scraping content."""
    stealth = StealthConfig(
        randomize_viewport=True,
        min_page_load_wait=3.0,
        max_page_load_wait=7.0,
    )
    
    behavior = HumanBehaviorConfig(
        reading_speed_wpm=200,  # Slower reader
        random_pause_chance=0.15,  # More random pauses
    )
    
    with StealthBrowser(behavior_config=behavior, stealth_config=stealth) as browser:
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]
        
        results = []
        
        for url in urls:
            browser.navigate(url)
            
            # Simulate human reading behavior
            browser.simulate_reading()
            
            # Random mouse movements
            browser.random_mouse_movement()
            browser.random_pause()
            
            # Scroll around
            browser.scroll.scroll_page("down", 0.5)
            browser.random_pause()
            browser.scroll.scroll_page("down", 0.3)
            browser.random_pause()
            
            # Collect data
            try:
                title = browser.driver.find_element(By.TAG_NAME, "h1").text
                results.append({
                    "url": url,
                    "title": title,
                })
            except:
                pass
            
            # Random longer pause between pages
            browser.random_pause(2.0, 5.0)
        
        return results


def example_custom_mouse_patterns():
    """Example with custom mouse movement patterns."""
    behavior = HumanBehaviorConfig(
        mouse_curve_intensity=0.4,  # More curved movements
        mouse_overshoot_chance=0.2,  # More overshoots
        mouse_jitter=True,
        min_mouse_speed=1.0,
        max_mouse_speed=3.0,
    )
    
    with StealthBrowser(behavior_config=behavior) as browser:
        browser.navigate("https://example.com")
        
        # Make several random movements
        for _ in range(5):
            browser.random_mouse_movement()
            browser.random_pause(0.5, 1.5)
        
        # Find and hover over links
        links = browser.driver.find_elements(By.TAG_NAME, "a")[:5]
        for link in links:
            browser.mouse.move_to_element(link)
            browser.random_pause(0.3, 1.0)


def example_infinite_scroll_page():
    """Example handling infinite scroll pages."""
    with StealthBrowser() as browser:
        browser.navigate("https://example.com/infinite-scroll")
        
        collected_items = set()
        max_scrolls = 10
        
        for i in range(max_scrolls):
            # Get current items
            items = browser.driver.find_elements(By.CSS_SELECTOR, ".item")
            for item in items:
                collected_items.add(item.text)
            
            # Human-like scroll down
            browser.scroll.scroll_page("down", 0.8)
            
            # Wait for content to load
            browser.random_pause(1.0, 3.0)
            
            # Occasionally scroll back up slightly
            if i % 3 == 0:
                browser.scroll.scroll_page("up", 0.2)
                browser.random_pause(0.5, 1.0)
            
            # Random mouse movement
            if i % 2 == 0:
                browser.random_mouse_movement()
            
            print(f"Scroll {i+1}: {len(collected_items)} items collected")
        
    return list(collected_items)


def example_advanced_stealth_features():
    """Example using advanced human behavior features."""
    with StealthBrowser() as browser:
        browser.navigate("https://example.com")
        
        # Simulate window switching (Tab away and back)
        print("Simulating window switch...")
        browser.simulate_window_switching()
        
        # Simulate keyboard shortcuts
        print("Simulating keyboard shortcut (Ctrl+C)...")
        browser.simulate_shortcut(["Control", "c"])
        
        # Human reading with natural pauses and micro-movements (idle entropy)
        print("Simulating deep reading...")
        browser.simulate_reading(word_count=300)


def example_with_persistent_profile():
    """Example using persistent browser profile."""
    stealth = StealthConfig(
        use_persistent_profile=True,
        profile_path="/tmp/chrome_profile",
    )
    
    # First session - login
    with StealthBrowser(stealth_config=stealth) as browser:
        browser.navigate("https://example.com/login")
        # ... login process ...
        browser.random_pause(2.0, 4.0)
    
    # Second session - already logged in
    with StealthBrowser(stealth_config=stealth) as browser:
        browser.navigate("https://example.com/dashboard")
        # Should be already logged in
        browser.simulate_reading()


if __name__ == "__main__":
    # Run basic example
    print("Running basic usage example...")
    example_basic_usage()
