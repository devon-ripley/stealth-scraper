"""
Examples demonstrating the use of preset stealth levels.
"""

from stealth_scraper import (
    StealthLevel,
    create_browser_with_level,
    get_stealth_config,
    StealthBrowser,
)


def example_low_stealth():
    """Fast scraping with minimal stealth (basic anti-detection only)."""
    print("\n=== LOW STEALTH LEVEL ===")
    print("Fast, minimal stealth - good for sites with weak bot detection\n")

    with create_browser_with_level(StealthLevel.LOW) as browser:
        browser.navigate("https://example.com")
        browser.random_pause()

        content = browser.get_page_source()
        print(f"Page loaded: {len(content)} characters")


def example_medium_stealth():
    """Balanced stealth - good for most use cases."""
    print("\n=== MEDIUM STEALTH LEVEL ===")
    print("Balanced stealth with reasonable speed - recommended for most sites\n")

    with create_browser_with_level(StealthLevel.MEDIUM) as browser:
        browser.navigate("https://example.com")
        browser.simulate_reading()

        content = browser.get_page_source()
        print(f"Page loaded: {len(content)} characters")


def example_high_stealth():
    """Maximum stealth - for sites with strong bot detection."""
    print("\n=== HIGH STEALTH LEVEL ===")
    print("Maximum stealth, slower but most human-like\n")

    with create_browser_with_level(StealthLevel.HIGH) as browser:
        browser.navigate("https://example.com")

        # More realistic human behavior
        browser.simulate_reading()
        browser.random_mouse_movement()
        browser.scroll.scroll_page("down", 0.3)
        browser.random_pause()

        content = browser.get_page_source()
        print(f"Page loaded: {len(content)} characters")


def example_with_overrides():
    """Using preset levels with custom overrides."""
    print("\n=== MEDIUM STEALTH + CUSTOM OVERRIDES ===")
    print("Starting with MEDIUM preset, adding geolocation spoofing\n")

    # Start with MEDIUM preset, but add custom geolocation
    with create_browser_with_level(
        StealthLevel.MEDIUM,
        spoof_timezone="America/New_York",
        spoof_geolocation=(40.7128, -74.0060),  # NYC
        spoof_locale="en-US",
    ) as browser:
        browser.navigate("https://example.com")
        browser.random_pause()

        # Check timezone and geolocation
        timezone = browser.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
        print(f"Spoofed timezone: {timezone}")


def example_manual_config():
    """Manually getting config for inspection or modification."""
    print("\n=== MANUAL CONFIG FROM PRESET ===")
    print("Getting config objects for manual modification\n")

    # Get preset configurations
    behavior, stealth = get_stealth_config(StealthLevel.HIGH)

    # Inspect or modify before use
    print(f"Mouse speed range: {behavior.min_mouse_speed} - {behavior.max_mouse_speed}")
    print(f"Typo chance: {behavior.typo_chance}")
    print(f"Page load wait: {stealth.min_page_load_wait} - {stealth.max_page_load_wait}")

    # Modify if needed
    stealth.spoof_timezone = "Europe/London"
    behavior.reading_speed_wpm = 180  # Even slower

    # Use modified config
    with StealthBrowser(behavior_config=behavior, stealth_config=stealth) as browser:
        browser.navigate("https://example.com")
        print("Using modified HIGH preset")


def example_comparison():
    """Compare different stealth levels."""
    print("\n=== STEALTH LEVEL COMPARISON ===\n")

    levels = [
        (StealthLevel.LOW, "Low"),
        (StealthLevel.MEDIUM, "Medium"),
        (StealthLevel.HIGH, "High"),
    ]

    for level, name in levels:
        behavior, stealth = get_stealth_config(level)

        print(f"{name} Stealth Level:")
        print(f"  Mouse speed: {behavior.min_mouse_speed}-{behavior.max_mouse_speed}s")
        print(f"  Typing delay: {behavior.min_typing_delay}-{behavior.max_typing_delay}s")
        print(f"  Typo chance: {behavior.typo_chance * 100}%")
        print(f"  Random pauses: {behavior.random_pause_chance * 100}%")
        print(f"  Page load wait: {stealth.min_page_load_wait}-{stealth.max_page_load_wait}s")
        print(f"  Selenium-stealth: {stealth.use_selenium_stealth}")
        print()


if __name__ == "__main__":
    import sys

    # Show comparison first
    example_comparison()

    # Ask user which example to run
    print("\nAvailable examples:")
    print("1. Low stealth (fast)")
    print("2. Medium stealth (balanced)")
    print("3. High stealth (paranoid)")
    print("4. Medium with overrides")
    print("5. Manual config modification")

    choice = input("\nEnter choice (1-5) or 'all' to run all: ").strip().lower()

    if choice == "1":
        example_low_stealth()
    elif choice == "2":
        example_medium_stealth()
    elif choice == "3":
        example_high_stealth()
    elif choice == "4":
        example_with_overrides()
    elif choice == "5":
        example_manual_config()
    elif choice == "all":
        example_low_stealth()
        example_medium_stealth()
        example_high_stealth()
        example_with_overrides()
        example_manual_config()
    else:
        print("Running medium stealth as default...")
        example_medium_stealth()
