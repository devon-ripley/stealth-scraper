
from stealth_scraper import create_stealth_browser, StealthLevel, CustomStealthLevel, StealthIdentity

def test_custom_level():
    print("\n🛠️ Testing CustomStealthLevel...")
    
    # Define a custom level
    # Base: HIGH (Mouse curves, slow typing)
    # Override: max_mouse_speed=0.0 (Teleport), block_resources=True
    custom_fast = CustomStealthLevel(
        base=StealthLevel.HIGH,
        max_mouse_speed=0.0,
        block_resources=True,
        identity=StealthIdentity.CONSISTENT, # Test identity override
        invalid_param="should_warn_but_not_crash"
    )
    
    print("  Initializing browser with Custom Level...")
    browser = create_stealth_browser(
        level=custom_fast,
        headless=True
    )
    
    # Internal Verification
    # Check Behavior config
    mouse_speed = browser.behavior_config.max_mouse_speed
    print(f"  Max Mouse Speed (Should be 0.0): {mouse_speed}")
    
    # Check Stealth config
    block_res = browser.stealth_config.block_resources
    print(f"  Block Resources (Should be True): {block_res}")
    
    # Check Identity Config
    identity_res = browser.stealth_config.identity
    print(f"  Identity (Should be CONSISTENT): {identity_res}")
    
    if mouse_speed == 0.0 and block_res is True and identity_res == StealthIdentity.CONSISTENT:
        print("✅ Custom Level Overrides Applied Successfully!")
    else:
        print("❌ Custom Level Overrides FAILED.")

    print("\n🛠️ Testing Factory Precedence...")
    # Custom Level says HEADLESS=TRUE
    # Factory says HEADLESS=FALSE
    print("  Initializing with Custom(Headless=True) AND Factory(Headless=False)...")
    browser_override = create_stealth_browser(
        level=custom_fast,
        headless=False # Should win
    )
    
    is_headless = browser_override.stealth_config.headless
    print(f"  Result Headless (Should be False): {is_headless}")
    
    if is_headless is False:
        print("✅ Factory Argument Correctly Overrode Custom Level!")
    else:
        print("❌ Factory Argument FAILED to override.")

if __name__ == "__main__":
    test_custom_level()
