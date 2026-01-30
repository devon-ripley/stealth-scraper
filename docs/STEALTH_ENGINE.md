# Stealth Engine: Under the Hood

Ultimate Stealth Web Scraper uses a multi-layered approach to bypass modern anti-bot systems.

---

## 🛡️ Anti-Detection Layers

### 1. WebDriver Masking
We remove all traces of automation in the browser:
- `navigator.webdriver` is set to `undefined`.
- `chrome.runtime` and other internal objects are mocked with realistic implementations.
- Automation-specific Chrome flags are stripped.

### 2. Fingerprint Spoofing
Instead of simply hiding, we *spoof* your hardware identity:
- **Canvas/WebGL**: We inject "noise" into rendering calls to ensure your device fingerprint is unique (GHOST mode) or stable (CONSISTENT mode).
- **AudioContext**: We add imperceptible noise to audio sample processing.
- **Hardware**: We randomize `deviceMemory` and `hardwareConcurrency`.

### 3. CDP (Chrome DevTools Protocol)
We use low-level CDP commands to ensure spoofing is deep and consistent:
- **Network**: `Accept-Language` headers are synchronized with your spoofed locale.
- **Emulation**: Timezone and Geolocation are applied at the browser engine level, not just the JS layer.
- **Permissions**: Geolocation permissions are automatically granted via CDP.

---

## 🎭 Human Behavior Simulation

### Bezier Mouse Movement
We don't move the mouse in straight lines. We generate complex **Bezier Curves** with:
- **Variable Tempo**: Slow at start/end, fast in the middle (Fitts's Law approximation).
- **Overshooting**: Occasionally missing the target and correcting, just like a human.
- **Micro-moves**: Tiny drifts when the mouse is "idle" to avoid freezing detection.

### Human Typing
- **Typo Map**: We maintain a list of adjacent keys. If a typo occurs, the "hand" hits a neighboring key, realizes the mistake, hits Backspace, and corrects it.
- **Punctuation Pauses**: Longer delays are added after periods and commas.

### Resource Blocking
We use CDP `Network.setBlockedURLs` to intercept requests *before* they leave the browser. This allows for 5x speed improvements in `FAST` mode without losing fingerprint protection.
