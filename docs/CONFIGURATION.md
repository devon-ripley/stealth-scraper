# Configuration Reference

The scraper is highly configurable through two main configuration classes: `StealthConfig` and `HumanBehaviorConfig`.

---

## Preset Stealth Levels

Using levels is the easiest way to get started.

```python
from stealth_scraper import StealthLevel

# Optimization Levels
StealthLevel.FAST     # API-speed (0ms delays), invisible.
StealthLevel.LOW      # Minimal delays, basic stealth.
StealthLevel.MEDIUM   # Balanced (Default).
StealthLevel.HIGH     # Maximum human simulation.
StealthLevel.PARANOID # Extreme stealth, headful mode.
```

### Stealth Level Progressions

The preset levels follow logical progressions for human-like behavior:

| Parameter | FAST | LOW | MEDIUM | HIGH | PARANOID |
|-----------|------|-----|--------|------|----------|
| **Mouse Overshoot** | N/A | 0.05 | 0.15 | 0.25 | 0.4 |
| **Random Pause Chance** | 0.0 | 0.02 | 0.05 | 0.15 | 0.25 |
| **Reading Speed (WPM)** | N/A | 350 | 250 | 220 | 180 |
| **Mouse Speed (sec)** | 0.0 | 0.3-0.8 | 0.4-1.0 | 0.8-1.8 | 1.2-2.5 |
| **Typing Delay (sec)** | 0.0 | 0.03-0.12 | 0.05-0.15 | 0.08-0.25 | 0.12-0.35 |
| **Action Pause (sec)** | 0-0.05 | 0.2-0.8 | 0.4-1.2 | 0.5-2.0 | 1.0-3.0 |
| **Page Load Wait (sec)** | 0.1-0.5 | 0.5-1.5 | 1.0-3.0 | 3.0-6.0 | 4.0-8.0 |

---

## HumanBehaviorConfig

Controls human-like interaction simulation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_mouse_speed` | float | 0.4 | Minimum time (secs) for a mouse movement |
| `max_mouse_speed` | float | 1.0 | Maximum time (secs) for a mouse movement |
| `mouse_curve_intensity` | float | 0.3 | Curvature of paths (0.0=straight, 1.0=wild) |
| `mouse_overshoot_chance`| float | 0.15| Probability of overshooting target |
| `typo_chance` | float | 0.005 | Probability of making/correcting a typo |
| `reading_speed_wpm` | int | 250 | Words per minute for reading simulation |

---

## StealthConfig

Controls anti-detection and fingerprint settings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `identity` | enum | GHOST | `GHOST` (Random) or `CONSISTENT` (Seeded) |
| `identity_seed` | str | None | Seed for `CONSISTENT` fingerprint |
| `location` | object | None | `StealthLocation` preset (Tokyo, US, etc) |
| `headless` | bool | False | Run browser invisibly |
| `block_resources` | bool | False | Block CSS/Images for speed |
| `disable_webrtc` | bool | True | Prevent real IP leak |
| `spoof_timezone` | str | None | Custom timezone string |
| `spoof_locale` | str | None | Custom locale (e.g., "ja-JP") |

---

## Identity & Location Presets

```python
from stealth_scraper import StealthIdentity, StealthLocation

# Identity
StealthIdentity.GHOST
StealthIdentity.CONSISTENT

# Location
StealthLocation.US()
StealthLocation.UK()
StealthLocation.Tokyo()
```

---

## Proxy Configuration

Route traffic through proxies with authentication, rotation, and geo-location sync.

### Quick Start

```python
from stealth_scraper import create_stealth_browser

# Simple URL string
with create_stealth_browser(proxy="http://user:pass@proxy.example.com:8080") as browser:
    browser.navigate("https://example.com")
```

### Proxy Class

Single proxy definition supporting HTTP, HTTPS, and SOCKS5.

```python
from stealth_scraper import Proxy, ProxyType

# Basic proxy
proxy = Proxy(host="proxy.example.com", port=8080)

# Authenticated proxy
proxy = Proxy(
    host="proxy.example.com",
    port=8080,
    username="user",
    password="pass"
)

# SOCKS5 with geo-targeting
proxy = Proxy(
    host="socks.example.com",
    port=1080,
    proxy_type=ProxyType.SOCKS5,
    username="user",
    password="pass",
    country="US",  # ISO 3166-1 alpha-2
    city="New York"
)

# Parse from URL
proxy = Proxy.from_url("http://user:pass@host:8080", country="US")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | str | required | Proxy hostname or IP |
| `port` | int | required | Proxy port |
| `proxy_type` | ProxyType | HTTP | HTTP, HTTPS, or SOCKS5 |
| `username` | str | None | Auth username |
| `password` | str | None | Auth password |
| `country` | str | None | ISO country code for geo-sync |
| `city` | str | None | City name |
| `provider` | str | None | Provider identifier |

### ProxyConfig

Full configuration with rotation and geo-sync.

```python
from stealth_scraper import ProxyConfig, Proxy, RotationStrategy

config = ProxyConfig(
    enabled=True,
    proxy=Proxy(host="proxy.com", port=8080, country="US"),
    sync_location=True,  # Auto-match timezone/locale to proxy country
    rotation_strategy=RotationStrategy.NONE
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | True | Enable/disable proxy |
| `proxy` | Proxy | None | Single proxy instance |
| `proxy_pool` | ProxyPool | None | Pool for rotation |
| `rotation_strategy` | RotationStrategy | NONE | Rotation strategy |
| `rotation_interval_seconds` | int | 300 | Interval for TIMED rotation |
| `sync_location` | bool | False | Auto-sync timezone/locale |

### ProxyPool & Rotation

```python
from stealth_scraper import ProxyConfig, ProxyPool, Proxy, RotationStrategy

pool = ProxyPool([
    Proxy(host="us.proxy.com", port=8080, country="US"),
    Proxy(host="uk.proxy.com", port=8080, country="GB"),
    Proxy(host="jp.proxy.com", port=8080, country="JP"),
])

config = ProxyConfig(
    enabled=True,
    proxy_pool=pool,
    rotation_strategy=RotationStrategy.PER_SESSION,
    sync_location=True
)
```

### Rotation Strategies

| Strategy | Description |
|----------|-------------|
| `NONE` | Use single proxy, no rotation |
| `PER_SESSION` | New proxy for each browser session |
| `TIMED` | Rotate after `rotation_interval_seconds` |
| `ON_ERROR` | Rotate when proxy fails |

### Geo-Location Sync

When `sync_location=True` and proxy has a `country`, the browser automatically uses matching timezone, geolocation, and locale.

Supported countries: US, CA, MX, GB, DE, FR, ES, IT, NL, BE, CH, AT, PL, SE, NO, DK, FI, PT, IE, RU, JP, KR, CN, TW, HK, SG, IN, AU, NZ, TH, VN, ID, MY, PH, BR, AR, CL, CO, AE, IL, SA, TR, ZA, EG, NG

```python
from stealth_scraper import create_stealth_browser, Proxy, ProxyConfig

# US proxy with geo-sync
proxy = Proxy(host="us.proxy.com", port=8080, country="US", username="u", password="p")
config = ProxyConfig(enabled=True, proxy=proxy, sync_location=True)

# Browser uses:
# - Timezone: America/New_York
# - Geolocation: 40.7128, -74.0060 (NYC)
# - Locale: en-US
# - Languages: ["en-US", "en"]
with create_stealth_browser(proxy=config) as browser:
    browser.navigate("https://example.com")
```
