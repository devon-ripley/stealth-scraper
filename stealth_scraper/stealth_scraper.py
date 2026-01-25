"""
Ultimate Stealth Web Scraper
Designed to be undetectable by bot detection systems.
"""

import random
import time
import math
import json
import platform
from typing import Optional, Tuple, List, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import numpy as np
from scipy.interpolate import splprep, splev

# Optional selenium-stealth import
try:
    from selenium_stealth import stealth
    SELENIUM_STEALTH_AVAILABLE = True
except ImportError:
    SELENIUM_STEALTH_AVAILABLE = False


@dataclass
class HumanBehaviorConfig:
    """Configuration for human-like behavior simulation."""
    
    # Mouse movement settings
    min_mouse_speed: float = 0.5  # seconds
    max_mouse_speed: float = 2.0
    mouse_curve_intensity: float = 0.3  # How curved the mouse path is
    mouse_overshoot_chance: float = 0.15  # Chance to overshoot target
    mouse_jitter: bool = True  # Add small random movements
    
    # Scrolling settings
    scroll_style: str = "smooth"  # smooth, stepped, or mixed
    min_scroll_pause: float = 0.1
    max_scroll_pause: float = 0.5
    scroll_variance: float = 0.3  # Variance in scroll distance
    
    # Typing settings
    min_typing_delay: float = 0.05
    max_typing_delay: float = 0.25
    typo_chance: float = 0.02  # Chance to make and correct a typo
    
    # General behavior
    min_action_pause: float = 0.3
    max_action_pause: float = 2.0
    random_pause_chance: float = 0.1  # Chance to take a random longer pause
    random_pause_duration: Tuple[float, float] = (2.0, 8.0)
    
    # Reading simulation
    reading_speed_wpm: int = 250  # Words per minute
    reading_variance: float = 0.3


@dataclass  
class StealthConfig:
    """Configuration for stealth/anti-detection measures."""
    
    # Browser fingerprint
    use_undetected_chrome: bool = True
    randomize_viewport: bool = True
    viewport_sizes: List[Tuple[int, int]] = field(default_factory=lambda: [
        (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
        (1280, 720), (1600, 900), (1280, 800), (1680, 1050),
    ])
    
    # WebDriver detection evasion
    remove_webdriver_property: bool = True
    mask_automation_indicators: bool = True
    
    # Request patterns
    randomize_request_timing: bool = True
    min_page_load_wait: float = 2.0
    max_page_load_wait: float = 6.0
    
    # Session behavior
    use_persistent_profile: bool = False
    profile_path: Optional[str] = None
    clear_cookies_chance: float = 0.05
    
    # Advanced stealth options
    disable_webrtc: bool = True  # Prevent WebRTC IP leak
    spoof_timezone: Optional[str] = None  # e.g., "America/New_York"
    spoof_locale: Optional[str] = None  # e.g., "en-US"
    spoof_geolocation: Optional[Tuple[float, float]] = None  # (latitude, longitude)
    block_images: bool = False  # Faster loading, less human-like
    disable_notifications: bool = True
    disable_popup_blocking: bool = False
    use_selenium_stealth: bool = True  # Use selenium-stealth library


@dataclass
class ProxyConfig:
    """Configuration for DataImpulse rotating residential proxies.
    
    DataImpulse proxy format:
    - Host: gw.dataimpulse.com
    - Port: 823
    - Username format with targeting: username__cr.{country};city.{city}
    
    Pricing note: City-level targeting doubles the rate (~$2/GB vs ~$1/GB).
    """
    
    enabled: bool = False
    username: str = ""
    password: str = ""
    
    # DataImpulse defaults
    host: str = "gw.dataimpulse.com"
    port: int = 823
    
    # Geotargeting
    country: str = "us"  # ISO country code
    city: Optional[str] = None  # e.g., "newyork", "losangeles", "saltlakecity"


class BezierCurve:
    """Generate bezier curves for natural mouse movement."""
    
    @staticmethod
    def calculate_point(t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate a point on a bezier curve at parameter t."""
        n = len(points) - 1
        x, y = 0.0, 0.0
        for i, (px, py) in enumerate(points):
            binomial = math.comb(n, i)
            term = binomial * (t ** i) * ((1 - t) ** (n - i))
            x += term * px
            y += term * py
        return x, y
    
    @staticmethod
    def generate_curve(
        start: Tuple[int, int],
        end: Tuple[int, int],
        control_points: int = 2,
        intensity: float = 0.3
    ) -> List[Tuple[int, int]]:
        """Generate a bezier curve path between two points."""
        points = [start]
        
        # Generate control points with some randomness
        for i in range(control_points):
            t = (i + 1) / (control_points + 1)
            base_x = start[0] + (end[0] - start[0]) * t
            base_y = start[1] + (end[1] - start[1]) * t
            
            # Add perpendicular offset for curve
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = math.sqrt(dx * dx + dy * dy)
            
            if length > 0:
                # Perpendicular direction
                perp_x = -dy / length
                perp_y = dx / length
                
                offset = random.gauss(0, length * intensity)
                ctrl_x = base_x + perp_x * offset
                ctrl_y = base_y + perp_y * offset
                points.append((ctrl_x, ctrl_y))
        
        points.append(end)
        
        # Sample the curve
        path = []
        num_samples = max(20, int(math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) / 5))
        
        for i in range(num_samples + 1):
            t = i / num_samples
            x, y = BezierCurve.calculate_point(t, points)
            path.append((int(x), int(y)))
        
        return path


class HumanMouseSimulator:
    """Simulate realistic human mouse movements."""
    
    def __init__(self, driver: webdriver.Chrome, config: HumanBehaviorConfig):
        self.driver = driver
        self.config = config
        self.current_pos = (0, 0)
        self.actions = ActionChains(driver)
    
    def _add_jitter(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Add small random jitter to mouse path."""
        if not self.config.mouse_jitter:
            return path
        
        jittered = []
        for i, (x, y) in enumerate(path):
            if i == 0 or i == len(path) - 1:
                jittered.append((x, y))
            else:
                jx = x + random.randint(-2, 2)
                jy = y + random.randint(-2, 2)
                jittered.append((jx, jy))
        return jittered
    
    def _calculate_speed_curve(self, path_length: int) -> List[float]:
        """Calculate variable speed along path (slow start/end, fast middle)."""
        speeds = []
        for i in range(path_length):
            t = i / max(1, path_length - 1)
            # Ease in-out curve
            if t < 0.5:
                speed = 2 * t * t
            else:
                speed = 1 - (-2 * t + 2) ** 2 / 2
            speeds.append(speed)
        return speeds
    
    def move_to(self, x: int, y: int, click: bool = False) -> None:
        """Move mouse to coordinates with human-like motion."""
        # Generate curved path
        path = BezierCurve.generate_curve(
            self.current_pos,
            (x, y),
            control_points=random.randint(1, 3),
            intensity=self.config.mouse_curve_intensity
        )
        
        # Add jitter
        path = self._add_jitter(path)
        
        # Calculate timing
        total_time = random.uniform(
            self.config.min_mouse_speed,
            self.config.max_mouse_speed
        )
        speeds = self._calculate_speed_curve(len(path))
        
        # Execute movement
        self.actions.reset_actions()
        
        prev_x, prev_y = self.current_pos
        for i, (px, py) in enumerate(path[1:], 1):
            dx = px - prev_x
            dy = py - prev_y
            
            self.actions.move_by_offset(dx, dy)
            prev_x, prev_y = px, py
            
            # Variable delay based on position in path
            if i < len(path) - 1:
                base_delay = total_time / len(path)
                speed_factor = 0.5 + speeds[i]
                delay = base_delay * speed_factor * random.uniform(0.8, 1.2)
                self.actions.pause(delay)
        
        self.actions.perform()
        self.current_pos = (x, y)
        
        # Possible overshoot and correction
        if random.random() < self.config.mouse_overshoot_chance:
            overshoot_x = x + random.randint(-20, 20)
            overshoot_y = y + random.randint(-15, 15)
            self._micro_move(overshoot_x, overshoot_y)
            time.sleep(random.uniform(0.1, 0.3))
            self._micro_move(x, y)
        
        if click:
            self._human_click()
    
    def _micro_move(self, x: int, y: int) -> None:
        """Small correction movement."""
        self.actions.reset_actions()
        dx = x - self.current_pos[0]
        dy = y - self.current_pos[1]
        self.actions.move_by_offset(dx, dy)
        self.actions.perform()
        self.current_pos = (x, y)
    
    def _human_click(self) -> None:
        """Perform a human-like click with variable timing."""
        self.actions.reset_actions()
        
        # Random pre-click pause
        time.sleep(random.uniform(0.05, 0.15))
        
        # Click with random hold time
        self.actions.click_and_hold()
        self.actions.pause(random.uniform(0.05, 0.12))
        self.actions.release()
        self.actions.perform()
        
        # Post-click pause
        time.sleep(random.uniform(0.1, 0.3))
    
    def move_to_element(self, element, click: bool = False) -> None:
        """Move to a web element with human-like motion."""
        location = element.location
        size = element.size
        
        # Click somewhere within the element, not dead center
        x = location['x'] + random.randint(
            int(size['width'] * 0.2),
            int(size['width'] * 0.8)
        )
        y = location['y'] + random.randint(
            int(size['height'] * 0.2),
            int(size['height'] * 0.8)
        )
        
        self.move_to(x, y, click=click)


class HumanScrollSimulator:
    """Simulate realistic human scrolling behavior."""
    
    def __init__(self, driver: webdriver.Chrome, config: HumanBehaviorConfig):
        self.driver = driver
        self.config = config
    
    def scroll_to(self, target_y: int, style: Optional[str] = None) -> None:
        """Scroll to a vertical position with human-like behavior."""
        style = style or self.config.scroll_style
        current_y = self.driver.execute_script("return window.pageYOffset;")
        distance = target_y - current_y
        
        if style == "smooth":
            self._smooth_scroll(current_y, target_y)
        elif style == "stepped":
            self._stepped_scroll(current_y, target_y)
        else:
            # Mixed - randomly choose
            if random.random() < 0.5:
                self._smooth_scroll(current_y, target_y)
            else:
                self._stepped_scroll(current_y, target_y)
    
    def _smooth_scroll(self, start_y: int, end_y: int) -> None:
        """Smooth scrolling with easing."""
        distance = end_y - start_y
        duration = abs(distance) / random.uniform(800, 1500)  # pixels per second
        steps = max(10, int(duration * 60))  # ~60fps
        
        for i in range(steps + 1):
            t = i / steps
            # Ease out cubic
            eased_t = 1 - (1 - t) ** 3
            current = start_y + distance * eased_t
            
            self.driver.execute_script(f"window.scrollTo(0, {int(current)});")
            
            # Variable frame timing
            base_delay = duration / steps
            actual_delay = base_delay * random.uniform(0.8, 1.2)
            time.sleep(actual_delay)
            
            # Occasional micro-pause
            if random.random() < 0.05:
                time.sleep(random.uniform(0.05, 0.15))
    
    def _stepped_scroll(self, start_y: int, end_y: int) -> None:
        """Stepped scrolling like mouse wheel."""
        distance = end_y - start_y
        direction = 1 if distance > 0 else -1
        remaining = abs(distance)
        current = start_y
        
        while remaining > 0:
            # Variable scroll step (like mousewheel)
            base_step = random.randint(80, 150)
            variance = base_step * self.config.scroll_variance
            step = int(base_step + random.gauss(0, variance))
            step = min(step, remaining)
            
            current += step * direction
            self.driver.execute_script(f"window.scrollTo(0, {int(current)});")
            remaining -= step
            
            # Pause between steps
            pause = random.uniform(
                self.config.min_scroll_pause,
                self.config.max_scroll_pause
            )
            time.sleep(pause)
            
            # Occasional longer pause (reading)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 2.0))
    
    def scroll_page(self, direction: str = "down", amount: float = 0.7) -> None:
        """Scroll by a portion of the viewport."""
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        current_y = self.driver.execute_script("return window.pageYOffset;")
        
        scroll_amount = int(viewport_height * amount * random.uniform(0.8, 1.2))
        
        if direction == "down":
            target_y = current_y + scroll_amount
        else:
            target_y = max(0, current_y - scroll_amount)
        
        self.scroll_to(target_y)
    
    def scroll_to_element(self, element, align: str = "center") -> None:
        """Scroll to bring an element into view."""
        location = element.location
        size = element.size
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        
        if align == "center":
            target_y = location['y'] - (viewport_height - size['height']) / 2
        elif align == "top":
            target_y = location['y'] - 100
        else:  # bottom
            target_y = location['y'] - viewport_height + size['height'] + 100
        
        target_y = max(0, int(target_y))
        self.scroll_to(target_y)


class HumanTypingSimulator:
    """Simulate realistic human typing behavior."""
    
    def __init__(self, driver: webdriver.Chrome, config: HumanBehaviorConfig):
        self.driver = driver
        self.config = config
        
        # Common typo patterns (wrong key -> intended key)
        self.typo_map = {
            'a': ['s', 'q', 'z'],
            'b': ['v', 'n', 'g'],
            'c': ['x', 'v', 'd'],
            'd': ['s', 'f', 'e'],
            'e': ['w', 'r', 'd'],
            'f': ['d', 'g', 'r'],
            'g': ['f', 'h', 't'],
            'h': ['g', 'j', 'y'],
            'i': ['u', 'o', 'k'],
            'j': ['h', 'k', 'u'],
            'k': ['j', 'l', 'i'],
            'l': ['k', 'o', 'p'],
            'm': ['n', 'k'],
            'n': ['b', 'm', 'j'],
            'o': ['i', 'p', 'l'],
            'p': ['o', 'l'],
            'q': ['w', 'a'],
            'r': ['e', 't', 'f'],
            's': ['a', 'd', 'w'],
            't': ['r', 'y', 'g'],
            'u': ['y', 'i', 'j'],
            'v': ['c', 'b', 'f'],
            'w': ['q', 'e', 's'],
            'x': ['z', 'c', 's'],
            'y': ['t', 'u', 'h'],
            'z': ['a', 'x'],
        }
    
    def type_text(self, element, text: str, clear_first: bool = True) -> None:
        """Type text into an element with human-like behavior."""
        if clear_first:
            element.clear()
            time.sleep(random.uniform(0.1, 0.3))
        
        element.click()
        time.sleep(random.uniform(0.1, 0.3))
        
        i = 0
        while i < len(text):
            char = text[i]
            
            # Possible typo
            if (random.random() < self.config.typo_chance and 
                char.lower() in self.typo_map):
                # Make typo
                typo_char = random.choice(self.typo_map[char.lower()])
                if char.isupper():
                    typo_char = typo_char.upper()
                
                element.send_keys(typo_char)
                time.sleep(random.uniform(0.1, 0.4))
                
                # Realize mistake and correct
                element.send_keys(Keys.BACKSPACE)
                time.sleep(random.uniform(0.05, 0.15))
            
            # Type the correct character
            element.send_keys(char)
            
            # Variable delay
            delay = random.uniform(
                self.config.min_typing_delay,
                self.config.max_typing_delay
            )
            
            # Longer pause after punctuation
            if char in '.!?,;:':
                delay *= random.uniform(1.5, 3.0)
            
            # Longer pause after space (word boundary)
            elif char == ' ':
                delay *= random.uniform(1.2, 2.0)
            
            time.sleep(delay)
            i += 1
            
            # Occasional thinking pause
            if random.random() < 0.02:
                time.sleep(random.uniform(0.5, 1.5))


class StealthBrowser:
    """Main stealth browser class with anti-detection measures."""
    
    def __init__(
        self,
        behavior_config: Optional[HumanBehaviorConfig] = None,
        stealth_config: Optional[StealthConfig] = None,
        proxy_config: Optional['ProxyConfig'] = None,
    ):
        self.behavior_config = behavior_config or HumanBehaviorConfig()
        self.stealth_config = stealth_config or StealthConfig()
        self.proxy_config = proxy_config
        self.driver: Optional[webdriver.Chrome] = None
        self.mouse: Optional[HumanMouseSimulator] = None
        self.scroll: Optional[HumanScrollSimulator] = None
        self.typing: Optional[HumanTypingSimulator] = None
    
    
    def _build_proxy_url(self) -> str:
        """Build DataImpulse proxy URL with geotargeting parameters.
        
        Format: http://username__cr.{country};city.{city}:password@host:port
        """
        if not self.proxy_config:
            return ""
        
        # Build targeting string
        targeting = f"cr.{self.proxy_config.country}"
        if self.proxy_config.city:
            # Normalize city name (lowercase, no spaces)
            city = self.proxy_config.city.lower().replace(" ", "").replace("-", "")
            targeting += f";city.{city}"
        
        # Build username with targeting
        username_with_targeting = f"{self.proxy_config.username}__{targeting}"
        
        return (
            f"http://{username_with_targeting}:{self.proxy_config.password}"
            f"@{self.proxy_config.host}:{self.proxy_config.port}"
        )
    
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
        options.add_argument("--disable-extensions")
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
        
        # Proxy is handled via selenium-wire in start(), not here via extension
        pass
        
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
        """Inject JavaScript to mask automation indicators."""
        stealth_scripts = """
        // ========================================
        // WEBDRIVER PROPERTY MASKING
        // ========================================
        
        // Overwrite navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        
        // Delete webdriver property completely
        delete navigator.__proto__.webdriver;
        
        // ========================================
        // CHROME RUNTIME MASKING
        // ========================================
        
        // Overwrite chrome runtime to look like a real Chrome instance
        window.chrome = {
            runtime: {
                connect: function() {},
                sendMessage: function() {},
                onMessage: {
                    addListener: function() {},
                    removeListener: function() {}
                }
            },
            loadTimes: function() {
                return {
                    commitLoadTime: Date.now() / 1000 - Math.random() * 5,
                    connectionInfo: "h2",
                    finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 2,
                    finishLoadTime: Date.now() / 1000 - Math.random(),
                    firstPaintAfterLoadTime: 0,
                    firstPaintTime: Date.now() / 1000 - Math.random() * 3,
                    navigationType: "Other",
                    npnNegotiatedProtocol: "h2",
                    requestTime: Date.now() / 1000 - Math.random() * 6,
                    startLoadTime: Date.now() / 1000 - Math.random() * 5,
                    wasAlternateProtocolAvailable: false,
                    wasFetchedViaSpdy: true,
                    wasNpnNegotiated: true
                };
            },
            csi: function() {
                return {
                    onloadT: Date.now(),
                    pageT: Math.random() * 1000 + 500,
                    startE: Date.now() - Math.random() * 5000,
                    tran: 15
                };
            },
            app: {
                isInstalled: false,
                InstallState: {
                    DISABLED: "disabled",
                    INSTALLED: "installed",
                    NOT_INSTALLED: "not_installed"
                },
                RunningState: {
                    CANNOT_RUN: "cannot_run",
                    READY_TO_RUN: "ready_to_run",
                    RUNNING: "running"
                }
            }
        };
        
        // ========================================
        // PERMISSIONS API MASKING
        // ========================================
        
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // ========================================
        // PLUGINS MASKING
        // ========================================
        
        // Create realistic plugin array
        const makePluginArray = () => {
            const plugins = [
                {
                    name: "Chrome PDF Plugin",
                    filename: "internal-pdf-viewer",
                    description: "Portable Document Format"
                },
                {
                    name: "Chrome PDF Viewer", 
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    description: ""
                },
                {
                    name: "Native Client",
                    filename: "internal-nacl-plugin",
                    description: ""
                }
            ];
            
            const pluginArray = Object.create(PluginArray.prototype);
            plugins.forEach((p, i) => {
                const plugin = Object.create(Plugin.prototype);
                plugin.name = p.name;
                plugin.filename = p.filename;
                plugin.description = p.description;
                pluginArray[i] = plugin;
            });
            pluginArray.length = plugins.length;
            pluginArray.item = (i) => pluginArray[i];
            pluginArray.namedItem = (name) => plugins.find(p => p.name === name);
            pluginArray.refresh = () => {};
            return pluginArray;
        };
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => makePluginArray(),
            configurable: true
        });
        
        // ========================================
        // LANGUAGES MASKING
        // ========================================
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
            configurable: true
        });
        
        Object.defineProperty(navigator, 'language', {
            get: () => 'en-US',
            configurable: true
        });
        
        // ========================================
        // HARDWARE CONCURRENCY (CPU CORES)
        // ========================================
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => [4, 8, 12, 16][Math.floor(Math.random() * 4)],
            configurable: true
        });
        
        // ========================================
        // DEVICE MEMORY
        // ========================================
        
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => [4, 8, 16][Math.floor(Math.random() * 3)],
            configurable: true
        });
        
        // ========================================
        // MAX TOUCH POINTS
        // ========================================
        
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => 0,  // Desktop typically has 0
            configurable: true
        });
        
        // ========================================
        // PLATFORM MASKING
        // ========================================
        
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
            configurable: true
        });
        
        // ========================================
        // VENDOR MASKING
        // ========================================
        
        Object.defineProperty(navigator, 'vendor', {
            get: () => 'Google Inc.',
            configurable: true
        });
        
        // ========================================
        // CONNECTION INFO
        // ========================================
        
        if (navigator.connection) {
            Object.defineProperty(navigator.connection, 'rtt', {
                get: () => Math.floor(Math.random() * 100) + 50,
                configurable: true
            });
        }
        
        // ========================================
        // CANVAS FINGERPRINTING PROTECTION
        // ========================================
        
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attributes) {
            const context = originalGetContext.call(this, type, attributes);
            if (type === '2d' && context) {
                const originalFillText = context.fillText.bind(context);
                const originalStrokeText = context.strokeText.bind(context);
                const originalFillRect = context.fillRect.bind(context);
                
                // Add imperceptible noise to canvas operations
                context.fillText = function(...args) {
                    context.shadowBlur = Math.random() * 0.5;
                    context.shadowColor = 'rgba(0,0,0,0.01)';
                    return originalFillText(...args);
                };
                
                context.strokeText = function(...args) {
                    context.shadowBlur = Math.random() * 0.5;
                    context.shadowColor = 'rgba(0,0,0,0.01)';
                    return originalStrokeText(...args);
                };
            }
            return context;
        };
        
        // Modify toDataURL to add noise
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
            // Only modify if canvas has been drawn to
            if (this.width > 0 && this.height > 0) {
                const ctx = this.getContext('2d');
                if (ctx) {
                    // Add a single invisible pixel modification
                    const imageData = ctx.getImageData(0, 0, 1, 1);
                    imageData.data[0] = imageData.data[0] ^ (Math.random() > 0.5 ? 1 : 0);
                    ctx.putImageData(imageData, 0, 0);
                }
            }
            return originalToDataURL.call(this, type, quality);
        };
        
        // ========================================
        // WEBGL FINGERPRINTING PROTECTION
        // ========================================
        
        const getParameterProxyHandler = {
            apply: function(target, thisArg, argumentsList) {
                const param = argumentsList[0];
                const result = Reflect.apply(target, thisArg, argumentsList);
                
                // UNMASKED_VENDOR_WEBGL
                if (param === 37445) {
                    return 'Intel Inc.';
                }
                // UNMASKED_RENDERER_WEBGL
                if (param === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return result;
            }
        };
        
        try {
            const getParameterPrototype = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = new Proxy(getParameterPrototype, getParameterProxyHandler);
            
            // Also handle WebGL2
            if (typeof WebGL2RenderingContext !== 'undefined') {
                const getParameter2Prototype = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = new Proxy(getParameter2Prototype, getParameterProxyHandler);
            }
        } catch (e) {}
        
        // ========================================
        // AUDIO CONTEXT FINGERPRINTING PROTECTION
        // ========================================
        
        const audioContextPrototype = window.AudioContext || window.webkitAudioContext;
        if (audioContextPrototype) {
            const originalCreateOscillator = audioContextPrototype.prototype.createOscillator;
            audioContextPrototype.prototype.createOscillator = function() {
                const oscillator = originalCreateOscillator.call(this);
                // Slightly modify the default frequency
                const originalFrequency = oscillator.frequency.value;
                oscillator.frequency.value = originalFrequency + (Math.random() - 0.5) * 0.01;
                return oscillator;
            };
            
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = function(channel) {
                const data = originalGetChannelData.call(this, channel);
                // Add tiny noise to prevent fingerprinting
                for (let i = 0; i < Math.min(10, data.length); i++) {
                    data[i] += (Math.random() - 0.5) * 0.0001;
                }
                return data;
            };
        }
        
        // ========================================
        // IFRAME CONTENTWINDOW PROTECTION
        // ========================================
        
        // Prevent detection via iframe contentWindow checks
        try {
            const originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    const win = originalContentWindow.get.call(this);
                    if (win) {
                        try {
                            // Try to mask webdriver in iframes too
                            Object.defineProperty(win.navigator, 'webdriver', {
                                get: () => undefined
                            });
                        } catch (e) {}
                    }
                    return win;
                }
            });
        } catch (e) {}
        
        // ========================================
        // SCREEN PROPERTIES
        // ========================================
        
        const screenProps = {
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            width: screen.width,
            height: screen.height,
            colorDepth: 24,
            pixelDepth: 24,
        };
        
        for (const [prop, value] of Object.entries(screenProps)) {
            try {
                Object.defineProperty(screen, prop, {
                    get: () => value,
                    configurable: true
                });
            } catch (e) {}
        }
        
        // ========================================
        // BATTERY API MASKING
        // ========================================
        
        // Some sites check for battery API behavior
        if (navigator.getBattery) {
            navigator.getBattery = async function() {
                return {
                    charging: true,
                    chargingTime: Infinity,
                    dischargingTime: Infinity,
                    level: 1.0,
                    addEventListener: function() {},
                    removeEventListener: function() {}
                };
            };
        }
        
        // ========================================
        // NOTIFICATION PERMISSION
        // ========================================
        
        // Ensure notification permission looks normal
        Object.defineProperty(Notification, 'permission', {
            get: () => 'default',
            configurable: true
        });
        
        console.log = (function(old_console_log) {
            return function() {
                // Filter out any webdriver-related console messages
                const args = Array.from(arguments);
                const hasWebdriver = args.some(arg => 
                    typeof arg === 'string' && 
                    (arg.includes('webdriver') || arg.includes('automation'))
                );
                if (!hasWebdriver) {
                    old_console_log.apply(console, arguments);
                }
            };
        })(console.log);
        """
        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_scripts
        })
    
    def start(self) -> 'StealthBrowser':
        """Initialize the stealth browser."""
        options = self._get_stealth_options()
        
        # Check if using proxy via selenium-wire
        use_proxy = self.proxy_config and self.proxy_config.enabled
        seleniumwire_options = {}
        
        if use_proxy:
            proxy_url = self._build_proxy_url()
            seleniumwire_options = {
                'proxy': {
                    'http': proxy_url,
                    'https': proxy_url,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
        
        if self.stealth_config.use_undetected_chrome:
            if use_proxy:
                try:
                    import seleniumwire.undetected_chromedriver as uc_wire
                    self.driver = uc_wire.Chrome(
                        options=options,
                        seleniumwire_options=seleniumwire_options,
                        headless=False,
                        use_subprocess=True,
                    )
                except ImportError:
                    print("⚠️  selenium-wire not found. Proxy configuration skipped.")
                    # Fallback to standard uc
                    self.driver = uc.Chrome(
                        options=options,
                        headless=False,
                        use_subprocess=True,
                    )
            else:
                self.driver = uc.Chrome(
                    options=options,
                    headless=False,
                    use_subprocess=True,
                )
        else:
            if use_proxy:
                try:
                    from seleniumwire import webdriver as wire_webdriver
                    self.driver = wire_webdriver.Chrome(
                        options=options,
                        seleniumwire_options=seleniumwire_options
                    )
                except ImportError:
                    print("⚠️  selenium-wire not found. Proxy configuration skipped.")
                    self.driver = webdriver.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        
        # Apply selenium-stealth if available and enabled
        if SELENIUM_STEALTH_AVAILABLE and self.stealth_config.use_selenium_stealth:
            self._apply_selenium_stealth()
        
        # Inject stealth scripts via CDP
        if self.stealth_config.mask_automation_indicators:
            self._inject_stealth_scripts()
        
        # Apply CDP-based configurations
        self._apply_cdp_configurations()
        
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
            # Set timezone if specified
            if self.stealth_config.spoof_timezone:
                self.driver.execute_cdp_cmd(
                    "Emulation.setTimezoneOverride",
                    {"timezoneId": self.stealth_config.spoof_timezone}
                )
            
            # Set geolocation if specified
            if self.stealth_config.spoof_geolocation:
                lat, lon = self.stealth_config.spoof_geolocation
                self.driver.execute_cdp_cmd(
                    "Emulation.setGeolocationOverride",
                    {
                        "latitude": lat,
                        "longitude": lon,
                        "accuracy": 100
                    }
                )
            
            # Set locale/language via CDP
            if self.stealth_config.spoof_locale:
                self.driver.execute_cdp_cmd(
                    "Emulation.setLocaleOverride",
                    {"locale": self.stealth_config.spoof_locale}
                )
            
            # Set user agent via CDP for consistency
            if hasattr(self, '_current_user_agent'):
                # Get platform info
                platform_info = {
                    "windows": "Windows",
                    "darwin": "macOS", 
                    "linux": "Linux"
                }.get(platform.system().lower(), "Windows")
                
                self.driver.execute_cdp_cmd(
                    "Emulation.setUserAgentOverride",
                    {
                        "userAgent": self._current_user_agent,
                        "platform": platform_info,
                        "acceptLanguage": "en-US,en;q=0.9",
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
    
    def navigate(self, url: str) -> None:
        """Navigate to a URL with human-like behavior."""
        self.driver.get(url)
        
        # Random wait after page load
        wait_time = random.uniform(
            self.stealth_config.min_page_load_wait,
            self.stealth_config.max_page_load_wait
        )
        time.sleep(wait_time)
        
        # Possible random scroll after load
        if random.random() < 0.3:
            self.scroll.scroll_page("down", random.uniform(0.1, 0.3))
    
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
    
    def random_pause(
        self,
        min_time: Optional[float] = None,
        max_time: Optional[float] = None
    ) -> None:
        """Take a random pause."""
        min_t = min_time or self.behavior_config.min_action_pause
        max_t = max_time or self.behavior_config.max_action_pause
        
        pause_time = random.uniform(min_t, max_t)
        
        # Chance for longer "thinking" pause
        if random.random() < self.behavior_config.random_pause_chance:
            extra_min, extra_max = self.behavior_config.random_pause_duration
            pause_time += random.uniform(extra_min, extra_max)
        
        time.sleep(pause_time)
    
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
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self) -> 'StealthBrowser':
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


# Convenience function
def create_stealth_browser(**kwargs) -> StealthBrowser:
    """Create a stealth browser with optional custom configuration."""
    behavior_config = HumanBehaviorConfig(**{
        k: v for k, v in kwargs.items() 
        if hasattr(HumanBehaviorConfig, k)
    })
    stealth_config = StealthConfig(**{
        k: v for k, v in kwargs.items() 
        if hasattr(StealthConfig, k)
    })
    return StealthBrowser(behavior_config, stealth_config)
