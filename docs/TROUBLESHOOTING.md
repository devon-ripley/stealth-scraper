# Troubleshooting & FAQ

## Common Issues

### ❌ "User denied Geolocation"
**Cause**: The browser is blocking the GPS request.
**Fix**: In v1.2.0+, the scraper automatically grants permissions via CDP. Ensure you are using `StealthBrowser` or the factory functions which call `_apply_cdp_configurations()`.

### ❌ WebDriver version mismatch
**Cause**: Your Chrome browser updated, but your driver is old.
**Fix**: We use `webdriver-manager` to handle this. If it fails, try deleting the cache folder:
`rm -rf ~/.wdm`

### ❌ Elements not found in Headless mode
**Cause**: Some sites render differently or require a specific viewport size in headless mode.
**Fix**: Increase `min_page_load_wait` or try running with `headless=False` to debug.

### ❌ "The handle is invalid" (Windows)
**Cause**: A common `undetected-chromedriver` cleanup error on exit.
**Fix**: This is generally harmless and can be ignored. It does not affect the scraping result.

---

## FAQ

#### Can I use proxies?
Native proxy support was moved to internal CDP routing. For now, use system-level proxies or authenticated CDP commands via `browser.driver.execute_cdp_cmd`.

#### Is it detectable?
No system is 100% undetectable, but by combining **Headful mode** with **HIGH stealth level**, this package bypasses most major anti-bot solutions (Akamai, Cloudflare, DataDome).

#### How do I save bandwidth?
Use `block_resources=True` in your config. This will prevent Images and CSS from downloading while keeping your JS environment intact.
