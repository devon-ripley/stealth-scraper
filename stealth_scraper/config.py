from typing import List, Tuple, Optional, Any, Dict, Union
from dataclasses import dataclass, field
from enum import Enum

class StealthLevel(Enum):
    """Preset stealth levels for easy configuration."""
    LOW = "low"          # Fast, minimal stealth - basic anti-detection only
    MEDIUM = "medium"    # Balanced - good stealth with reasonable speed
    HIGH = "high"        # Maximum stealth - slower but most human-like
    PARANOID = "paranoid"  # Alias for HIGH
    FAST = "fast"        # Instant interactions, minimal stealth (API compatible)


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


@dataclass
class ProxyConfig:
    """Proxy configuration (deprecated)."""
    enabled: bool = False
