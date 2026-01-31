# API Reference

Complete method listing for core scraper classes.

---

## StealthBrowser

The primary interface for automation.

### `navigate(url: str)`
Navigates to a URL with human-like waits and behavior.

### `wait_for_element(by, value, timeout=10, condition="presence")`
Waits for an element. Conditions: `presence`, `visible`, `clickable`.

### `click_element(element, scroll_first=True)`
Moves mouse to element and clicks.

### `type_into(element, text, scroll_first=True)`
Moves mouse to element, clicks, and types with realistic logic.

### `simulate_reading(word_count=None)`
Simulates reading the page with natural scrolling.

### `simulate_window_switching()`
Simulates tabbing away and back (Focus/Blur events).

### `simulate_shortcut(keys)`
Simulates keyboard shortcuts (e.g., `['Control', 'c']`).

---

## HumanMouseSimulator

Accessible via `browser.mouse`.

### `move_to(x, y, click=False)`
Curved mouse movement to coordinates.

### `move_to_element(element, click=False)`
Curved mouse movement to an element's bounding box.

---

## HumanScrollSimulator

Accessible via `browser.scroll`.

### `scroll_page(direction="down", amount=0.7)`
Scrolls by viewport percentage.

### `scroll_to_element(element, align="center")`
Brings element into view.

---

## HumanTypingSimulator

Accessible via `browser.typing`.

### `type_text(element, text, clear_first=True)`
Types into an element with variable delays and typos.

---

## Proxy Classes

### Proxy

Single proxy definition.

```python
from stealth_scraper import Proxy, ProxyType

proxy = Proxy(
    host="proxy.example.com",
    port=8080,
    proxy_type=ProxyType.HTTP,  # HTTP, HTTPS, SOCKS5
    username="user",
    password="pass",
    country="US",  # For geo-sync
)
```

#### Properties
- `requires_auth` - Returns `True` if proxy has credentials
- `url` - Full proxy URL with credentials
- `url_no_auth` - Proxy URL without credentials (for logging)

#### Class Methods
- `Proxy.from_url(url, country=None)` - Parse proxy from URL string

### ProxyConfig

Full proxy configuration.

```python
from stealth_scraper import ProxyConfig, RotationStrategy

config = ProxyConfig(
    enabled=True,
    proxy=proxy,  # Single proxy
    # OR proxy_pool=pool,  # Multiple proxies
    rotation_strategy=RotationStrategy.PER_SESSION,
    sync_location=True,  # Auto-match timezone/locale
)
```

#### Methods
- `get_current_proxy()` - Get active proxy
- `rotate()` - Move to next proxy in pool

#### Class Methods
- `ProxyConfig.from_url(url, **kwargs)` - Create config from URL string

### ProxyPool

Pool of proxies for rotation.

```python
from stealth_scraper import ProxyPool, Proxy

pool = ProxyPool([
    Proxy(host="proxy1.com", port=8080),
    Proxy(host="proxy2.com", port=8080),
])

pool.get_current()  # Get current proxy
pool.rotate()       # Move to next proxy
pool.reset()        # Reset to first proxy
```

### RotationStrategy Enum

```python
from stealth_scraper import RotationStrategy

RotationStrategy.NONE        # No rotation
RotationStrategy.PER_SESSION # New proxy each session
RotationStrategy.TIMED       # Rotate after interval
RotationStrategy.ON_ERROR    # Rotate on failure
```

### ProxyType Enum

```python
from stealth_scraper import ProxyType

ProxyType.HTTP    # HTTP proxy
ProxyType.HTTPS   # HTTPS proxy
ProxyType.SOCKS5  # SOCKS5 proxy
```

### ProxyManager

Internal manager for proxy lifecycle (usually not used directly).

```python
from stealth_scraper import ProxyManager

# Access via browser
browser._proxy_manager.current_proxy
browser._proxy_manager.get_synced_location()
```

### `report_failure()`
Alias for `rotate_on_error()`. Rotates to the next proxy if `ON_ERROR` strategy is active.

---

## NetworkManager

Accessible via `browser.network`. Manages passive CDP-based traffic capture.

### `start_capture(capture_body=False, max_body_size=1048576)`
Starts capturing network events.
- `capture_body`: If `True`, enables response body buffering (required for `get_response_body`).
- `max_body_size`: Maximum payload size to buffer (default 1MB).

### `stop_capture()`
Disables the network domain and stops capturing.

### `get_traffic() -> List[Dict]`
Returns a list of all captured network events since the start of the session.
Each event is a dictionary containing `method` (e.g., `Network.requestWillBeSent`), `params` (full CDP event data), and `timestamp`.

### `get_response_body(request_id: str) -> Optional[str]`
Retrieves the body for a specific request. 
**Note**: Requires `capture_body=True` in `start_capture()`.

### `wait_for_request(url_pattern: str, timeout=10.0) -> Optional[Dict]`
Blocks until a request matching the pattern is detected or timeout occurs.
Returns the request event if found.
---

## UA-Sync Engine

Implicit synchronization of browser environment with User-Agent.

### Automatic Sync
When `is_mobile=None` (default), the engine detects mobile status from the `user_agent`. If mobile is detected:
- **Plugins/MimeTypes**: Set to empty (matches mobile Chrome).
- **Platform**: Set to `Linux armv8l`.
- **Interaction**: CDP Touch Emulation automatically enabled.
- **Viewport**: Enforces mobile-appropriate dimensions (e.g., 390x844).

### Explicit Control
Force environment settings regardless of UA:
- `StealthConfig(is_mobile=True)`: Force mobile environmental spoofing.
- `StealthConfig(emulate_touch=True)`: Force touch events via CDP.
- `StealthConfig(mask_plugins=False)`: Disable the Plugin/MimeType masking system.

---

## Testing Tools

Professional verification tools for stealth hardening.

### Parametric Device Testing
Run the entire test suite against specific device profiles via CLI:

```bash
# Run all tests for BOTH Mobile and Desktop
python -m pytest tests/ -v

# Run only Mobile profile tests
python -m pytest tests/ -v --browser-type mobile

# Run only Desktop profile tests
python -m pytest tests/ -v --browser-type desktop
```

### Key Stealth Tests
- `test_ua_property_consistency`: Verifies that JS properties (Plugins, Platform, Viewport, Touch) match the UA.
- `test_language_header_consistency`: Verifies that network headers match JS languages.
- `test_identity_spoofing`: Verifies that location/fingerprint seeds work across device types.
