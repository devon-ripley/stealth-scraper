# Ultimate Stealth Web Scraper

## Complete Documentation

A comprehensive Python package for undetectable web scraping with human-like behavior simulation, advanced anti-detection techniques, and browser fingerprint masking.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
   - [HumanBehaviorConfig](#humanbehaviorconfig)
   - [StealthConfig](#stealthconfig)
4. [Core Classes](#core-classes)
   - [StealthBrowser](#stealthbrowser)
   - [HumanMouseSimulator](#humanmousesimulator)
   - [HumanScrollSimulator](#humanscrollsimulator)
   - [HumanTypingSimulator](#humantypingsimulator)
   - [BezierCurve](#beziercurve)
5. [Anti-Detection Features](#anti-detection-features)
6. [Examples](#examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.8+
- Google Chrome browser installed
- ChromeDriver (automatically managed by undetected-chromedriver)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install selenium>=4.15.0
pip install undetected-chromedriver>=3.5.0
pip install fake-useragent>=1.4.0
pip install numpy>=1.24.0
pip install scipy>=1.11.0
pip install selenium-stealth>=1.0.6
pip install webdriver-manager>=4.0.0
```

### Import the Package

```python
from stealth_scraper import (
    StealthBrowser,
    HumanBehaviorConfig,
    StealthConfig,
    create_stealth_browser,
)
from selenium.webdriver.common.by import By
```

---

## Quick Start

### Basic Usage

```python
from stealth_scraper import StealthBrowser

# Using context manager (recommended)
with StealthBrowser() as browser:
    browser.navigate("https://example.com")
    browser.simulate_reading()
    content = browser.get_page_source()
    print(f"Page loaded: {len(content)} characters")
```

### Manual Control

```python
from stealth_scraper import StealthBrowser

browser = StealthBrowser()
browser.start()

try:
    browser.navigate("https://example.com")
    browser.random_pause()
    browser.scroll.scroll_page("down")
finally:
    browser.close()
```

### Quick Factory Function

```python
from stealth_scraper import create_stealth_browser

# Create with custom settings in one line
browser = create_stealth_browser(
    min_mouse_speed=1.0,
    max_mouse_speed=3.0,
    spoof_timezone="America/New_York"
)
```

### High-Performance "Fast" Mode
For API-like scraping speeds while maintaining fingerprint protection:

```python
from stealth_scraper import create_stealth_browser, StealthLevel

browser = create_stealth_browser(
    level=StealthLevel.FAST, 
    headless=True,
    block_resources=True
)
```

---

## Configuration

### Preset Stealth Levels

Using proper levels significantly improves success rates.

```python
from stealth_scraper import StealthLevel

# Optimization Levels
StealthLevel.FAST     # API-speed (0ms delays), invisible. Best for public data.
StealthLevel.LOW      # Minimal delays, basic stealth. Good for simple sites.
StealthLevel.MEDIUM   # Balanced (Default). Good for most sites.
StealthLevel.HIGH     # Maximum human simulation. Best for tough anti-bot systems.
StealthLevel.PARANOID # Extreme stealth, forces headful mode.
```

### Custom Stealth Levels

Create your own reusable profiles by inheriting and overriding.

```python
from stealth_scraper import CustomStealthLevel, StealthLevel

# Create a "Fast but Valid" profile
MyProfile = CustomStealthLevel(
    base=StealthLevel.HIGH, # Start with strong fingerprinting
    
    # Override behavior for speed
    min_mouse_speed=0.1, 
    min_action_pause=0.1,
    headless=True
)

browser = create_stealth_browser(level=MyProfile)
```

### HumanBehaviorConfig


Controls human-like behavior simulation parameters.

```python
from stealth_scraper import HumanBehaviorConfig

config = HumanBehaviorConfig(
    # Mouse Movement
    min_mouse_speed=0.5,          # Minimum mouse movement duration (seconds)
    max_mouse_speed=2.0,          # Maximum mouse movement duration (seconds)
    mouse_curve_intensity=0.3,    # How curved the mouse path is (0.0-1.0)
    mouse_overshoot_chance=0.15,  # Probability of overshooting target
    mouse_jitter=True,            # Add small random movements along path
    
    # Scrolling
    scroll_style="smooth",        # Options: "smooth", "stepped", "mixed"
    min_scroll_pause=0.1,         # Minimum pause between scroll steps
    max_scroll_pause=0.5,         # Maximum pause between scroll steps
    scroll_variance=0.3,          # Variance in scroll distance (0.0-1.0)
    
    # Typing
    min_typing_delay=0.05,        # Minimum delay between keystrokes (seconds)
    max_typing_delay=0.25,        # Maximum delay between keystrokes (seconds)
    typo_chance=0.02,             # Probability of making/correcting a typo
    
    # General Behavior
    min_action_pause=0.3,         # Minimum pause between actions
    max_action_pause=2.0,         # Maximum pause between actions
    random_pause_chance=0.1,      # Chance of taking a longer "thinking" pause
    random_pause_duration=(2.0, 8.0),  # Duration range for thinking pauses
    
    # Reading Simulation
    reading_speed_wpm=250,        # Words per minute for reading simulation
    reading_variance=0.3,         # Variance in reading speed
)
```

#### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_mouse_speed` | float | 0.5 | Minimum time (seconds) to complete a mouse movement |
| `max_mouse_speed` | float | 2.0 | Maximum time (seconds) to complete a mouse movement |
| `mouse_curve_intensity` | float | 0.3 | Controls how curved mouse paths are. Higher = more curved |
| `mouse_overshoot_chance` | float | 0.15 | Probability (0-1) of overshooting the target and correcting |
| `mouse_jitter` | bool | True | Whether to add small random movements along the path |
| `scroll_style` | str | "smooth" | Scrolling style: "smooth" (CSS-like), "stepped" (mousewheel), "mixed" |
| `min_scroll_pause` | float | 0.1 | Minimum pause between scroll increments |
| `max_scroll_pause` | float | 0.5 | Maximum pause between scroll increments |
| `scroll_variance` | float | 0.3 | How much scroll distances vary from target |
| `min_typing_delay` | float | 0.05 | Fastest time between keystrokes |
| `max_typing_delay` | float | 0.25 | Slowest time between keystrokes |
| `typo_chance` | float | 0.02 | Probability of making a typo (then correcting it) |
| `min_action_pause` | float | 0.3 | Minimum random pause between browser actions |
| `max_action_pause` | float | 2.0 | Maximum random pause between browser actions |
| `random_pause_chance` | float | 0.1 | Probability of taking an extra long pause |
| `random_pause_duration` | tuple | (2.0, 8.0) | Range for extra long pauses |
| `reading_speed_wpm` | int | 250 | Simulated reading speed in words per minute |
| `reading_variance` | float | 0.3 | Variance in reading time calculation |

---

### StealthConfig

Controls anti-detection and browser stealth settings.

```python
from stealth_scraper import StealthConfig

config = StealthConfig(
    # Browser Fingerprint
    use_undetected_chrome=True,   # Use undetected-chromedriver library
    randomize_viewport=True,       # Randomize browser window size
    viewport_sizes=[               # Available viewport sizes to choose from
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1280, 720), (1600, 900), (1280, 800), (1680, 1050),
    ],
    
    # WebDriver Detection Evasion
    remove_webdriver_property=True,    # Remove navigator.webdriver flag
    mask_automation_indicators=True,   # Inject JS to mask automation signs
    
    # Request Patterns
    randomize_request_timing=True,     # Add random delays to requests
    min_page_load_wait=2.0,            # Minimum wait after page load
    max_page_load_wait=6.0,            # Maximum wait after page load
    
    # Session Behavior
    use_persistent_profile=False,      # Use a persistent Chrome profile
    profile_path=None,                 # Path to Chrome profile directory
    clear_cookies_chance=0.05,         # Probability of clearing cookies
    
    # Advanced Stealth Options
    disable_webrtc=True,               # Prevent WebRTC IP leak
    spoof_timezone=None,               # Spoof timezone (e.g., "America/New_York")
    spoof_locale=None,                 # Spoof locale (e.g., "en-US")
    spoof_geolocation=None,            # Spoof GPS: (latitude, longitude)
    block_images=False,                # Block image loading
    disable_notifications=True,        # Disable browser notifications
    disable_popup_blocking=False,      # Disable popup blocker
    use_selenium_stealth=True,         # Use selenium-stealth library
)
```

#### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_undetected_chrome` | bool | True | Use undetected-chromedriver instead of standard Chrome |
| `randomize_viewport` | bool | True | Randomly select viewport size from available options |
| `viewport_sizes` | list | [...] | List of (width, height) tuples for viewport randomization |
| `remove_webdriver_property` | bool | True | Remove the navigator.webdriver JavaScript property |
| `mask_automation_indicators` | bool | True | Inject JavaScript to hide automation indicators |
| `randomize_request_timing` | bool | True | Add random delays between requests |
| `min_page_load_wait` | float | 2.0 | Minimum seconds to wait after page loads |
| `max_page_load_wait` | float | 6.0 | Maximum seconds to wait after page loads |
| `use_persistent_profile` | bool | False | Persist browser profile between sessions |
| `profile_path` | str | None | Path to persistent Chrome profile directory |
| `clear_cookies_chance` | float | 0.05 | Probability of clearing cookies on session start |
| `disable_webrtc` | bool | True | Disable WebRTC to prevent IP address leaks |
| `spoof_timezone` | str | None | Override browser timezone (e.g., "Europe/London") |
| `spoof_locale` | str | None | Override browser locale (e.g., "fr-FR") |
| `spoof_geolocation` | tuple | None | Override GPS coordinates as (lat, lon) |
| `block_images` | bool | False | Block image loading (faster but less human-like) |
| `disable_notifications` | bool | True | Block notification permission requests |
| `disable_popup_blocking` | bool | False | Allow popups |
| `use_selenium_stealth` | bool | True | Apply selenium-stealth library patches |
| `visualize_mouse` | bool | False | Enable hardware-accelerated red dot for debugging |
| `identity` | enum | GHOST | Fingerprint strategy (GHOST or CONSISTENT) |
| `location` | object | None | Geographic context (Timezone, Geo, Locale) |
| `block_resources` | bool | False | Block images/CSS/fonts for extreme speed |

---

### Identity & Location (Phase 2)

Control the browser's fingerprint consistency and geospatial context.

```python
from stealth_scraper import StealthIdentity, StealthLocation

# Identity presets
StealthIdentity.GHOST        # Random every session
StealthIdentity.CONSISTENT   # Deterministic seeded values

# Location presets
StealthLocation.US()    # en-US, NYC
StealthLocation.UK()    # en-GB, London
StealthLocation.Tokyo() # ja-JP, Tokyo
```

---

## Core Classes

### StealthBrowser

The main class for stealth web scraping. Combines all anti-detection features with human behavior simulation.

#### Constructor

```python
browser = StealthBrowser(
    behavior_config: Optional[HumanBehaviorConfig] = None,
    stealth_config: Optional[StealthConfig] = None,
)
```

#### Methods

##### `start() -> StealthBrowser`
Initialize and start the browser. Returns self for chaining.

```python
browser = StealthBrowser()
browser.start()
# Browser is now running
```

##### `close() -> None`
Close the browser and clean up resources.

```python
browser.close()
```

##### `navigate(url: str) -> None`
Navigate to a URL with human-like behavior (random wait after load, possible scroll).

```python
browser.navigate("https://example.com")
```

##### `wait_for_element(by: By, value: str, timeout: float = 10, condition: str = "presence")`
Wait for an element to appear on the page.

**Parameters:**
- `by`: Selenium By locator (e.g., `By.ID`, `By.CSS_SELECTOR`)
- `value`: The locator value
- `timeout`: Maximum seconds to wait
- `condition`: One of "presence", "visible", "clickable"

```python
from selenium.webdriver.common.by import By

# Wait for element to exist in DOM
element = browser.wait_for_element(By.ID, "submit-btn")

# Wait for element to be visible
element = browser.wait_for_element(By.CSS_SELECTOR, ".modal", condition="visible")

# Wait for element to be clickable
element = browser.wait_for_element(By.XPATH, "//button", timeout=15, condition="clickable")
```

##### `click_element(element, scroll_first: bool = True) -> None`
Click an element with human-like mouse movement.

```python
button = browser.wait_for_element(By.ID, "submit")
browser.click_element(button)

# Skip scrolling if element is already visible
browser.click_element(button, scroll_first=False)
```

##### `type_into(element, text: str, scroll_first: bool = True) -> None`
Type text into an input element with human-like delays and occasional typos.

```python
search_box = browser.wait_for_element(By.NAME, "q")
browser.type_into(search_box, "stealth web scraping python")
```

##### `simulate_window_switching() -> None`
Simulate tabbing away and back (Focus/Blur events).

##### `simulate_shortcut(keys: List[str]) -> None`
Simulate a keyboard shortcut using CDP (e.g., `["Control", "c"]`).

##### `random_pause(min_time: float = None, max_time: float = None) -> None`
Take a random pause. If the pause is > 1s, the browser will occasionally perform "Idle Entropy" (micro mouse drifts).

##### `simulate_reading(word_count: int = None) -> None`
Simulate reading the page content with scrolling.

```python
# Auto-detect word count from page
browser.simulate_reading()

# Specify expected word count
browser.simulate_reading(word_count=500)
```

##### `random_mouse_movement() -> None`
Move the mouse to a random position on the page.

```python
browser.random_mouse_movement()
```

##### `get_page_source() -> str`
Get the current page HTML source.

```python
html = browser.get_page_source()
```

##### `get_current_url() -> str`
Get the current page URL.

```python
url = browser.get_current_url()
```

##### `execute_script(script: str) -> Any`
Execute JavaScript on the page.

```python
title = browser.execute_script("return document.title;")
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

##### `save_screenshot(path: str) -> None`
Save a screenshot of the current page.

```python
browser.save_screenshot("screenshot.png")
```

#### Properties

- `driver`: Direct access to the Selenium WebDriver instance
- `mouse`: Access to HumanMouseSimulator
- `scroll`: Access to HumanScrollSimulator
- `typing`: Access to HumanTypingSimulator

```python
# Direct driver access for advanced operations
browser.driver.find_elements(By.TAG_NAME, "a")

# Use simulators directly
browser.scroll.scroll_page("down", 0.5)
browser.mouse.move_to(500, 300)
```

---

### HumanMouseSimulator

Simulates realistic human mouse movements using Bezier curves.

#### Methods

##### `move_to(x: int, y: int, click: bool = False) -> None`
Move mouse to absolute coordinates with human-like curved motion.

```python
browser.mouse.move_to(500, 300)           # Move only
browser.mouse.move_to(500, 300, click=True)  # Move and click
```

##### `move_to_element(element, click: bool = False) -> None`
Move mouse to a web element (clicks at random position within element, not center).

```python
button = browser.driver.find_element(By.ID, "submit")
browser.mouse.move_to_element(button, click=True)
```

---

### HumanScrollSimulator

Simulates realistic human scrolling behavior.

#### Methods

##### `scroll_to(target_y: int, style: str = None) -> None`
Scroll to an absolute Y position.

```python
browser.scroll.scroll_to(1000)                    # Use default style
browser.scroll.scroll_to(1000, style="smooth")    # Force smooth scroll
browser.scroll.scroll_to(1000, style="stepped")   # Force stepped scroll
```

##### `scroll_page(direction: str = "down", amount: float = 0.7) -> None`
Scroll by a portion of the viewport.

```python
browser.scroll.scroll_page("down")          # Scroll down 70% of viewport
browser.scroll.scroll_page("down", 0.5)     # Scroll down 50%
browser.scroll.scroll_page("up", 0.3)       # Scroll up 30%
```

##### `scroll_to_element(element, align: str = "center") -> None`
Scroll to bring an element into view.

```python
element = browser.driver.find_element(By.ID, "target")
browser.scroll.scroll_to_element(element)                # Center element
browser.scroll.scroll_to_element(element, align="top")   # Element at top
browser.scroll.scroll_to_element(element, align="bottom") # Element at bottom
```

---

### HumanTypingSimulator

Simulates realistic human typing with variable delays and typos.

#### Methods

##### `type_text(element, text: str, clear_first: bool = True) -> None`
Type text into an element with human-like behavior.

```python
input_field = browser.driver.find_element(By.NAME, "username")
browser.typing.type_text(input_field, "myusername")

# Don't clear existing text
browser.typing.type_text(input_field, " additional text", clear_first=False)
```

---

### BezierCurve

Utility class for generating natural curved paths.

#### Static Methods

##### `generate_curve(start, end, control_points=2, intensity=0.3) -> List[Tuple[int, int]]`
Generate a bezier curve path between two points.

```python
from stealth_scraper import BezierCurve

path = BezierCurve.generate_curve(
    start=(0, 0),
    end=(500, 300),
    control_points=3,
    intensity=0.4
)
# Returns: [(0, 0), (15, 8), (32, 18), ..., (500, 300)]
```

##### `calculate_point(t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]`
Calculate a single point on a bezier curve at parameter t (0-1).

```python
point = BezierCurve.calculate_point(0.5, [(0, 0), (100, 200), (500, 300)])
```

---

## Anti-Detection Features

### Chrome Arguments Applied

The scraper applies numerous Chrome arguments to avoid detection:

**Core Anti-Detection:**
- `--disable-blink-features=AutomationControlled` — Removes automation flag
- `--disable-features=AutomationControlled` — Additional automation removal
- `--disable-infobars` — Removes "Chrome is being controlled" banner

**Fingerprint Evasion:**
- `--disable-features=OptimizationGuideModelDownloading` — Prevents detectable downloads
- `--disable-features=TranslateUI` — Disables translation prompts
- `--log-level=3`, `--silent`, `--disable-logging` — Hides logging artifacts

**WebRTC Protection:**
- `--disable-webrtc` — Prevents IP leaks
- `--enforce-webrtc-ip-permission-check` — Additional WebRTC protection

**Performance/Stealth Balance:**
- `--enable-accelerated-2d-canvas` — Enables GPU for realistic fingerprint
- `--enable-accelerated-video-decode` — Standard browser behavior

### JavaScript Fingerprint Masking

The scraper injects JavaScript to mask:

- `navigator.webdriver` — Set to undefined
- `chrome.runtime` — Mocked with realistic implementation
- `chrome.loadTimes()` — Returns realistic timing data
- `chrome.csi()` — Returns realistic performance data
- `navigator.plugins` — Shows PDF Plugin, Native Client
- `navigator.languages` — Returns ["en-US", "en"]
- `navigator.hardwareConcurrency` — Random: 4, 8, 12, or 16 cores
- `navigator.deviceMemory` — Random: 4, 8, or 16 GB
- `navigator.maxTouchPoints` — Set to 0 (desktop)

### Canvas Fingerprinting Protection

- Adds imperceptible noise to `fillText` and `strokeText`
- Modifies `toDataURL` output slightly
- Prevents consistent canvas fingerprints

### WebGL Fingerprinting Protection

- Spoofs `UNMASKED_VENDOR_WEBGL` to "Intel Inc."
- Spoofs `UNMASKED_RENDERER_WEBGL` to realistic GPU strings
- Handles both WebGL1 and WebGL2 contexts

### Audio Fingerprinting Protection

- Adds tiny noise to `AudioBuffer.getChannelData`
- Slightly modifies oscillator frequencies

### CDP (Chrome DevTools Protocol) Features

- Timezone spoofing via `Emulation.setTimezoneOverride`
- Geolocation spoofing via `Emulation.setGeolocationOverride`
- Locale spoofing via `Emulation.setLocaleOverride`
- User agent consistency via `Emulation.setUserAgentOverride`

---

## Examples

### Example 1: Basic Web Scraping

```python
from stealth_scraper import StealthBrowser
from selenium.webdriver.common.by import By

with StealthBrowser() as browser:
    browser.navigate("https://quotes.toscrape.com")
    
    # Wait and scroll like a human
    browser.simulate_reading()
    
    # Extract quotes
    quotes = browser.driver.find_elements(By.CLASS_NAME, "quote")
    for quote in quotes:
        text = quote.find_element(By.CLASS_NAME, "text").text
        author = quote.find_element(By.CLASS_NAME, "author").text
        print(f"{text} - {author}")
```

### Example 2: Form Interaction

```python
from stealth_scraper import StealthBrowser, HumanBehaviorConfig
from selenium.webdriver.common.by import By

# Slower, more careful typing
behavior = HumanBehaviorConfig(
    min_typing_delay=0.1,
    max_typing_delay=0.35,
    typo_chance=0.03,
)

with StealthBrowser(behavior_config=behavior) as browser:
    browser.navigate("https://example.com/login")
    
    # Find and fill form
    username = browser.wait_for_element(By.NAME, "username", condition="visible")
    browser.type_into(username, "my_username")
    
    browser.random_pause()
    
    password = browser.wait_for_element(By.NAME, "password", condition="visible")
    browser.type_into(password, "my_password")
    
    browser.random_pause()
    
    # Click submit
    submit = browser.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
    browser.click_element(submit)
```

### Example 3: Infinite Scroll Handling

```python
from stealth_scraper import StealthBrowser
from selenium.webdriver.common.by import By

with StealthBrowser() as browser:
    browser.navigate("https://example.com/infinite-scroll")
    
    collected_items = []
    last_count = 0
    max_scrolls = 20
    
    for i in range(max_scrolls):
        # Get current items
        items = browser.driver.find_elements(By.CSS_SELECTOR, ".item")
        
        for item in items[last_count:]:
            collected_items.append(item.text)
        
        last_count = len(items)
        
        # Human-like scrolling
        browser.scroll.scroll_page("down", 0.8)
        browser.random_pause(1.0, 3.0)
        
        # Occasional scroll back up (humans do this)
        if i % 4 == 0 and i > 0:
            browser.scroll.scroll_page("up", 0.2)
            browser.random_pause(0.5, 1.5)
        
        # Random mouse movement
        if i % 2 == 0:
            browser.random_mouse_movement()
        
        print(f"Scroll {i+1}: {len(collected_items)} items")
    
    print(f"Total collected: {len(collected_items)}")
```

### Example 4: Geolocation Spoofing

```python
from stealth_scraper import StealthBrowser, StealthConfig

# Spoof location to New York City
stealth = StealthConfig(
    spoof_timezone="America/New_York",
    spoof_geolocation=(40.7128, -74.0060),  # NYC coordinates
    spoof_locale="en-US",
)

with StealthBrowser(stealth_config=stealth) as browser:
    browser.navigate("https://whatismyipaddress.com")
    browser.simulate_reading()
    browser.save_screenshot("location_test.png")
```

### Example 5: Persistent Profile

```python
from stealth_scraper import StealthBrowser, StealthConfig

stealth = StealthConfig(
    use_persistent_profile=True,
    profile_path="/tmp/my_chrome_profile",
)

# First session - log in
with StealthBrowser(stealth_config=stealth) as browser:
    browser.navigate("https://example.com/login")
    # ... perform login ...
    browser.random_pause(2.0, 4.0)

# Second session - already logged in!
with StealthBrowser(stealth_config=stealth) as browser:
    browser.navigate("https://example.com/dashboard")
    # Cookies are preserved, should be logged in
```

### Example 6: Multi-Page Navigation

```python
from stealth_scraper import StealthBrowser, HumanBehaviorConfig, StealthConfig
from selenium.webdriver.common.by import By

behavior = HumanBehaviorConfig(
    reading_speed_wpm=200,
    random_pause_chance=0.15,
)

stealth = StealthConfig(
    min_page_load_wait=3.0,
    max_page_load_wait=7.0,
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
        browser.simulate_reading()
        
        # Random mouse movements
        browser.random_mouse_movement()
        browser.random_pause()
        
        # Scroll around naturally
        browser.scroll.scroll_page("down", 0.5)
        browser.random_pause()
        browser.scroll.scroll_page("down", 0.3)
        browser.random_pause()
        
        # Collect data
        try:
            title = browser.driver.find_element(By.TAG_NAME, "h1").text
            results.append({"url": url, "title": title})
        except:
            pass
        
        # Longer pause between pages
        browser.random_pause(2.0, 5.0)
```

---

## Best Practices

### 1. Use Realistic Timing

```python
# BAD - Too fast
config = HumanBehaviorConfig(
    min_action_pause=0.0,
    max_action_pause=0.1,
)

# GOOD - Human-like
config = HumanBehaviorConfig(
    min_action_pause=0.5,
    max_action_pause=3.0,
    random_pause_chance=0.2,
)
```

### 2. Vary Your Behavior

```python
# Add randomness to your scraping pattern
for page in pages:
    browser.navigate(page)
    
    # Don't always do the same thing
    if random.random() < 0.3:
        browser.random_mouse_movement()
    
    if random.random() < 0.2:
        browser.scroll.scroll_page("up", 0.1)
    
    browser.random_pause()
```

### 3. Handle Errors Gracefully

```python
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    element = browser.wait_for_element(By.ID, "target", timeout=10)
    browser.click_element(element)
except TimeoutException:
    print("Element not found, skipping...")
    browser.save_screenshot("error_timeout.png")
except NoSuchElementException:
    print("Element disappeared, retrying...")
```

### 4. Use Persistent Profiles for Sessions

```python
# For sites requiring login, use persistent profiles
stealth = StealthConfig(
    use_persistent_profile=True,
    profile_path="/path/to/profile",
)
```

### 5. Respect Rate Limits

```python
import time
import random

for url in urls:
    browser.navigate(url)
    # ... scrape data ...
    
    # Wait 5-15 seconds between pages
    time.sleep(random.uniform(5, 15))
```

---

## Troubleshooting

### Chrome Not Starting

**Problem:** Browser fails to start

**Solutions:**
1. Ensure Chrome is installed and up to date
2. Check that chromedriver version matches Chrome version
3. Try with `use_undetected_chrome=False` to use standard Selenium

### Still Getting Detected

**Problem:** Bot detection systems still blocking

**Solutions:**
1. Slow down your scraping speed
2. Use residential proxies
3. Enable persistent profiles
4. Add more random pauses and mouse movements
5. Try different viewport sizes

### WebRTC Leak

**Problem:** Real IP leaking through WebRTC

**Solution:** Ensure `disable_webrtc=True` in StealthConfig

### Timezone Mismatch

**Problem:** Timezone not matching spoofed location

**Solution:** Set both `spoof_timezone` and `spoof_geolocation` together

```python
stealth = StealthConfig(
    spoof_timezone="America/Los_Angeles",
    spoof_geolocation=(34.0522, -118.2437),  # Los Angeles
)
```

### Memory Issues

**Problem:** Browser consuming too much memory

**Solutions:**
1. Close browser between batches
2. Use `block_images=True` for faster, lighter operation
3. Clear cookies periodically

---

## License

This package is provided for educational purposes. Use responsibly and respect website terms of service.

---

## Support

For issues and feature requests, please create an issue in the repository.
