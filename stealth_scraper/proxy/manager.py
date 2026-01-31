"""
Proxy manager for stealth-scraper.

Handles proxy lifecycle, rotation, extension management, and location sync.
"""

import time
from typing import Optional, Union, TYPE_CHECKING

from .config import Proxy, ProxyConfig, ProxyPool, RotationStrategy, ProxyInput
from .extension import ProxyExtensionGenerator
from .geo import get_location_for_country

if TYPE_CHECKING:
    from ..config import StealthLocation


class ProxyManager:
    """
    Manages proxy lifecycle including rotation and extension handling.

    Features:
        - Proxy pool management with multiple rotation strategies
        - Chrome extension creation/cleanup for authenticated proxies
        - Geo-location sync with proxy country
        - Request counting for timed rotation
    """

    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        Initialize the proxy manager.

        Args:
            config: ProxyConfig instance, or None to disable
        """
        self._config = config
        self._extension_generator = ProxyExtensionGenerator()
        self._current_extension_path: Optional[str] = None
        self._last_rotation_time: float = time.time()
        self._request_count: int = 0

    @classmethod
    def from_input(cls, proxy_input: ProxyInput) -> Optional["ProxyManager"]:
        """
        Create ProxyManager from various input types.

        Args:
            proxy_input: Can be:
                - None: No proxy
                - str: Proxy URL (e.g., "http://user:pass@host:8080")
                - Proxy: Single proxy instance
                - ProxyConfig: Full configuration

        Returns:
            ProxyManager instance or None if no proxy
        """
        if proxy_input is None:
            return None

        if isinstance(proxy_input, str):
            # Parse URL string
            config = ProxyConfig.from_url(proxy_input)
            return cls(config)

        if isinstance(proxy_input, Proxy):
            # Wrap single proxy in config
            config = ProxyConfig(enabled=True, proxy=proxy_input)
            return cls(config)

        if isinstance(proxy_input, ProxyConfig):
            if not proxy_input.enabled:
                return None
            return cls(proxy_input)

        raise TypeError(f"Unsupported proxy input type: {type(proxy_input)}")

    @property
    def enabled(self) -> bool:
        """Check if proxy is enabled."""
        return self._config is not None and self._config.enabled

    @property
    def config(self) -> Optional[ProxyConfig]:
        """Get the proxy configuration."""
        return self._config

    @property
    def current_proxy(self) -> Optional[Proxy]:
        """Get the currently active proxy."""
        if not self._config:
            return None
        return self._config.get_current_proxy()

    @property
    def extension_path(self) -> Optional[str]:
        """Get path to the current proxy extension."""
        return self._current_extension_path

    @property
    def sync_location(self) -> bool:
        """Check if location sync is enabled."""
        return self._config is not None and self._config.sync_location

    def get_synced_location(self) -> Optional["StealthLocation"]:
        """
        Get StealthLocation matching the current proxy's country.

        Returns:
            StealthLocation if proxy has country and sync is enabled, None otherwise
        """
        if not self.sync_location:
            return None

        proxy = self.current_proxy
        if not proxy or not proxy.country:
            return None

        return get_location_for_country(proxy.country)

    def create_extension(self) -> Optional[str]:
        """
        Create Chrome extension for the current proxy.

        Returns:
            Path to extension directory, or None if no auth needed
        """
        proxy = self.current_proxy
        if not proxy:
            return None

        # Only create extension if proxy requires auth
        if not proxy.requires_auth:
            # For non-auth proxies, we'll use Chrome's --proxy-server flag
            return None

        self._current_extension_path = self._extension_generator.create_extension(proxy)
        return self._current_extension_path

    def get_chrome_options_args(self) -> list:
        """
        Get Chrome command-line arguments for proxy.

        Returns:
            List of arguments to add to Chrome options
        """
        args = []
        proxy = self.current_proxy

        if not proxy:
            return args

        if proxy.requires_auth:
            # Auth proxies use extension
            if self._current_extension_path:
                args.append(f"--load-extension={self._current_extension_path}")
        else:
            # Non-auth proxies use --proxy-server
            args.append(f"--proxy-server={proxy.url_no_auth}")

        return args

    def should_rotate(self) -> bool:
        """
        Check if proxy should be rotated based on strategy.

        Returns:
            True if rotation should occur
        """
        if not self._config:
            return False

        strategy = self._config.rotation_strategy

        if strategy == RotationStrategy.NONE:
            return False

        if strategy == RotationStrategy.PER_SESSION:
            # Per-session rotation is handled at browser creation
            return False

        if strategy == RotationStrategy.TIMED:
            elapsed = time.time() - self._last_rotation_time
            return elapsed >= self._config.rotation_interval_seconds

        if strategy == RotationStrategy.ON_ERROR:
            # Caller should invoke rotate_on_error() explicitly
            return False

        return False

    def rotate(self) -> Optional[Proxy]:
        """
        Rotate to the next proxy.

        Returns:
            The new current proxy, or None
        """
        if not self._config:
            return None

        # Clean up old extension
        if self._current_extension_path:
            self._extension_generator.cleanup()
            self._current_extension_path = None

        # Rotate the proxy
        new_proxy = self._config.rotate()
        self._last_rotation_time = time.time()

        return new_proxy

    def rotate_on_error(self) -> Optional[Proxy]:
        """
        Rotate proxy due to an error.

        Use this when a request fails and ON_ERROR strategy is configured.

        Returns:
            The new current proxy, or None
        """
        if not self._config:
            return None

        if self._config.rotation_strategy != RotationStrategy.ON_ERROR:
            return self.current_proxy

        return self.rotate()

    def report_failure(self) -> Optional[Proxy]:
        """Alias for rotate_on_error."""
        return self.rotate_on_error()

    def increment_request_count(self) -> None:
        """Increment the request counter (for timed rotation tracking)."""
        self._request_count += 1

    def check_and_rotate(self) -> bool:
        """
        Check rotation conditions and rotate if needed.

        Returns:
            True if rotation occurred
        """
        if self.should_rotate():
            self.rotate()
            return True
        return False

    def cleanup(self) -> None:
        """Clean up resources (extension temp files)."""
        self._extension_generator.cleanup()
        self._current_extension_path = None

    def __repr__(self) -> str:
        proxy = self.current_proxy
        if proxy:
            return f"ProxyManager(proxy={proxy}, sync_location={self.sync_location})"
        return "ProxyManager(disabled)"

    def __del__(self):
        self.cleanup()
