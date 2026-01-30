# User Guide & Quick Start

A comprehensive guide to getting started with Ultimate Stealth Web Scraper.

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

## Common Workflows

### 1. Form Login
```python
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

### 2. Infinite Scroll Scraping
```python
with StealthBrowser() as browser:
    browser.navigate("https://example.com/feed")

    for i in range(10):
        # Human-like scrolling
        browser.scroll.scroll_page("down", 0.8)
        browser.random_pause(1.0, 3.0)

        # Occasional scroll back up (humans do this)
        if i % 3 == 0:
            browser.scroll.scroll_page("up", 0.2)
```

### 3. Using Proxies
```python
from stealth_scraper import create_stealth_browser, Proxy, ProxyConfig

# Simple: URL string
with create_stealth_browser(proxy="http://user:pass@proxy.example.com:8080") as browser:
    browser.navigate("https://httpbin.org/ip")
    print(browser.get_page_source())  # Shows proxy IP

# With geo-location sync
proxy = Proxy(
    host="us.proxy.com",
    port=8080,
    country="US",
    username="user",
    password="pass"
)
config = ProxyConfig(enabled=True, proxy=proxy, sync_location=True)

with create_stealth_browser(proxy=config) as browser:
    # Browser timezone/locale automatically set to US
    browser.navigate("https://example.com")
```

### 4. Proxy Rotation
```python
from stealth_scraper import create_stealth_browser, Proxy, ProxyConfig, ProxyPool, RotationStrategy

# Create pool of proxies
pool = ProxyPool([
    Proxy(host="proxy1.com", port=8080, country="US"),
    Proxy(host="proxy2.com", port=8080, country="GB"),
    Proxy(host="proxy3.com", port=8080, country="DE"),
])

config = ProxyConfig(
    enabled=True,
    proxy_pool=pool,
    rotation_strategy=RotationStrategy.PER_SESSION,
    sync_location=True
)

# Each browser session uses next proxy in pool
for i in range(3):
    with create_stealth_browser(proxy=config) as browser:
        browser.navigate("https://httpbin.org/ip")
        print(f"Session {i+1}: {browser.proxy_manager.current_proxy}")
    config.rotate()  # Move to next proxy
```
