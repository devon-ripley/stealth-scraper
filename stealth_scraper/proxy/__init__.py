"""
Proxy module for stealth-scraper.

Provides comprehensive proxy support with rotation and geo-location sync
for enhanced bot detection avoidance using Chrome extension approach.
"""

from .config import (
    Proxy,
    ProxyConfig,
    ProxyPool,
    ProxyType,
    RotationStrategy,
)
from .extension import ProxyExtensionGenerator
from .manager import ProxyManager
from .geo import get_location_for_country, COUNTRY_LOCATIONS

__all__ = [
    # Config classes
    "Proxy",
    "ProxyConfig",
    "ProxyPool",
    "ProxyType",
    "RotationStrategy",
    # Extension
    "ProxyExtensionGenerator",
    # Manager
    "ProxyManager",
    # Geo
    "get_location_for_country",
    "COUNTRY_LOCATIONS",
]
