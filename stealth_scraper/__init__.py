"""
Ultimate Stealth Web Scraper Package
Undetectable web scraping with human-like behavior simulation.
"""

from .stealth_scraper import (
    StealthBrowser,
    HumanBehaviorConfig,
    StealthConfig,
    ProxyConfig,
    HumanMouseSimulator,
    HumanScrollSimulator,
    HumanTypingSimulator,
    BezierCurve,
    create_stealth_browser,
)

__version__ = "1.0.0"
__all__ = [
    "StealthBrowser",
    "HumanBehaviorConfig",
    "StealthConfig",
    "ProxyConfig",
    "HumanMouseSimulator",
    "HumanScrollSimulator",
    "HumanTypingSimulator",
    "BezierCurve",
    "create_stealth_browser",
]
