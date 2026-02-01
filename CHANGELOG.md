# Changelog

All notable changes to **Ultimate Stealth Web Scraper** will be documented in this file.

## [1.4.2] - 2026-02-01
### Added
- **True Mobile Emulation**: Implemented genuine Touch Events (`touchstart`, `touchmove`, `touchend`) for scrolling and tapping on mobile configurations.
  - Replaces mouse interactions on mobile (no more mouse cursors or hover events).
  - Supports pull-to-scroll swipe gestures.
- **Random Mouse Initialization**: Mouse cursor now starts at a random viewport position instead of (0,0) to reduce bot detection.
- **Mouse Persistence**: Visual cursor position is now preserved across page navigations, improving session realism.

### Fixed
- **Visual Cursor Bug**: Fixed regression where visual cursor would disappear on page navigation or reload.
- **Mobile Fidelity**: Removed visual mouse cursor entirely when running in mobile mode.

## [1.4.1] - 2026-01-31
### Fixed
- **GHOST Mode Fingerprinting**: Fixed fingerprint randomization to produce unique hardware profiles (concurrency/memory) on each browser instance.
- **Mobile Touch Support**: Corrected `maxTouchPoints` property to use `is_mobile` flag instead of `emulate_touch`, ensuring mobile devices report touch capability correctly.
- **Accept-Language Header**: Implemented consistent language header injection via CDP for both mobile and desktop browsers.
- **Test Suite Improvements**:
  - Fixed import error in `test_local_mechanics.py`.
  - Added navigation trigger for stealth script injection in `test_fingerprint_consistency.py`.
  - Corrected network event structure parsing in `test_ua_consistency.py`.
  - Test success rate improved from 85% to 96% (52/54 passing).

### Technical Details
- Enhanced `_inject_stealth_scripts()` to use time-based RNG seed for GHOST mode randomization.
- Added `_apply_header_consistency()` call in browser startup sequence.
- Updated `stealth.js` navigator property masking logic for better mobile device simulation.

### Known Limitations
- Network body capture on mobile devices has limited support due to standard Selenium CDP constraints (architectural limitation, not a regression).

## [1.4.0] - 2026-01-30
### Added
- **Perfect Masking**: Upgraded `navigator.webdriver` masking to be undetectable by advanced prototype checks ("Sannysoft New").
- **UA-Sync Engine**: Implicitly synchronizes `plugins`, `platform`, and `languages` based on the spoofed User-Agent.
- **Mobile Fidelity**: Automated mobile-device profile injection (0 plugins, Linux armv8l platform) when using a mobile User-Agent.
- **Custom Identity**: Added `user_agent` support to `create_stealth_browser` and `StealthConfig`.
- **Network Traffic Capture**: Passive CDP-based traffic inspection.
- **Hardening Suite**: New formal tests for Behavior Sanity, Network Capture, Proxy Rotation, and UA Consistency.
- **Windows Cleanup**: Silenced noisy `WinError 6` tracebacks during browser teardown on Windows.
- **Visual Improvements**: added red ripple effect for mouse clicks in `cursor.js`.
- **Stability**: Disabled `emulate_touch` by default to prevent hangs during rapid mobile interactions.
- **Deterministic Identity**: Implemented seeded RNG in `StealthBrowser` to guarantee consistent viewports and headers in `CONSISTENT` mode.
- **Universal Test Suite**: Full `conftest.py` monkeypatching implies standardizing tests for both Mobile and Desktop profiles (54/54 passed).
- **Hardening**: Fixed potential race conditions in `test_identity_spoofing.py` and `test_fingerprint_consistency.py`.

## [1.3.0] - 2026-01-29
### Added
- **Proxy Support**: Comprehensive proxy module with rotation and geo-sync.
  - `Proxy` class for single proxy definition (HTTP/HTTPS/SOCKS5 with auth).
  - `ProxyConfig` for full configuration with rotation strategies.
  - `ProxyPool` for managing multiple proxies.
  - `RotationStrategy` enum: NONE, PER_SESSION, TIMED, ON_ERROR.
  - Chrome extension generator for authenticated proxy support.
  - Geo-location sync: Auto-match timezone/locale to proxy country.
- **40+ Country Mappings**: US, GB, JP, DE, FR, CA, AU, and more.
- Simple URL string support: `proxy="http://user:pass@host:8080"`.

### Changed
- `create_stealth_browser()` now accepts `proxy` parameter.
- `StealthBrowser.__init__` accepts `proxy` parameter.
- Removed deprecated `ProxyConfig` stub from `config.py`.
- **Stealth Level Rebalancing**: Improved preset configurations for better progression.
  - FAST: Explicitly set mouse_overshoot_chance=0.0 (no overshoot in teleport mode).
  - LOW: Added minimal random pauses (2% chance, 0.5-1.5s duration) to avoid robotic behavior.
  - MEDIUM: Made all values explicit (mouse_overshoot_chance=0.15, random_pause_chance=0.05, reading_speed_wpm=250).
  - Added progression documentation in code comments and docs.
  - Updated comparison tables in README and CONFIGURATION docs.

## [1.2.0] - 2026-01-29
### Added
- External JS files (`stealth.js`, `cursor.js`) for better maintainability.
- Robust configuration injection using `.replace()` instead of templates.
- **Modular Identity**: GHOST vs CONSISTENT fingerprinting strategies.
- **Location Presets**: `StealthLocation.Tokyo()`, `US()`, `UK()`.
- **New Tests**: `test_identity_spoofing.py`, `test_resource_blocking.py`.
- **Direct Geolocation Permission**: CDP-based permission granting.

### Fixed
- Fixed `navigator.language` synchronization bug.
- Fixed mouse coordinate issues on scrolled pages.
- Fixed hardcoded "en-US" headers in CDP overrides.

## [1.1.0] - 2026-01-20
### Added
- `CustomStealthLevel` for granular overrides.
- `StealthLevel.FAST` for 0ms delay throughput.
- Resource blocking (CSS/Images) via CDP.

## [1.0.0] - 2026-01-10
### Added
- Initial release.
- Bezier mouse movements.
- Human typing with typos.
- Reading simulation.
- `undetected-chromedriver` core integration.
