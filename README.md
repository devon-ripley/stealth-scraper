# 🥷 Ultimate Stealth Web Scraper

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.15+-green.svg)](https://selenium.dev)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-52%2F54%20passed-success)](tests/)

> **Undetectable web scraping with human-like behavior simulation.**

A powerful Python package that combines advanced anti-detection techniques (fingerprint spoofing, CDP overrides) with realistic human interaction simulation (Bezier mouse curves, typos, reading pauses) to scrape websites without triggering bot detection systems.

<p align="center">
  <img src="https://img.shields.io/badge/Bot%20Detection-Bypassed-success?style=for-the-badge" alt="Bot Detection Bypassed"/>
  <img src="https://img.shields.io/badge/Fingerprint-Masked-success?style=for-the-badge" alt="Fingerprint Masked"/>
  <img src="https://img.shields.io/badge/Mobile-Native-success?style=for-the-badge" alt="Mobile Native"/>
</p>

---

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| **[User Guide](docs/USER_GUIDE.md)** | Getting started, basic usage, and common workflows. |
| **[Configuration](docs/CONFIGURATION.md)** | Stealth levels, proxy setups, identity, and behavior tuning. |
| **[API Reference](docs/API.md)** | Full method listings for Browser, Simulators, and Managers. |
| **[Internals](docs/INTERNALS.md)** | Deep dive into the "Stealth Engine" and anti-detection layers. |
| **[Troubleshooting](docs/TROUBLESHOOTING.md)** | Solutions for common issues. |

---

## ✨ Key Features

### 🛡️ Anti-Detection Arsenal
- **Undetected ChromeDriver**: Core bypass integration.
- **Fingerprint Spoofing**: Canvas, WebGL, Audio, Font, and Hardware noise injection.
- **Mobile Fidelity**: Automatic `touch`, `platform`, and `viewport` adaptation when using a Mobile UA.
- **Network Capture**: Passive CDP traffic inspection.
- **Proxy Engine**: HTTP/SOCKS5 support with Auth, Rotation strategies, and Geo-Location sync.
- **UA-Sync**: Ensures Headers, JS Runtime, and Navigator properties perfectly match your User-Agent.

### 🎭 Human Behavior Simulation
- **Bezier Mouse**: Natural, curved cursor movements with variable speed errors.
- **Human Typing**: Realistic keystrokes with typos, corrections, and thought pauses.
- **Reading Flow**: Simulates "scrolling while reading" rather than instant jumps.
- **Idle Entropy**: Tiny micro-movements to avoid "dead" idle states.

---

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from stealth_scraper import StealthBrowser

# Uses "Ghost" identity (randomized fingerprint) by default
with StealthBrowser() as browser:
    browser.navigate("https://example.com")
    browser.simulate_reading()
    print(browser.get_page_source())
```

### Using Preset Levels

```python
from stealth_scraper import create_browser_with_level, StealthLevel

# Optimization Levels: FAST, LOW, MEDIUM, HIGH, PARANOID
with create_browser_with_level(StealthLevel.HIGH) as browser:
    browser.navigate("https://example.com/login")
```

### Advanced: Proxies & Consistent Identity

```python
from stealth_scraper import create_stealth_browser, StealthIdentity, Proxy

# 1. Consistent "Hardware" Identity (Safe for sessions)
# 2. Routing through a US proxy
with create_stealth_browser(
    identity=StealthIdentity.CONSISTENT,
    identity_seed="my_google_account_1",
    proxy="http://user:pass@us.proxy.com:8080"
) as browser:
    browser.navigate("https://whoer.net")
```

---

## ⚠️ Disclaimer

This tool is provided for **educational and research purposes only**. Users are responsible for ensuring their use complies with Website Terms of Service, applicable laws, and ethical scraping practices.

---

## 🤝 Contributing

Contributions are welcome! Feel free to report bugs or submit pull requests.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.
