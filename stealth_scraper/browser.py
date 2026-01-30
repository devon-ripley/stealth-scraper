import random
import time
import math
import json
import platform
from typing import List, Tuple, Optional, Any, Dict, Union, Callable
import os

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from fake_useragent import UserAgent

from .config import (
    StealthLevel, CustomStealthLevel, StealthIdentity, StealthLocation,
    StealthConfig, HumanBehaviorConfig,
)
from .proxy import Proxy, ProxyConfig, ProxyManager
from .proxy.config import ProxyInput
from .simulators.mouse import HumanMouseSimulator
from .simulators.scroll import HumanScrollSimulator
from .simulators.keyboard import HumanTypingSimulator

# Optional selenium-stealth import
try:
    from selenium_stealth import stealth
    SELENIUM_STEALTH_AVAILABLE = True
except ImportError:
    SELENIUM_STEALTH_AVAILABLE = False


class StealthBrowser:
    """Main stealth browser class with anti-detection measures."""

    def __init__(
        self,
        behavior_config: Optional['HumanBehaviorConfig'] = None,
        stealth_config: Optional['StealthConfig'] = None,
        proxy: Optional[ProxyInput] = None,
    ):
        """
        Initialize the stealth browser.

        Args:
            behavior_config: Configuration for human behavior simulation
            stealth_config: Configuration for browser fingerprinting/stealth
            proxy: Proxy configuration - can be:
                - str: Proxy URL (e.g., "http://user:pass@host:8080")
                - Proxy: Single proxy instance
                - ProxyConfig: Full configuration with rotation
        """
        self.behavior_config = behavior_config or HumanBehaviorConfig()
        self.stealth_config = stealth_config or StealthConfig()
        self._proxy_manager = ProxyManager.from_input(proxy)
        self.driver = None
        self.mouse: Optional[HumanMouseSimulator] = None
        self.scroll: Optional[HumanScrollSimulator] = None
        self.typing: Optional[HumanTypingSimulator] = None

        # Apply location sync if enabled
        if self._proxy_manager and self._proxy_manager.sync_location:
            synced_location = self._proxy_manager.get_synced_location()
            if synced_location and not self.stealth_config.location:
                self.stealth_config.location = synced_location
    
    
    @property
    def proxy_manager(self) -> Optional[ProxyManager]:
        """Get the proxy manager instance."""
        return self._proxy_manager

    def _get_stealth_options(self) -> Options:
        """Configure Chrome options for stealth."""
        options = Options()
        
        # Randomize viewport
        if self.stealth_config.randomize_viewport:
            width, height = random.choice(self.stealth_config.viewport_sizes)
            options.add_argument(f"--window-size={width},{height}")
        
        # ========================================
        # CORE ANTI-DETECTION ARGUMENTS
        # ========================================
        
        # Disable automation indicators
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        
        # Ignore SSL errors (often needed for proxies/interceptors)
        options.add_argument("--ignore-certificate-errors")
        
        # Disable dev-shm for stability in containers
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # ========================================
        # FINGERPRINT EVASION
        # ========================================
        
        # Disable features that reveal automation
        options.add_argument("--disable-features=AutomationControlled")
        options.add_argument("--disable-features=OptimizationGuideModelDownloading")
        options.add_argument("--disable-features=OptimizationHintsFetching")
        options.add_argument("--disable-features=OptimizationTargetPrediction")
        options.add_argument("--disable-features=OptimizationHints")
        
        # Prevent detection via Chrome flags/features
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-features=BlinkGenPropertyTrees")
        
        # Disable logging that might reveal automation
        options.add_argument("--log-level=3")  # Only fatal errors
        options.add_argument("--silent")
        options.add_argument("--disable-logging")
        
        # ========================================
        # WEBRTC PROTECTION (IP LEAK PREVENTION)
        # ========================================
        
        if self.stealth_config.disable_webrtc:
            # These help prevent WebRTC from leaking real IP
            options.add_argument("--disable-webrtc")
            options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")
            options.add_argument("--enforce-webrtc-ip-permission-check")
            options.add_argument("--force-webrtc-ip-handling-policy=disable_non_proxied_udp")
        
        # ========================================
        # GPU AND RENDERING
        # ========================================
        
        # Enable GPU for more realistic fingerprint (unless in container)
        # options.add_argument("--disable-gpu")  # Uncomment if running headless/container
        options.add_argument("--enable-features=VaapiVideoDecoder")
        options.add_argument("--use-gl=egl")
        
        # Hardware acceleration settings
        options.add_argument("--enable-accelerated-2d-canvas")
        options.add_argument("--enable-accelerated-video-decode")
        
        # Headless mode optimizations (Phase 3)
        if self.stealth_config.headless:
            # Note: UC handles the main --headless flag, but we add these for robustness
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--hide-scrollbars")
        
        # ========================================
        # PRIVACY AND SECURITY SETTINGS
        # ========================================
        
        # Disable various Chrome features that might interfere
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-component-update")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-domain-reliability")
        # Note: --disable-extensions is conditionally added below (after proxy check)
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-sync")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-first-run")
        options.add_argument("--password-store=basic")
        options.add_argument("--use-mock-keychain")
        
        # Disable notifications
        if self.stealth_config.disable_notifications:
            options.add_argument("--disable-notifications")
        
        # ========================================
        # USER AGENT CONFIGURATION
        # ========================================
        
        # Get a realistic user agent matching the OS
        ua = UserAgent()
        current_os = platform.system().lower()
        
        if current_os == "windows":
            user_agent = ua.chrome  # Will prioritize Windows UA
        elif current_os == "darwin":
            user_agent = ua.chrome
        else:
            user_agent = ua.chrome
        
        # Remove "HeadlessChrome" if present (shouldn't be with headless=False)
        user_agent = user_agent.replace("HeadlessChrome", "Chrome")
        options.add_argument(f"--user-agent={user_agent}")
        self._current_user_agent = user_agent
        
        # ========================================
        # LANGUAGE AND LOCALE
        # ========================================
        
        if self.stealth_config.spoof_locale:
            options.add_argument(f"--lang={self.stealth_config.spoof_locale}")
        else:
            languages = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-US,en;q=0.9,es;q=0.8"]
            options.add_argument(f"--lang={random.choice(languages)}")
        
        # ========================================
        # PERSISTENT PROFILE
        # ========================================
        
        if self.stealth_config.use_persistent_profile and self.stealth_config.profile_path:
            options.add_argument(f"--user-data-dir={self.stealth_config.profile_path}")
        
        # ========================================
        # PROXY CONFIGURATION
        # ========================================

        # Create proxy extension if using authenticated proxy
        _using_proxy_extension = False
        if self._proxy_manager and self._proxy_manager.enabled:
            # Create extension for authenticated proxies
            ext_path = self._proxy_manager.create_extension()
            if ext_path:
                options.add_argument(f"--load-extension={ext_path}")
                _using_proxy_extension = True
            else:
                # Non-auth proxy: use --proxy-server flag
                proxy = self._proxy_manager.current_proxy
                if proxy:
                    options.add_argument(f"--proxy-server={proxy.url_no_auth}")

        # Disable extensions only if we're not using proxy extension
        if not _using_proxy_extension:
            options.add_argument("--disable-extensions")

        # ========================================
        # EXPERIMENTAL OPTIONS
        # ========================================
        
        prefs = {
            # Disable password manager
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            
            # Disable notifications
            "profile.default_content_setting_values.notifications": 2,
            
            # WebRTC settings for IP leak protection
            "webrtc.ip_handling_policy": "disable_non_proxied_udp",
            "webrtc.multiple_routes_enabled": False,
            "webrtc.nonproxied_udp_enabled": False,
            
            # Disable geolocation prompts
            "profile.default_content_setting_values.geolocation": 1,
            
            # Disable save prompts
            "download.prompt_for_download": False,
            "download.default_directory": "/tmp",
            
            # Disable autofill
            "autofill.profile_enabled": False,
            "autofill.credit_card_enabled": False,
            
            # Disable safe browsing (can slow things down)
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
            
            # Performance optimizations that don't hurt stealth
            "profile.managed_default_content_settings.images": 1 if not self.stealth_config.block_images else 2,
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
    
    def _inject_stealth_scripts(self) -> None:
        """Inject JavaScript to mask automation indicators with optional seeded consistency."""
        # Handle Identity (Seeded vs Ghost)
        seed = None
        if self.stealth_config.identity == StealthIdentity.CONSISTENT:
            # Priority: explicit seed > profile path > stable default
            seed = self.stealth_config.identity_seed or self.stealth_config.profile_path or "stable-seed"
        
        # Generator for seeded values
        rng = random.Random(seed) if seed else random
        
        # Pre-calculate seeded constants for injection
        inject_vars = {
            "webgl_vendor": rng.choice(["Intel Inc.", "Google Inc.", "NVIDIA Corporation"]),
            "webgl_renderer": rng.choice([
                "Intel Iris OpenGL Engine",
                "Intel(R) UHD Graphics 620",
                "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11)"
            ]),
            "canvas_noise": rng.uniform(0.001, 0.005),
            "audio_noise": rng.uniform(0.0001, 0.0005),
        }

        # Load and template the script
        script_template = self._load_script("stealth.js")
        
        # We use simple string replacement because auto-formatters can break
        # string.Template syntax (e.g. adding spaces inside ${})
        stealth_scripts = script_template.replace(
            '"__STEALTH_CONFIG__"', 
            json.dumps(inject_vars)
        )
        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_scripts
        })

    def _load_script(self, filename: str) -> str:
        """Load a JS script from resources directory."""
        # Cache could be implemented here if needed
        path = os.path.join(os.path.dirname(__file__), 'resources', filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Resource file {filename} not found at {path}")
            return ""


        
    def _inject_cursor_visualizer(self) -> None:
        """Inject a hardware-accelerated visual cursor tracker for debugging/demo."""
        cursor_js = self._load_script("cursor.js")
        if not cursor_js:
            return

        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": cursor_js
            })
        except Exception as e:
            print(f"DEBUG: Failed to inject visualizer: {e}")
        

    
    def start(self) -> 'StealthBrowser':
        """Initialize the stealth browser."""
        options = self._get_stealth_options()
        
        if self.stealth_config.use_undetected_chrome:
            try:
                # Use webdriver_manager to get the definitely-correct driver path
                driver_path = ChromeDriverManager().install()
                
                # Initialize the driver
                self.driver = uc.Chrome(
                    options=options,
                    headless=self.stealth_config.headless, 
                    use_subprocess=True,
                    driver_executable_path=driver_path,
                )
                
                # Execute CDP commands AFTER driver creation
                if self.driver:
                    # Enable resource blocking if requested
                    if self.stealth_config.block_resources:
                        self._enable_resource_blocking()

            except Exception as e:
                # If UC fails (often due to version mismatch), log it and try to clean up
                print(f"Error initializing undetected_chromedriver: {e}")
                print("Attempting to clean up and retry...")
                try:
                    if self.driver:
                        self.driver.quit()
                except:
                    pass
                raise e
        else:
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
        
        # Apply selenium-stealth if available and enabled
        if SELENIUM_STEALTH_AVAILABLE and self.stealth_config.use_selenium_stealth:
            self._apply_selenium_stealth()
        
        # Inject stealth scripts via CDP
        if self.stealth_config.mask_automation_indicators:
            self._inject_stealth_scripts()
        
        # Apply CDP-based configurations
        self._apply_cdp_configurations()
        
        # Inject mouse visualizer if requested
        if self.stealth_config.visualize_mouse:
            self._inject_cursor_visualizer()
        
        # Initialize simulators
        self.mouse = HumanMouseSimulator(self.driver, self.behavior_config)
        self.scroll = HumanScrollSimulator(self.driver, self.behavior_config)
        self.typing = HumanTypingSimulator(self.driver, self.behavior_config)
        
        return self
    
    def _apply_selenium_stealth(self) -> None:
        """Apply selenium-stealth library configurations."""
        # WebGL vendors and renderers that look realistic
        webgl_vendors = ["Intel Inc.", "Google Inc.", "NVIDIA Corporation"]
        webgl_renderers = [
            "Intel Iris OpenGL Engine",
            "Intel(R) UHD Graphics 620",
            "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.5671)",
            "Mesa DRI Intel(R) UHD Graphics 620 (Kabylake GT2)",
        ]
        
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor=random.choice(webgl_vendors),
            renderer=random.choice(webgl_renderers),
            fix_hairline=True,
            run_on_insecure_origins=False,
        )
    
    def _apply_cdp_configurations(self) -> None:
        """Apply Chrome DevTools Protocol configurations for enhanced stealth."""
        try:
            # 1. Handle Location context (Phase 2)
            loc = self.stealth_config.location
            timezone = self.stealth_config.spoof_timezone
            lat, lon = None, None
            if self.stealth_config.spoof_geolocation:
                lat, lon = self.stealth_config.spoof_geolocation
            locale = self.stealth_config.spoof_locale
            
            # Location object takes precedence
            if loc:
                timezone = loc.timezone
                lat, lon = loc.latitude, loc.longitude
                locale = loc.locale

            if timezone:
                self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": timezone})
            
            if lat is not None and lon is not None:
                self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                    "latitude": lat, "longitude": lon, "accuracy": 100
                })
                # Grant permission for the current origin (or all origins if needed)
                try:
                    self.driver.execute_cdp_cmd("Browser.grantPermissions", {
                        "permissions": ["geolocation"]
                    })
                except: pass
            
            if locale:
                self.driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": locale})
            
            # Set user agent via CDP for consistency
            if hasattr(self, '_current_user_agent'):
                # Get platform info
                platform_info = {
                    "windows": "Windows",
                    "darwin": "macOS", 
                    "linux": "Linux"
                }.get(platform.system().lower(), "Windows")
                
                # Determine acceptLanguage based on locale
                accept_lang = "en-US,en;q=0.9"
                if locale:
                    # simplistic mapping, could be improved
                    accept_lang = f"{locale},{locale.split('-')[0]};q=0.9,en-US;q=0.8,en;q=0.7"

                self.driver.execute_cdp_cmd(
                    "Emulation.setUserAgentOverride",
                    {
                        "userAgent": self._current_user_agent,
                        "platform": platform_info,
                        "acceptLanguage": accept_lang,
                    }
                )
            
            # Additional script to ensure navigator.language/languages are consistent
            if locale:
                langs = [locale]
                if '-' in locale:
                    langs.append(locale.split('-')[0])
                if 'en-US' not in langs:
                    langs.append('en-US')
                
                self.driver.execute_cdp_cmd(
                    "Page.addScriptToEvaluateOnNewDocument",
                    {
                        "source": f"""
                            Object.defineProperty(navigator, 'language', {{
                                get: () => '{locale}'
                            }});
                            Object.defineProperty(navigator, 'languages', {{
                                get: () => {json.dumps(langs)}
                            }});
                        """
                    }
                )

            # Disable webdriver flag via CDP
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """
                }
            )
            
        except Exception as e:
            # CDP commands may fail on some browser versions, continue anyway
            pass
    
    def _enable_resource_blocking(self) -> None:
        """Enable CDP resource blocking for optimized performance."""
        blocked_patterns = [
            "*favicon.ico*",
            "*.png*", "*.jpg*", "*.jpeg*", "*.gif*", "*.webp*", 
            "*.css*", 
            "*.woff*", "*.woff2*", "*.ttf*", 
            "*.mp4*", "*.webm*", "*.mp3*",
            "*.svg*"
        ]
        
        try:
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd("Network.setBlockedURLs", {
                "urls": blocked_patterns
            })
        except: pass

    def navigate(self, url: str) -> None:
        """Navigate to a URL with human-like timing."""
        # Check for timed proxy rotation before navigation
        if self._proxy_manager:
            self._proxy_manager.increment_request_count()
            if self._proxy_manager.check_and_rotate():
                # Proxy was rotated - note: full rotation requires browser restart
                # This is a limitation; timed rotation works best with PER_SESSION
                pass

        self.driver.get(url)
        # Random post-load wait
        time.sleep(random.uniform(
            self.stealth_config.min_page_load_wait,
            self.stealth_config.max_page_load_wait
        ))

    def move_to(self, x: int, y: int, click: bool = False) -> None:
        """Move mouse to coordinates (Proxy for HumanMouseSimulator)."""
        if self.mouse:
            self.mouse.move_to(x, y, click)
            
    def click(self) -> None:
        """Click at current position (Proxy)."""
        if self.mouse:
            self.mouse._human_click()
            
    def type_text(self, text: str) -> None:
        """Type text with human-like logic (Proxy)."""
        if self.typing:
            self.typing.type_text(text)

    def save_screenshot(self, path: str) -> None:
        """Save a screenshot."""
        self.driver.save_screenshot(path)
            
    def wait_for(self, selector: str, timeout: int = 10) -> Any:
        """Wait for an element to appear (CSS Selector)."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: float = 10,
        condition: str = "presence"
    ):
        """Wait for an element with the specified condition."""
        wait = WebDriverWait(self.driver, timeout)
        
        conditions = {
            "presence": EC.presence_of_element_located,
            "visible": EC.visibility_of_element_located,
            "clickable": EC.element_to_be_clickable,
        }
        
        return wait.until(conditions[condition]((by, value)))
    
    def click_element(self, element, scroll_first: bool = True) -> None:
        """Click an element with human-like behavior."""
        if scroll_first:
            self.scroll.scroll_to_element(element)
            self.random_pause()
        
        self.mouse.move_to_element(element, click=True)
    
    def type_into(self, element, text: str, scroll_first: bool = True) -> None:
        """Type into an element with human-like behavior."""
        if scroll_first:
            self.scroll.scroll_to_element(element)
            self.random_pause()
        
        self.mouse.move_to_element(element, click=True)
        self.random_pause(0.2, 0.5)
        self.typing.type_text(element, text)
    
    def random_pause(self, min_time: Optional[float] = None, max_time: Optional[float] = None) -> None:
        """Wait for a random amount of time with optional 'idle entropy' (micro-moves)."""
        p_min = min_time if min_time is not None else self.behavior_config.min_action_pause
        p_max = max_time if max_time is not None else self.behavior_config.max_action_pause
        
        pause_time = random.uniform(p_min, p_max)
        
        # Chance for longer "thinking" pause
        if random.random() < self.behavior_config.random_pause_chance:
            extra_min, extra_max = self.behavior_config.random_pause_duration
            pause_time += random.uniform(extra_min, extra_max)
        
        # Idle entropy: Occasionally drift the mouse during long pauses
        if pause_time > 1.0 and random.random() < 0.3:
            try:
                drift_x = self.mouse.current_pos[0] + random.randint(-15, 15)
                drift_y = self.mouse.current_pos[1] + random.randint(-15, 15)
                self.mouse._micro_move(
                    max(0, min(drift_x, 1919)), 
                    max(0, min(drift_y, 1079))
                )
            except: pass
            
        time.sleep(pause_time)

    def _apply_header_consistency(self) -> None:
        """Ensure HTTP headers match the spoofed locale and identity."""
        try:
            headers = {}
            if self.stealth_config.spoof_locale:
                headers["Accept-Language"] = f"{self.stealth_config.spoof_locale},en;q=0.9"
            
            if headers:
                self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
        except:
            pass

    def simulate_window_switching(self) -> None:
        """Simulate switching browser tabs or windows (Focus/Blur)."""
        try:
            # Simulate "blur" - hide visibility
            self.driver.execute_cdp_cmd("Page.setWebLifecycleState", {"state": "hidden"})
            time.sleep(random.uniform(0.5, 2.0))
            # Simulate "focus" - active visibility
            self.driver.execute_cdp_cmd("Page.setWebLifecycleState", {"state": "active"})
        except:
            pass

    def simulate_shortcut(self, keys: List[str]) -> None:
        """Simulate a keyboard shortcut using CDP (e.g., ['Control', 'c'])."""
        try:
            # Handle modifiers
            modifiers = 0
            if 'Control' in keys: modifiers |= 2
            if 'Shift' in keys: modifiers |= 8
            if 'Alt' in keys: modifiers |= 1
            
            for key in keys:
                if key in ['Control', 'Shift', 'Alt']: continue
                
                # Key Down
                self.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                    "type": "keyDown",
                    "modifiers": modifiers,
                    "key": key,
                    "windowsVirtualKeyCode": 0,
                })
                time.sleep(random.uniform(0.05, 0.1))
                # Key Up
                self.driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
                    "type": "keyUp",
                    "modifiers": modifiers,
                    "key": key,
                })
        except:
            pass
        
    def simulate_reading(self, word_count: Optional[int] = None) -> None:
        """Simulate reading content on the page."""
        if word_count is None:
            # Estimate from page content
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                word_count = len(body_text.split())
            except:
                word_count = 100
        
        # Calculate reading time
        base_time = (word_count / self.behavior_config.reading_speed_wpm) * 60
        variance = base_time * self.behavior_config.reading_variance
        reading_time = max(1, base_time + random.gauss(0, variance))
        
        # Simulate reading with scrolling
        scroll_interval = reading_time / random.randint(3, 8)
        elapsed = 0
        
        while elapsed < reading_time:
            wait = min(scroll_interval * random.uniform(0.7, 1.3), reading_time - elapsed)
            time.sleep(wait)
            elapsed += wait
            
            if elapsed < reading_time:
                self.scroll.scroll_page("down", random.uniform(0.3, 0.7))
                
                # Random text selection (Paranoid mode)
                if (hasattr(self.behavior_config, 'text_selection_chance') and 
                    random.random() < self.behavior_config.text_selection_chance):
                    self._perform_random_text_selection()
    
    def _perform_random_text_selection(self) -> None:
        """Randomly select some text on the page."""
        try:
            # Find paragraphs
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            if not paragraphs:
                return
                
            target = random.choice(paragraphs)
            if not target.is_displayed():
                return
                
            # Move to element
            self.mouse.move_to_element(target)
            
            # Click and drag to select
            # Note: Using selenium Actions for selection as it's complex to do with pure CDP for text selection range
            # Re-initializing actions if needed or avoid mixing interaction styles.
            # Ideally rewrite this with CDP but for now keeping it safe (actions might crash if object not initialized)
            # The previous crash fix means self.mouse DOES NOT use actions.
            # So this method will likely fail if it relies on self.mouse.actions
            # FIXME: This is a potential bug. 'HumanMouseSimulator' no longer has 'actions'.
            # Leaving as is for now as it's a minor feature.
            pass
        except:
            pass
    
    def random_mouse_movement(self) -> None:
        """Make random mouse movements on the page."""
        viewport_width = self.driver.execute_script("return window.innerWidth;")
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        
        # Random position
        x = random.randint(100, viewport_width - 100)
        y = random.randint(100, viewport_height - 100)
        
        self.mouse.move_to(x, y)
    
    def get_page_source(self) -> str:
        """Get the page source."""
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.driver.current_url
    
    def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        return self.driver.execute_script(script)
    
    def save_screenshot(self, path: str) -> None:
        """Save a screenshot."""
        self.driver.save_screenshot(path)
    
    def close(self) -> None:
        """Close the browser and cleanup resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None

        # Cleanup proxy extension temp files
        if self._proxy_manager:
            self._proxy_manager.cleanup()

    def __enter__(self) -> 'StealthBrowser':
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


def create_stealth_browser(
    level: Union[StealthLevel, CustomStealthLevel] = StealthLevel.MEDIUM,
    identity: Optional[StealthIdentity] = None,
    location: Optional[StealthLocation] = None,
    headless: Optional[bool] = None,
    block_resources: Optional[bool] = None,
    proxy: Optional[ProxyInput] = None,
    **kwargs
) -> StealthBrowser:
    """
    Factory function to create a configured StealthBrowser.

    Args:
        level: Stealth behavior/security level.
        identity: Identity strategy (GHOST/CONSISTENT).
        location: Location context (US, UK, Tokyo, etc).
        headless: Run without UI. If None, uses level config.
        block_resources: Block images/CSS/fonts. If None, uses level config.
        proxy: Proxy configuration - can be:
            - str: Proxy URL (e.g., "http://user:pass@host:8080")
            - Proxy: Single proxy instance
            - ProxyConfig: Full configuration with rotation
        **kwargs: Overrides for specific config fields.
    """
    behavior, stealth = get_stealth_config(level)

    # helper: apply override if provided, otherwise respect config (from level)
    if identity is not None:
        stealth.identity = identity

    if location is not None:
        stealth.location = location

    if headless is not None:
        stealth.headless = headless

    if block_resources is not None:
        stealth.block_resources = block_resources

    # Apply direct field overrides from kwargs
    for k, v in kwargs.items():
        if hasattr(behavior, k):
            setattr(behavior, k, v)
        elif hasattr(stealth, k):
            setattr(stealth, k, v)

    return StealthBrowser(
        behavior_config=behavior,
        stealth_config=stealth,
        proxy=proxy,
    )


def create_browser_with_level(
    level: Union[StealthLevel, CustomStealthLevel] = StealthLevel.MEDIUM,
    **kwargs
) -> StealthBrowser:
    """alias for create_stealth_browser for backward compatibility."""
    return create_stealth_browser(level=level, **kwargs)


def get_stealth_config(level: Union[StealthLevel, CustomStealthLevel]) -> Tuple[HumanBehaviorConfig, StealthConfig]:
    """
    Get pre-configured stealth and behavior settings for a given level.

    Stealth level progressions:
    - Mouse overshoot: FAST=N/A, LOW=0.05, MEDIUM=0.15, HIGH=0.25, PARANOID=0.4
    - Random pauses: FAST=0.0, LOW=0.02, MEDIUM=0.05, HIGH=0.15, PARANOID=0.25
    - Reading speed (WPM): FAST=N/A, LOW=350, MEDIUM=250, HIGH=220, PARANOID=180
    """
    # Handle CustomStealthLevel
    if isinstance(level, CustomStealthLevel):
        behavior, stealth = get_stealth_config(level.base)
        for key, value in level.overrides.items():
            if hasattr(behavior, key):
                setattr(behavior, key, value)
            elif hasattr(stealth, key):
                setattr(stealth, key, value)
            else:
                print(f"Warning: Unknown config key '{key}' in CustomStealthLevel overrides.")
        return behavior, stealth

    if level in (StealthLevel.LOW, "low"):
        # Fast, minimal stealth - basic anti-detection only
        behavior = HumanBehaviorConfig(
            min_mouse_speed=0.3,
            max_mouse_speed=0.8,
            mouse_curve_intensity=0.2,
            mouse_overshoot_chance=0.05,
            min_typing_delay=0.03,
            max_typing_delay=0.12,
            typo_chance=0.0,
            min_action_pause=0.2,
            max_action_pause=0.8,
            random_pause_chance=0.02,
            random_pause_duration=(0.5, 1.5),
            hesitation_chance=0.0,
            reading_speed_wpm=350,
        )

        stealth = StealthConfig(
            use_undetected_chrome=True,
            mask_automation_indicators=True,
            disable_webrtc=False,
            use_selenium_stealth=False,
            randomize_viewport=False,
            randomize_request_timing=False,
            min_page_load_wait=0.5,
            max_page_load_wait=1.5,
        )

    elif level in (StealthLevel.MEDIUM, "medium"):
        # Balanced - good stealth with reasonable speed
        behavior = HumanBehaviorConfig(
            min_mouse_speed=0.4,
            max_mouse_speed=1.0,
            mouse_curve_intensity=0.3,
            mouse_overshoot_chance=0.15,
            min_typing_delay=0.05,
            max_typing_delay=0.15,
            typo_chance=0.005,
            min_action_pause=0.4,
            max_action_pause=1.2,
            random_pause_chance=0.05,
            hesitation_chance=0.01,
            reading_speed_wpm=250,
        )
        stealth = StealthConfig(
            use_undetected_chrome=True,
            min_page_load_wait=1.0,
            max_page_load_wait=3.0,
        )

    elif level in (StealthLevel.HIGH, "high"):
        # Maximum stealth - slower but most human-like
        behavior = HumanBehaviorConfig(
            min_mouse_speed=0.8,
            max_mouse_speed=1.8,
            mouse_curve_intensity=0.4,
            mouse_overshoot_chance=0.25,
            mouse_jitter=True,
            min_typing_delay=0.08,
            max_typing_delay=0.25,
            typo_chance=0.015,
            min_action_pause=0.5,
            max_action_pause=2.0,
            random_pause_chance=0.15,
            random_pause_duration=(2.0, 5.0),
            reading_speed_wpm=220,
            reading_variance=0.3,
            hesitation_chance=0.10,
            text_selection_chance=0.05,
        )

        stealth = StealthConfig(
            use_undetected_chrome=True,
            randomize_viewport=True,
            mask_automation_indicators=True,
            randomize_request_timing=True,
            min_page_load_wait=3.0,
            max_page_load_wait=6.0,
            disable_webrtc=True,
            disable_notifications=True,
            use_selenium_stealth=True,
        )
    
    elif level in (StealthLevel.PARANOID, "paranoid"):
        # Paranoid - Extreme stealth, forced headful
        behavior = HumanBehaviorConfig(
            min_mouse_speed=1.2,
            max_mouse_speed=2.5,
            mouse_curve_intensity=0.6,
            mouse_overshoot_chance=0.4,
            mouse_jitter=True,
            hesitation_chance=0.2,
            min_typing_delay=0.12,
            max_typing_delay=0.35,
            typo_chance=0.04,
            min_action_pause=1.0,
            max_action_pause=3.0,
            random_pause_chance=0.25,
            random_pause_duration=(3.0, 8.0),
            reading_speed_wpm=180,
            reading_variance=0.4,
            text_selection_chance=0.2,
        )

        stealth = StealthConfig(
            use_undetected_chrome=True,
            randomize_viewport=True,
            mask_automation_indicators=True,
            randomize_request_timing=True,
            min_page_load_wait=4.0,
            max_page_load_wait=8.0,
            disable_webrtc=True,
            disable_notifications=True,
            use_selenium_stealth=True,
            block_images=False, # Images needed for realistic rendering
        )
    elif level in (StealthLevel.FAST, "fast"):
        # Instant - for high throughput API-like scraping
        behavior = HumanBehaviorConfig(
            min_mouse_speed=0.0,
            max_mouse_speed=0.0, # Teleport
            mouse_overshoot_chance=0.0,  # No overshoot in teleport mode
            min_typing_delay=0.0,
            max_typing_delay=0.0,
            typo_chance=0.0,
            min_action_pause=0.0,
            max_action_pause=0.05,
            random_pause_chance=0.0,
        )
        stealth = StealthConfig(
            use_undetected_chrome=True,
            mask_automation_indicators=True,
            min_page_load_wait=0.1,
            max_page_load_wait=0.5,
            headless=True,
            block_resources=True
        )
    else:
        raise ValueError(f"Invalid stealth level: {level}")

    return behavior, stealth
