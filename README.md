# 🥷 Ultimate Stealth Web Scraper

[User Guide](docs/GUIDE.md) | [Configuration](docs/CONFIGURATION.md) | [API Reference](docs/API_REFERENCE.md) | [Stealth Engine](docs/STEALTH_ENGINE.md)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.15+-green.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

> **Undetectable web scraping with human-like behavior simulation.**

A powerful Python package that combines advanced anti-detection techniques with realistic human behavior simulation to scrape websites without triggering bot detection systems.

<p align="center">
  <img src="https://img.shields.io/badge/Bot%20Detection-Bypassed-success?style=for-the-badge" alt="Bot Detection Bypassed"/>
  <img src="https://img.shields.io/badge/Fingerprint-Masked-success?style=for-the-badge" alt="Fingerprint Masked"/>
  <img src="https://img.shields.io/badge/Behavior-Human--Like-success?style=for-the-badge" alt="Human-Like Behavior"/>
</p>

---

## ✨ Features

### 🛡️ Anti-Detection Arsenal

| Feature | Description |
|---------|-------------|
| **Undetected ChromeDriver** | Patched driver that bypasses Cloudflare, DataDome, and more |
| **WebDriver Masking** | Removes `navigator.webdriver` and automation indicators |
| **Fingerprint Spoofing** | Randomizes canvas, WebGL, audio, and hardware fingerprints |
| **WebRTC Protection** | Prevents real IP leakage through WebRTC |
| **CDP Integration** | Chrome DevTools Protocol for timezone, geolocation & locale spoofing |
| **Network Stealth** | Synchronizes `Accept-Language` headers with spoofed locale |
| **Advanced Masking** | Spoofs Font metrics, AudioContext data, and WebGL parameters |

### 🎭 Human Behavior Simulation

| Feature | Description |
|---------|-------------|
| **Bezier Mouse Curves** | Natural curved mouse movements, not straight lines |
| **Variable Speed** | Slow start/end, fast middle — like real hand movement |
| **Mouse Overshoot** | Occasionally overshoots target and corrects |
| **Realistic Scrolling** | Smooth or stepped scrolling with random pauses |
| **Human Typing** | Variable delays, typos with corrections, thinking pauses |
| **Reading Simulation** | Calculates realistic reading time with natural scrolling |
| **Window Switching** | Simulates focus/blur events as if user tabbed away |
| **Idle Entropy** | Mouse makes tiny "micro-movements" instead of freezing when idle |
| **Keyboard Shortcuts** | Simulates realistic `Ctrl+C`, `Ctrl+T` etc. key presses |

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from stealth_scraper import StealthBrowser

with StealthBrowser() as browser:
    browser.navigate("https://example.com")
    browser.simulate_reading()
    
    print(browser.get_page_source())
```

### Form Interaction

```python
from stealth_scraper import StealthBrowser
from selenium.webdriver.common.by import By

with StealthBrowser() as browser:
    browser.navigate("https://example.com/login")
    
    # Human-like typing with occasional typos
    username = browser.wait_for_element(By.NAME, "username")
    browser.type_into(username, "my_username")
    
    browser.random_pause()
    
    password = browser.wait_for_element(By.NAME, "password")
    browser.type_into(password, "my_password")
    
    # Click with natural mouse movement
    submit = browser.wait_for_element(By.CSS_SELECTOR, "button[type='submit']")
    browser.click_element(submit)
```

---

## 🎚️ Preset Stealth Levels

Don't want to configure everything manually? Use preset stealth levels:

### Quick Start with Presets

```python
from stealth_scraper import StealthLevel, create_browser_with_level

# LOW: Fast, minimal stealth (basic anti-detection only)
with create_browser_with_level(StealthLevel.LOW) as browser:
    browser.navigate("https://example.com")

# MEDIUM: Balanced (recommended for most sites)
with create_browser_with_level(StealthLevel.MEDIUM) as browser:
    browser.navigate("https://example.com")

# HIGH: Maximum stealth (slower but most human-like)
with create_browser_with_level(StealthLevel.HIGH) as browser:
    browser.navigate("https://example.com")
```

### Modular Configuration (New!)

```python
from stealth_scraper import create_stealth_browser, StealthIdentity, StealthLocation

# 1. Consistent Identity (Safe for logging in)
# Uses a deterministic seed so your "hardware" fingerprint looks the same every time
browser = create_stealth_browser(
    identity=StealthIdentity.CONSISTENT, 
    identity_seed="my_google_account_1"
)

# 2. Location Context (Travel to Tokyo)
# Auto-sets Timezone, Geolocation, Locale, and Languages
browser = create_stealth_browser(
    location=StealthLocation.Tokyo()
)
```

### Stealth Level Comparison

| Feature | LOW | MEDIUM | HIGH |
|---------|-----|--------|------|
| **Mouse Speed** | 0.3-0.8s | 0.4-1.0s | 0.8-1.8s |
| **Typing Speed** | 0.03-0.12s | 0.05-0.15s | 0.08-0.25s |
| **Typos** | None | 0.5% | 1.5% |
| **Hesitation** | None | Low | Medium |
| **Fingerprint** | Standard | Masked | Masked + Noise |

### ⚠️ Headless vs. Headful: The Trade-off

Running `headless=True` (invisible) is convenient but comes with risks:

| Configuration | Behavioral Stealth | Fingerprint Stealth | Best For |
| :--- | :--- | :--- | :--- |
| **High + Headful** | ⭐⭐⭐⭐⭐ (Perfect) | ⭐⭐⭐⭐⭐ (Perfect) | Paranoid sites, Login, Ticketmaster |
| **High + Headless** | ⭐⭐⭐⭐⭐ (Perfect) | ⭐⭐⭐⭐ (Near Perfect) | Background farming, 95% of sites |
| **Fast + Headless** | ⭐ (Bot-like) | ⭐⭐⭐⭐ (Near Perfect) | API scraping, Public data |

> **Note**: Even with our advanced patching, **Headless Chrome** has subtle rendering differences (font smoothing, 3D timing) that extremely advanced trackers *can* detect. For maximum safety ("God Mode"), always use `headless=False`.

### Custom Stealth Levels
For advanced users, you can define your own reusable stealth level by inheriting from a base level and overriding specific settings.

```python
from stealth_scraper import create_stealth_browser, StealthLevel, CustomStealthLevel

# Define a "Fast but Careful" profile
# Inherits HIGH stealth (mouse curves) but speeds it up
MyScraperProfile = CustomStealthLevel(
    base=StealthLevel.HIGH,
    
    # Overrides (Any HumanBehaviorConfig or StealthConfig field)
    min_mouse_speed=0.1,      # Much faster mouse
    block_resources=True,     # Block images for speed
    typo_chance=0.0,          # No typos
    headless=True             # Invisible
)

browser = create_stealth_browser(level=MyScraperProfile)
```

#### Available Settings (Overrides)
You can override any of these parameters in `CustomStealthLevel`:

**Behavior (HumanMouseSimulator)**
*   `min_mouse_speed` / `max_mouse_speed` (float): Seconds to move mouse. 0.0 = Teleport.
*   `mouse_curve_intensity` (float): 0.1 (straight) to 1.0 (wild).
*   `min_typing_delay` / `max_typing_delay` (float): Seconds between keystrokes.
*   `typo_chance` (float): 0.0 to 1.0.
*   `min_action_pause` / `max_action_pause` (float): Seconds to wait after clicking/typing.

**Stealth (Browser Fingerprint)**
*   `headless` (bool): Run invisible.
*   `block_resources` (bool): Block images/fonts/CSS.
*   `mask_automation_indicators` (bool): Hide `navigator.webdriver`.
*   `disable_webrtc` (bool): Prevent IP leak.
*   `spoof_user_agent` (bool): Use real-world UA.
*   `use_selenium_stealth` (bool): Enable extra detected-chromedriver patches.

### With Custom Overrides

```python
# Start with a preset and add custom spoofing
with create_browser_with_level(
    StealthLevel.MEDIUM,
    spoof_timezone="America/New_York",
    spoof_geolocation=(40.7128, -74.0060),
    spoof_locale="en-US"
) as browser:
    browser.navigate("https://example.com")
```

### Manual Configuration from Preset

```python
from stealth_scraper import get_stealth_config, StealthBrowser, StealthLevel

# Get preset configurations
behavior, stealth = get_stealth_config(StealthLevel.HIGH)

# Modify as needed
stealth.spoof_timezone = "Europe/London"
behavior.reading_speed_wpm = 180

# Use modified config
with StealthBrowser(behavior_config=behavior, stealth_config=stealth) as browser:
    browser.navigate("https://example.com")
```

---

## ⚙️ Configuration

### Human Behavior Settings

```python
from stealth_scraper import StealthBrowser, HumanBehaviorConfig

config = HumanBehaviorConfig(
    # Mouse
    min_mouse_speed=0.5,
    max_mouse_speed=2.0,
    mouse_curve_intensity=0.3,
    mouse_overshoot_chance=0.15,
    
    # Typing
    min_typing_delay=0.05,
    max_typing_delay=0.25,
    typo_chance=0.02,
    
    # Scrolling
    scroll_style="smooth",  # or "stepped", "mixed"
    
    # Pauses
    random_pause_chance=0.1,
    reading_speed_wpm=250,
)

with StealthBrowser(behavior_config=config) as browser:
    # Your scraping code
    pass
```

### Stealth Settings

```python
from stealth_scraper import StealthBrowser, StealthConfig

config = StealthConfig(
    # Anti-detection
    use_undetected_chrome=True,
    mask_automation_indicators=True,
    disable_webrtc=True,

    # Spoofing
    spoof_timezone="America/New_York",
    spoof_geolocation=(40.7128, -74.0060),
    spoof_locale="en-US",

    # Session
    use_persistent_profile=True,
    profile_path="/path/to/profile",
)

with StealthBrowser(stealth_config=config) as browser:
    # Your scraping code
    pass
```

### Identity & Location Modularity (New!)

```python
from stealth_scraper import create_stealth_browser, StealthIdentity, StealthLocation

# 1. Consistent Identity (Safe for logging in)
# Uses a deterministic seed so your "hardware" fingerprint looks the same every time
browser = create_stealth_browser(
    identity=StealthIdentity.CONSISTENT, 
    identity_seed="my_google_account_1"
)

# 2. Location Context (Travel to Tokyo)
# Auto-sets Timezone, Geolocation, Locale, and Languages
browser = create_stealth_browser(
    location=StealthLocation.Tokyo()
)
```

---

## 🎯 API Reference

### Factory Functions

| Function | Description |
|----------|-------------|
| `create_browser_with_level(level, **overrides)` | Create browser with preset stealth level |
| `get_stealth_config(level)` | Get preset configs for manual modification |
| `create_stealth_browser(**kwargs)` | Create browser with custom configuration |

### StealthLevel Enum

```python
StealthLevel.LOW      # Fast, minimal stealth
StealthLevel.MEDIUM   # Balanced (default)
StealthLevel.HIGH     # Maximum stealth
StealthLevel.PARANOID # Alias for HIGH
```

### Identity & Location

```python
from stealth_scraper import StealthIdentity, StealthLocation

# Identity Strategies
StealthIdentity.GHOST        # Random every session (Default)
StealthIdentity.CONSISTENT   # Consistent based on seed/profile

# Location Presets
StealthLocation.US()    # New York, en-US
StealthLocation.UK()    # London, en-GB
StealthLocation.Tokyo() # Tokyo, ja-JP
```


### Headless & Fast Mode (New!)

To run invisible scraping at maximum speed (API-like throughput):

```python
# The "Turbo Scraper" Pattern
browser = create_stealth_browser(
    level=StealthLevel.FAST,       # Teleporting mouse, instant typing
    headless=True,                 # Invisible (--headless=new)
    block_resources=True           # Block images/css/fonts (5x speed)
)

with browser:
    browser.navigate("https://api-like-site.com")
    # Interactions are instant (0ms delay)
    browser.click() 
```

### StealthBrowser Interface
The browser object now exposes convenience methods for direct interaction:

| Method | Description |
| :--- | :--- |
| `navigate(url)` | Go to a URL (human-like loading). |
| `move_to(x, y)` | Move mouse (Curve or Teleport based on level). |
| `click()` | Click at current mouse position. |
| `type_text(text)` | Type text with human logic (typos/delays). |
| `save_screenshot(path)` | Save debug screenshot. |
| `click_element(element, scroll_first)` | Human-like click with mouse movement |
| `type_into(element, text)` | Type with realistic delays and typos |
| `random_pause(min, max)` | Random wait between actions |
| `simulate_reading(word_count)` | Simulate reading with scrolling |
| `random_mouse_movement()` | Move mouse to random position |
| `save_screenshot(path)` | Save screenshot |

### Direct Simulator Access

```python
# Mouse movements
browser.mouse.move_to(x, y, click=True)
browser.mouse.move_to_element(element)

# Scrolling
browser.scroll.scroll_page("down", amount=0.7)
browser.scroll.scroll_to_element(element)
browser.scroll.scroll_to(y_position)

# Typing
browser.typing.type_text(element, "text", clear_first=True)

# Advanced Behavior
browser.simulate_window_switching() # Simulates tabbing away and back
browser.simulate_shortcut(['Control', 't']) # Press Ctrl+T

```

---

## 🔒 Anti-Detection Techniques

### Browser Fingerprint Masking

```
✅ navigator.webdriver = undefined
✅ chrome.runtime mocked with realistic implementation
✅ Plugins array shows PDF Plugin, Native Client
✅ Hardware concurrency randomized (4/8/12/16 cores)
✅ Device memory randomized (4/8/16 GB)
✅ Canvas fingerprint noise injection
✅ WebGL vendor/renderer spoofing (NVIDIA/Intel)
✅ AudioContext fingerprint protection (noise injection)
✅ Font metrics randomization (offset width/height)
✅ Battery API spoofing
✅ Screen resolution & window dimension synchronization
✅ Network headers (`Accept-Language`) matched to locale
```

### Chrome Flags Applied

```
--disable-blink-features=AutomationControlled
--disable-features=AutomationControlled
--disable-features=OptimizationGuideModelDownloading
--disable-webrtc
--disable-notifications
--disable-popup-blocking
+ 30 more stealth flags
```

---

## 📖 Examples

### Infinite Scroll Scraping

```python
with StealthBrowser() as browser:
    browser.navigate("https://example.com/feed")
    
    items = []
    for i in range(10):
        # Collect items
        elements = browser.driver.find_elements(By.CSS_SELECTOR, ".item")
        items.extend([e.text for e in elements])
        
        # Human-like scrolling
        browser.scroll.scroll_page("down", 0.8)
        browser.random_pause(1.0, 3.0)
        
        # Occasional scroll back (humans do this)
        if i % 3 == 0:
            browser.scroll.scroll_page("up", 0.2)
            browser.random_mouse_movement()
```

### Location-Based Scraping

```python
config = StealthConfig(
    spoof_timezone="Europe/London",
    spoof_geolocation=(51.5074, -0.1278),  # London
    spoof_locale="en-GB",
)

with StealthBrowser(stealth_config=config) as browser:
    browser.navigate("https://example.com/local-deals")
    # See London-specific content
```

### Session Persistence

```python
config = StealthConfig(
    use_persistent_profile=True,
    profile_path="/tmp/my_session",
)

# First run: Login
with StealthBrowser(stealth_config=config) as browser:
    browser.navigate("https://example.com/login")
    # ... login flow ...

# Second run: Already logged in!
with StealthBrowser(stealth_config=config) as browser:
    browser.navigate("https://example.com/dashboard")
    # Cookies preserved, session active
```

---

## 📋 Requirements

- **Python** 3.8+
- **Google Chrome** (latest version recommended)
- **Dependencies:**
  ```
  selenium>=4.15.0
  undetected-chromedriver>=3.5.0
  fake-useragent>=1.4.0
  numpy>=1.24.0
  scipy>=1.11.0
  selenium-stealth>=1.0.6
  webdriver-manager>=4.0.0
  ```

---

## 📁 Package Structure

```
├── docs/                # Full Documentation
│   ├── GUIDE.md            # Getting Started
│   ├── CONFIGURATION.md    # Settings Deep Dive
│   ├── API_REFERENCE.md    # Method Listing
│   ├── STEALTH_ENGINE.md   # Technical Details
│   └── TROUBLESHOOTING.md  # Known Issues
├── tests/               # Comprehensive test suite
│   ├── test_external_bypass.py    # Bypassing external defenses
│   ├── test_local_mechanics.py     # Verifying internal logic (mouse, typing)
│   ├── test_identity_spoofing.py   # Geolocation, Timezone, Locale
│   ├── test_resource_blocking.py   # CDP Resource Interception
│   ├── test_behavior_advanced.py   # Typos, Shortcuts, Window focus
│   └── test_headless_benchmark.py  # Performance & headless checks
├── examples/            # Usage examples
├── requirements.txt         # Dependencies
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── DOCUMENTATION.md        # Full API documentation
└── LICENSE                 # MIT License
```

---

## ⚠️ Disclaimer

This tool is provided for **educational and research purposes only**. Users are responsible for ensuring their use complies with:

- Website Terms of Service
- Applicable laws and regulations
- Ethical scraping practices

Always respect `robots.txt` and rate limits. Consider using official APIs when available.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Happy Scraping! 🕷️</b>
</p>
