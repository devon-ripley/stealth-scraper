"""
Ultimate Stealth Web Scraper
Designed to be undetectable by bot detection systems.
"""

from .config import (
    StealthLevel,
    CustomStealthLevel,
    StealthIdentity,
    StealthLocation,
    StealthConfig,
    HumanBehaviorConfig,
)
from .browser import (
    StealthBrowser,
    create_stealth_browser,
    create_browser_with_level,
    get_stealth_config,
)
from .proxy import (
    Proxy,
    ProxyConfig,
    ProxyPool,
    ProxyType,
    RotationStrategy,
    ProxyManager,
    get_location_for_country,
)

__version__ = "1.4.0"
