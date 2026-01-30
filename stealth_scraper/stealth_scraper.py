"""
Ultimate Stealth Web Scraper
Designed to be undetectable by bot detection systems.
"""

import random
import time
import math
import json
import platform
from typing import List, Tuple, Optional, Any, Dict, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import os

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

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


class StealthLevel(Enum):
    """Preset stealth levels for easy configuration."""
    LOW = "low"          # Fast, minimal stealth - basic anti-detection only
    MEDIUM = "medium"    # Balanced - good stealth with reasonable speed
    HIGH = "high"        # Maximum stealth - slower but most human-like
    PARANOID = "paranoid"  # Alias for HIGH
    FAST = "fast"        # Instant interactions, minimal stealth (API compatible)


class CustomStealthLevel:
    """
    A custom stealth level allowing granular overrides.
    
    Args:
        base: The base StealthLevel to inherit from (e.g. MEDIUM).
        **overrides: Any parameter from HumanBehaviorConfig or StealthConfig.
    """
    def __init__(self, base: StealthLevel, **overrides):
        self.base = base
        self.overrides = overrides


class StealthIdentity(Enum):
    """Strategies for managing browser identity/fingerprint."""
    GHOST = "ghost"            # Randomize every session (Canvas, WebGL, Fonts)
    CONSISTENT = "consistent"  # Use a deterministic seed to keep fingerprint stable


@dataclass
class StealthLocation:
    """Location context including Timezone, Geolocation, and Languages."""
    timezone: str
    latitude: float
    longitude: float
    locale: str
    languages: List[str]

    @staticmethod
    def US():
        return StealthLocation("America/New_York", 40.7128, -74.0060, "en-US", ["en-US", "en"])
        
    @staticmethod
    def UK():
        return StealthLocation("Europe/London", 51.5074, -0.1278, "en-GB", ["en-GB", "en"])
        
    @staticmethod
    def Tokyo():
        return StealthLocation("Asia/Tokyo", 35.6895, 139.6917, "ja-JP", ["ja-JP", "ja", "en-US"])


@dataclass
class HumanBehaviorConfig:
    """Configuration for human-like behavior simulation."""
    
    # Mouse movement settings
    min_mouse_speed: float = 0.4  # seconds
    max_mouse_speed: float = 1.0
    mouse_curve_intensity: float = 0.3  # How curved the mouse path is
    mouse_overshoot_chance: float = 0.15  # Chance to overshoot target
    mouse_jitter: bool = True  # Add small random movements
    hesitation_chance: float = 0.01  # Chance to hesitate before clicking
    
    # Scrolling settings
    scroll_style: str = "smooth"  # smooth, stepped, or mixed
    min_scroll_pause: float = 0.1
    max_scroll_pause: float = 0.5
    scroll_variance: float = 0.3  # Variance in scroll distance
    
    # Typing settings
    min_typing_delay: float = 0.05
    max_typing_delay: float = 0.15
    typo_chance: float = 0.005  # Chance to make and correct a typo
    
    # General behavior
    min_action_pause: float = 0.4
    max_action_pause: float = 1.2
    random_pause_chance: float = 0.1  # Chance to take a random longer pause
    random_pause_duration: Tuple[float, float] = (2.0, 5.0)
    
    # Reading simulation
    reading_speed_wpm: int = 250  # Words per minute
    reading_variance: float = 0.3
    text_selection_chance: float = 0.0  # Chance to select text while reading


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
    
    # Modular Identity & Location (Phase 2)
    identity: StealthIdentity = StealthIdentity.GHOST
    identity_seed: Optional[str] = None
    location: Optional[StealthLocation] = None
    
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
    use_selenium_stealth: bool = True  # Use selenium-stealth library
    visualize_mouse: bool = False  # Debug only: Visualize mouse cursor with a red dot
    disable_notifications: bool = True
    disable_popup_blocking: bool = False
    
    # Performance & Visibility (Phase 3)
    headless: bool = False             # Run browser invisibly (using --headless=new)
    block_resources: bool = False      # Block images/css/fonts for speed
    block_images: bool = False         # Block images via Chrome preferences





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
        # Optimization: Use larger steps (25px) to reduce Selenium overhead
        # This is overridden by FAST mode teleportation in simulator
        step_size = 25
        num_samples = max(5, int(math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) / step_size))
        
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
        # Get viewport dimensions for clamping
        try:
            viewport = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
            max_x, max_y = viewport[0] - 1, viewport[1] - 1
        except:
            max_x, max_y = 1919, 1079  # Fallback
            
        # Clamp target
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))

        # FAST mode: Teleport instantly via CDP
        if self.config.max_mouse_speed == 0.0:
            self._cdp_move(x, y)
            if click:
                self._human_click()
            return
        
        # Generate curved path for human-like movement
        path = BezierCurve.generate_curve(
            self.current_pos,
            (x, y),
            control_points=random.randint(1, 3),
            intensity=self.config.mouse_curve_intensity
        )
        
        # Add jitter
        path = self._add_jitter(path)
        
        # Clamp path points to viewport
        path = [(max(0, min(px, max_x)), max(0, min(py, max_y))) for px, py in path]
        
        # Calculate timing
        total_time = random.uniform(
            self.config.min_mouse_speed,
            self.config.max_mouse_speed
        )
        speeds = self._calculate_speed_curve(len(path))
        
        # Execute movement via CDP
        for i, (px, py) in enumerate(path[1:], 1):
            # Skip redundant points
            if (px, py) == self.current_pos:
                continue
                
            self._cdp_move(px, py)
            
            # Variable delay based on position in path
            if i < len(path) - 1:
                base_delay = total_time / len(path)
                speed_factor = 0.5 + speeds[i]
                delay = base_delay * speed_factor * random.uniform(0.8, 1.2)
                time.sleep(delay)
        
        # Hesitation logic
        if random.random() < self.config.hesitation_chance:
            self._perform_hesitation()
        
        # Overshoot logic
        if random.random() < self.config.mouse_overshoot_chance:
            overshoot_x = max(0, min(x + random.randint(-20, 20), max_x))
            overshoot_y = max(0, min(y + random.randint(-15, 15), max_y))
            try:
                self._micro_move(overshoot_x, overshoot_y)
                time.sleep(random.uniform(0.1, 0.3))
                self._micro_move(x, y)
            except: pass
        
        if click:
            self._human_click()

    def _cdp_move(self, x: int, y: int) -> None:
        """Move cursor using CDP to avoid Selenium overhead."""
        try:
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mouseMoved",
                "x": x,
                "y": y,
                "button": "none",
                "pointerType": "mouse"
            })
            self.current_pos = (x, y)
        except:
            pass
    
    def _micro_move(self, x: int, y: int) -> None:
        """Small correction movement using CDP."""
        self._cdp_move(x, y)
    
    def _human_click(self) -> None:
        """Simulate a human-like click using CDP."""
        x, y = self.current_pos
        
        # Random pre-click pause (skip in FAST mode)
        if self.config.min_action_pause > 0:
            time.sleep(random.uniform(0.02, 0.08))
            
        try:
            # Mouse Down
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mousePressed",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 1, # Left button pressed
                "clickCount": 1,
                "pointerType": "mouse"
            })
            
            # Short hold time (skip in FAST mode)
            if self.config.min_action_pause > 0:
                time.sleep(random.uniform(0.05, 0.15))
            
            # Mouse Up
            self.driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
                "type": "mouseReleased",
                "x": x,
                "y": y,
                "button": "left",
                "buttons": 0, # Released
                "clickCount": 1,
                "pointerType": "mouse"
            })
        except:
            pass
            
        # Random post-click pause (skip in FAST mode)
        if self.config.min_action_pause > 0:
            time.sleep(random.uniform(0.1, 0.3))

    def _perform_hesitation(self) -> None:
        """Perform a hesitation movement (stop, micro-move, wait)."""
        time.sleep(random.uniform(0.1, 0.4))
        
        # Small random movement nearby using CDP (Fixes ActionChains crash)
        x, y = self.current_pos
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        
        # Move slightly away
        self._micro_move(x + offset_x, y + offset_y)
        time.sleep(random.uniform(0.2, 0.5))
        
        # Move back (roughly)
        self._micro_move(x, y)
        
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
        behavior_config: Optional['HumanBehaviorConfig'] = None,
        stealth_config: Optional['StealthConfig'] = None,
        proxy_config: Optional['ProxyConfig'] = None,
    ):
        """
        Initialize the stealth browser.
        
        Args:
            behavior_config: Configuration for human behavior simulation
            stealth_config: Configuration for browser fingerprinting/stealth
            proxy_config: Configuration for rotating proxies
        """
        self.behavior_config = behavior_config or HumanBehaviorConfig()
        self.stealth_config = stealth_config or StealthConfig()
        self.proxy_config = proxy_config
        self.driver = None
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
            "hardware_concurrency": rng.choice([4, 8, 12, 16]),
            "device_memory": rng.choice([4, 8, 16]),
            "canvas_noise": rng.uniform(0.001, 0.005),
            "audio_noise": rng.uniform(0.0001, 0.0005),
        }

        stealth_scripts = f"""
        const STEALTH_CONFIG = {json.dumps(inject_vars)};
        
        // ========================================
        // WEBDRIVER PROPERTY MASKING
        // ========================================
        
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined,
            configurable: true
        }});
        
        delete navigator.__proto__.webdriver;
        
        // ========================================
        // CHROME RUNTIME MASKING
        // ========================================
        
        window.chrome = {{
            runtime: {{
                connect: function() {{}},
                sendMessage: function() {{}},
                onMessage: {{
                    addListener: function() {{}},
                    removeListener: function() {{}}
                }}
            }},
            loadTimes: function() {{
                return {{
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
                }};
            }},
            csi: function() {{
                return {{
                    onloadT: Date.now(),
                    pageT: Math.random() * 1000 + 500,
                    startE: Date.now() - Math.random() * 5000,
                    tran: 15
                }};
            }},
            app: {{
                isInstalled: false,
                InstallState: {{
                    DISABLED: "disabled",
                    INSTALLED: "installed",
                    NOT_INSTALLED: "not_installed"
                }},
                RunningState: {{
                    CANNOT_RUN: "cannot_run",
                    READY_TO_RUN: "ready_to_run",
                    RUNNING: "running"
                }}
            }}
        }};
        
        // ========================================
        // PERMISSIONS API MASKING
        // ========================================
        
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // ========================================
        // PLUGINS MASKING
        // ========================================
        
        const makePluginArray = () => {{
            const plugins = [
                {{ name: "Chrome PDF Plugin", filename: "internal-pdf-viewer", description: "Portable Document Format" }},
                {{ name: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", description: "" }},
                {{ name: "Native Client", filename: "internal-nacl-plugin", description: "" }}
            ];
            
            const pluginArray = Object.create(PluginArray.prototype);
            plugins.forEach((p, i) => {{
                const plugin = Object.create(Plugin.prototype);
                plugin.name = p.name;
                plugin.filename = p.filename;
                plugin.description = p.description;
                pluginArray[i] = plugin;
            }});
            pluginArray.length = plugins.length;
            return pluginArray;
        }};
        
        Object.defineProperty(navigator, 'plugins', {{
            get: () => makePluginArray(),
            configurable: true
        }});
        
        // ========================================
        // IDENTITY MASKING (MODULAR)
        // ========================================
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => STEALTH_CONFIG.hardware_concurrency,
            configurable: true
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => STEALTH_CONFIG.device_memory,
            configurable: true
        }});

        Object.defineProperty(navigator, 'platform', {{
            get: () => 'Win32',
            configurable: true
        }});
        
        Object.defineProperty(navigator, 'vendor', {{
            get: () => 'Google Inc.',
            configurable: true
        }});
        
        // ========================================
        // CANVAS FINGERPRINTING PROTECTION
        // ========================================
        
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, attributes) {{
            const context = originalGetContext.call(this, type, attributes);
            if (type === '2d' && context) {{
                const originalFillText = context.fillText.bind(context);
                context.fillText = function(...args) {{
                    context.shadowBlur = Math.random() * STEALTH_CONFIG.canvas_noise;
                    return originalFillText(...args);
                }};
            }}
            return context;
        }};
        
        // ========================================
        // WEBGL FINGERPRINTING PROTECTION
        // ========================================
        
        const getParameterProxyHandler = {{
            apply: function(target, thisArg, argumentsList) {{
                const param = argumentsList[0];
                if (param === 37445) return STEALTH_CONFIG.webgl_vendor;
                if (param === 37446) return STEALTH_CONFIG.webgl_renderer;
                return Reflect.apply(target, thisArg, argumentsList);
            }}
        }};
        
        try {{
            WebGLRenderingContext.prototype.getParameter = new Proxy(WebGLRenderingContext.prototype.getParameter, getParameterProxyHandler);
            if (typeof WebGL2RenderingContext !== 'undefined') {{
                WebGL2RenderingContext.prototype.getParameter = new Proxy(WebGL2RenderingContext.prototype.getParameter, getParameterProxyHandler);
            }}
        }} catch (e) {{}}
        """
        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_scripts
        })
        
    def _inject_cursor_visualizer(self) -> None:
        """Inject a hardware-accelerated visual cursor tracker for debugging/demo."""
        cursor_js = """
        (function() {
            const ID = 'stealth-cursor-tracker';
            if (document.getElementById(ID)) return;
            
            const cursor = document.createElement('div');
            cursor.id = ID;
            Object.assign(cursor.style, {
                width: '20px',
                height: '20px',
                backgroundColor: 'rgba(255, 0, 0, 0.4)',
                border: '2px solid red',
                borderRadius: '50%',
                position: 'fixed',
                pointerEvents: 'none',
                zIndex: '999999',
                transition: 'transform 0.05s linear, background-color 0.1s',
                transform: 'translate3d(0, 0, 0)',
                left: '0',
                top: '0',
                willChange: 'transform'
            });
            
            const inject = () => {
                if (document.getElementById(ID)) return;
                (document.body || document.documentElement).appendChild(cursor);
            };

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', inject);
            } else {
                inject();
            }

            window.addEventListener('mousemove', (e) => {
                cursor.style.transform = `translate3d(${e.clientX - 10}px, ${e.clientY - 10}px, 0)`;
            }, { passive: true });

            window.addEventListener('mousedown', () => {
                cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.8)';
                cursor.style.transform += ' scale(0.8)';
            }, { passive: true });

            window.addEventListener('mouseup', () => {
                cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.4)';
            }, { passive: true });
        })();
        """
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
    
    def _enable_resource_blocking(self) -> None:
        """Enable CDP resource blocking for optimized performance."""
        blocked_patterns = [
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", 
            "*.css", 
            "*.woff", "*.woff2", "*.ttf", 
            "*.mp4", "*.webm", "*.mp3",
            "*.ico", "*.svg"
        ]
        
        try:
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd("Network.setBlockedURLs", {
                "urls": blocked_patterns
            })
        except: pass

    def navigate(self, url: str) -> None:
        """Navigate to a URL with human-like timing."""
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
            self.mouse.actions.reset_actions()
            self.mouse.actions.click_and_hold()
            self.mouse.actions.move_by_offset(random.randint(20, 100), random.randint(0, 10))
            self.mouse.actions.pause(random.uniform(0.5, 1.5))
            self.mouse.actions.release()
            self.mouse.actions.perform()
            
            # Pause to "read" selected text
            time.sleep(random.uniform(1.0, 3.0))
            
            # Click elsewhere to deselect
            self.mouse.move_to(
                random.randint(100, 500), 
                random.randint(100, 500), 
                click=True
            )
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
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
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
            random_pause_chance=0.0,
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
            min_typing_delay=0.05,
            max_typing_delay=0.15,
            typo_chance=0.005,
            min_action_pause=0.4,
            max_action_pause=1.2,
            hesitation_chance=0.01,
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


