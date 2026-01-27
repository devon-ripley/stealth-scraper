# 🥷 Ultimate Stealth Web Scraper

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

### 🎭 Human Behavior Simulation

| Feature | Description |
|---------|-------------|
| **Bezier Mouse Curves** | Natural curved mouse movements, not straight lines |
| **Variable Speed** | Slow start/end, fast middle — like real hand movement |
| **Mouse Overshoot** | Occasionally overshoots target and corrects |
| **Realistic Scrolling** | Smooth or stepped scrolling with random pauses |
| **Human Typing** | Variable delays, typos with corrections, thinking pauses |
| **Reading Simulation** | Calculates realistic reading time with natural scrolling |

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

### Stealth Level Comparison

| Feature | LOW | MEDIUM | HIGH |
|---------|-----|--------|------|
| **Speed** | Fast | Balanced | Slow |
| **Mouse Speed** | 0.3-0.8s | 0.5-2.0s | 1.0-3.0s |
| **Typing Speed** | 0.03-0.12s | 0.05-0.25s | 0.1-0.35s |
| **Typos** | None | 2% | 3% |
| **Random Pauses** | None | 10% | 20% |
| **Page Load Wait** | 0.5-1.5s | 2.0-6.0s | 4.0-8.0s |
| **Undetected Chrome** | ✓ | ✓ | ✓ |
| **Selenium-Stealth** | ✗ | ✓ | ✓ |
| **WebRTC Protection** | ✗ | ✓ | ✓ |
| **Use Case** | Weak detection | Most sites | Strong detection |

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

### Proxy Settings (DataImpulse)

```python
from stealth_scraper import StealthBrowser, ProxyConfig

proxy = ProxyConfig(
    enabled=True,
    username="your_username",
    password="your_password",
    host="gw.dataimpulse.com",  # Default
    port=823,                    # Default
    country="us",                # ISO country code
    city="newyork",              # Optional: city-level targeting (doubles cost)
)

with StealthBrowser(proxy_config=proxy) as browser:
    # Your scraping code with rotating residential proxies
    pass
```

**Note:** City-level targeting doubles the rate (~$2/GB vs ~$1/GB).

---

## 🎯 API Reference

### Factory Functions

| Function | Description |
|----------|-------------|
| `create_browser_with_level(level, proxy_config, **overrides)` | Create browser with preset stealth level |
| `get_stealth_config(level)` | Get preset configs for manual modification |
| `create_stealth_browser(**kwargs)` | Create browser with custom configuration |

### StealthLevel Enum

```python
StealthLevel.LOW      # Fast, minimal stealth
StealthLevel.MEDIUM   # Balanced (default)
StealthLevel.HIGH     # Maximum stealth
StealthLevel.PARANOID # Alias for HIGH
```

### StealthBrowser

| Method | Description |
|--------|-------------|
| `navigate(url)` | Navigate with random post-load wait |
| `wait_for_element(by, value, timeout, condition)` | Wait for element (presence/visible/clickable) |
| `click_element(element, scroll_first)` | Human-like click with mouse movement |
| `type_into(element, text)` | Type with realistic delays and typos |
| `random_pause(min, max)` | Random wait between actions |
| `simulate_reading(word_count)` | Simulate reading with scrolling |
| `random_mouse_movement()` | Move mouse to random position |
| `get_page_source()` | Get current HTML |
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
✅ WebGL vendor/renderer spoofing
✅ Audio context fingerprint protection
✅ Battery API spoofing
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
  selenium-wire>=5.1.0
  blinker<1.8
  ```

---

## 📁 Package Structure

```
stealth-scraper/
├── stealth_scraper/     # Main package
│   ├── __init__.py          # Package exports
│   └── stealth_scraper.py   # Main implementation
├── tests/
│   └── test_suite.py        # Test suite
├── examples.py              # Usage examples
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
