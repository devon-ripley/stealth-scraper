# Stealth Engine: Under the Hood

Ultimate Stealth Web Scraper uses a multi-layered approach to bypass modern anti-bot systems.

---

## 🛡️ Anti-Detection Layers

### 1. Browser Fingerprint Masking
We go beyond simple User-Agent switching. Every aspect of the browser's identity is sanitized or spoofed:

- **WebDriver Removal**: `navigator.webdriver` is set to `undefined`.
- **Mocked Runtime**: `chrome.runtime` and other internal objects are mocked with realistic implementations.
- **Plugins/MimeTypes**: The `plugins` and `mimeTypes` arrays are populated with realistic data (e.g., PDF Viewer, Native Client), customized per-platform.
- **Hardware Profile**: 
  - `hardwareConcurrency` is randomized (4, 8, 12, or 16 cores).
  - `deviceMemory` is randomized (4, 8, 16, or 32 GB).
- **Canvas Fingerprint**: We inject low-level noise into canvas rendering calls, creating a unique signature.
- **WebGL Spoofing**: We override the WebGL Vendor and Renderer strings (e.g., forcing "Intel Iris OpenGL Engine" instead of "Google SwiftShader").
- **AudioContext**: Imperceptible noise is added to audio processing buffers to randomize audio fingerprinting.
- **Font Metrics**: Width/Height of fonts are slightly randomized to defeat font enumeration fingerprinting.
- **Battery API**: Mocked to show realistic charging/level states.

### 2. Chrome Flags & Options
We launch Chrome with a carefully curated set of flags to disable automation "tells":

```
--disable-blink-features=AutomationControlled
--disable-features=AutomationControlled
--disable-features=OptimizationGuideModelDownloading
--disable-webrtc (Optional, prevents IP leaks)
--disable-notifications
--disable-popup-blocking
--disable-dev-shm-usage
--no-sandbox
--ignore-certificate-errors
--allow-running-insecure-content
```

### 3. CDP (Chrome DevTools Protocol)
We use low-level CDP commands to ensure spoofing is deep and consistent:

- **Network**: `Accept-Language` headers are synchronized with your spoofed locale via `Network.setUserAgentOverride`.
- **Emulation**: Timezone and Geolocation are applied at the browser engine level (`Emulation.setTimezoneOverride`), not just the JS layer.
- **Permissions**: Geolocation permissions are automatically granted via `Browser.grantPermissions`.
- **Resource Blocking**: `Network.setBlockedURLs` efficiently blocks ads/trackers before requests leave the network stack.

---

## 📱 Mobile Stealth Engine
The **UA-Sync Engine** is a specialized component for mobile emulation:

- **Platform Sync**: If a mobile UA is detected (Android/iOS), the platform is implicitly set to `Linux armv8l` or `iPhone`.
- **Touch Emulation**: Using `Emulation.setTouchEmulationEnabled`, we tell Chrome to behave like a touch device.
- **Viewport**: Mobile-specific viewports (e.g., 375x667) are enforced.
- **Plugin Cleaning**: Since mobile browsers typically don't have plugins, we clear the plugins array for mobile profiles to avoid "Impossible Identity" flags.
- **Detection Evasion**: We specifically mask the `navigator.webdriver` property using a rigorous prototype-modification technique that bypasses "New Sannysoft" checks.

---

## 🎭 Human Behavior Simulation

### Bezier Mouse Movement
We don't move the mouse in straight lines. We generate complex **Bezier Curves** with:
- **Variable Tempo**: Slow at start/end, fast in the middle (Fitts's Law approximation).
- **Overshooting**: Occasionally missing the target and correcting, just like a human.
- **Micro-moves**: Tiny drifts when the mouse is "idle" to avoid freezing detection (Entropy injection).

### Human Typing
- **Typo Map**: We maintain a list of adjacent keys. If a typo occurs, the "hand" hits a neighboring key, realizes the mistake, hits Backspace, and corrects it.
- **Punctuation Pauses**: Longer delays are added after periods, commas, and paragraph breaks.
- **Thinking Pauses**: Random "hesitations" are injected during typing flows.

### Reading Simulation
The `simulate_reading()` method calculates a realistic reading time based on word count (WPM) and:
- Scrolls gradually down the page.
- Variably pauses on sections.
- Occasionally scrolls back up (re-reading behavior).
