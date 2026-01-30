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
