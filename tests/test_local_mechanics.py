
import argparse
import os
import time
from pathlib import Path
from stealth_scraper import (
    StealthBrowser, 
    StealthLevel, 
    get_stealth_config,
    HumanBehaviorConfig,
    StealthConfig
)
from selenium.webdriver.common.by import By

def run_feature_demo(level_name: str):
    """Run the stealth feature demo with specific stealth level."""
    print(f"\n🚀 Starting Stealth Feature Demo")
    print(f"🎯 Level: {level_name.upper()}")
    
    # Map string to enum
    level_map = {
        "low": StealthLevel.LOW,
        "medium": StealthLevel.MEDIUM,
        "high": StealthLevel.HIGH,
        "paranoid": StealthLevel.PARANOID,
    }
    level = level_map.get(level_name.lower(), StealthLevel.MEDIUM)
    
    # Get configuration for level
    behavior, stealth = get_stealth_config(level)
    
    # Enable mouse visualization for demo
    stealth.visualize_mouse = True
    
    # Get local test page path
    current_dir = Path(__file__).parent.absolute()
    test_page_path = f"file:///{current_dir}/test_page.html"
    
    with StealthBrowser(behavior_config=behavior, stealth_config=stealth) as browser:
        print(f"🌐 Navigating to test page...")
        browser.navigate(test_page_path)
        
        # 1. Reading
        print("\n📖 DEMO: Reading Behavior")
        print("   Simulating reading the intro text...")
        browser.simulate_reading()
        
        # 2. Form Interaction
        print("\n✍️ DEMO: Form Interaction")
        
        print("   Locating username field...")
        username = browser.wait_for_element(By.ID, "username")
        print("   Typing username (watch for typos/speed)...")
        browser.type_into(username, "stealth_master_99")
        
        browser.random_pause(0.5, 1.5)
        
        print("   Locating password field...")
        password = browser.wait_for_element(By.ID, "password")
        print("   Typing password...")
        browser.type_into(password, "SuperSecretP@ssw0rd")
        
        browser.random_pause(0.5, 1.0)
        
        print("   Clicking checkbox...")
        checkbox = browser.driver.find_element(By.ID, "remember-me")
        browser.click_element(checkbox)
        
        # 3. Mouse Movement
        print("\n🖱️ DEMO: Mouse Movement")
        print("   Moving to hover target...")
        hover_box = browser.driver.find_element(By.ID, "hover-box")
        
        # Move to it
        browser.mouse.move_to_element(hover_box)
        browser.random_pause(1.0, 2.0)
        
        # Move around it a bit randomly
        print("   performing random movements...")
        for _ in range(3):
            browser.random_mouse_movement()
            browser.random_pause(0.5, 1.0)
            
        # 4. Dynamic Content
        print("\n⚡ DEMO: Dynamic Content")
        print("   Clicking button to show hidden content...")
        btn = browser.driver.find_element(By.ID, "show-hidden-btn")
        browser.click_element(btn)
        
        print("   Waiting for hidden content to appear...")
        hidden_div = browser.wait_for_element(By.ID, "dynamic-area", condition="visible")
        print(f"   Found content: '{hidden_div.text}'")
        
        # 5. Long Scroll
        print("\n📜 DEMO: Long Scroll")
        print("   Scrolling internal container...")
        scroll_container = browser.driver.find_element(By.CSS_SELECTOR, ".scroll-content")
        
        # Move mouse to container first
        browser.mouse.move_to_element(scroll_container)
        
        # Scroll the container down using JS (since HumanScrollSimulator mainly targets window)
        # We'll simulate a few scroll steps
        print("   Step 1: Scroll down...")
        browser.driver.execute_script("arguments[0].scrollTop += 100;", scroll_container)
        time.sleep(0.5)
        
        print("   Step 2: Scroll down more...")
        browser.driver.execute_script("arguments[0].scrollTop += 100;", scroll_container)
        time.sleep(0.5)
        
        print("   Step 3: Scroll back up...")
        browser.driver.execute_script("arguments[0].scrollTop -= 150;", scroll_container)
        
        print("\n✨ Demo Complete! Closing in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run stealth feature demo")
    parser.add_argument(
        "--level", 
        type=str, 
        default="medium",
        choices=["low", "medium", "high", "paranoid"],
        help="Stealth level preset to use"
    )
    
    args = parser.parse_args()
    run_feature_demo(args.level)
