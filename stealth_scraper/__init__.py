"""
Ultimate Stealth Web Scraper Package
Undetectable web scraping with human-like behavior simulation.
"""

from .stealth_scraper import (
    StealthBrowser,
    HumanBehaviorConfig,
    StealthConfig,
    StealthLevel,
    CustomStealthLevel,
    StealthIdentity,
    StealthLocation,
    HumanMouseSimulator,
    HumanScrollSimulator,
    HumanTypingSimulator,
    BezierCurve,
    create_stealth_browser,
    get_stealth_config,
    create_browser_with_level,
)

__version__ = "1.2.0"
__all__ = [
    "StealthBrowser",
    "HumanBehaviorConfig",
    "StealthConfig",
    "StealthLevel",
    "CustomStealthLevel",
    "StealthIdentity",
    "StealthLocation",
    "HumanMouseSimulator",
    "HumanScrollSimulator",
    "HumanTypingSimulator",
    "BezierCurve",
    "create_stealth_browser",
    "get_stealth_config",
    "create_browser_with_level",
]
