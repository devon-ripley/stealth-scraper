# Changelog

All notable changes to **Ultimate Stealth Web Scraper** will be documented in this file.

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
