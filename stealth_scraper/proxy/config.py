"""
Proxy configuration classes for stealth-scraper.
"""

from typing import List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ProxyType(Enum):
    """Supported proxy types."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class RotationStrategy(Enum):
    """Proxy rotation strategies."""
    NONE = "none"                # Use single proxy, no rotation
    PER_SESSION = "per_session"  # New proxy for each browser session
    TIMED = "timed"              # Rotate after time interval
    ON_ERROR = "on_error"        # Rotate when proxy fails


@dataclass
class Proxy:
    """Single proxy definition."""

    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None  # ISO 3166-1 alpha-2 (e.g., "US", "GB")
    city: Optional[str] = None
    provider: Optional[str] = None  # e.g., "dataimpulse", "brightdata"

    @property
    def requires_auth(self) -> bool:
        """Check if proxy requires authentication."""
        return self.username is not None and self.password is not None

    @property
    def url(self) -> str:
        """Build proxy URL."""
        scheme = self.proxy_type.value
        if self.requires_auth:
            return f"{scheme}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{scheme}://{self.host}:{self.port}"

    @property
    def url_no_auth(self) -> str:
        """Build proxy URL without credentials (for logging)."""
        scheme = self.proxy_type.value
        return f"{scheme}://{self.host}:{self.port}"

    @classmethod
    def from_url(cls, url: str, country: Optional[str] = None) -> "Proxy":
        """
        Parse a proxy from URL string.

        Formats:
            - http://host:port
            - http://user:pass@host:port
            - socks5://user:pass@host:port
        """
        import re

        # Match: scheme://[user:pass@]host:port
        pattern = r'^(https?|socks5)://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)$'
        match = re.match(pattern, url)

        if not match:
            raise ValueError(f"Invalid proxy URL format: {url}")

        scheme, username, password, host, port = match.groups()

        proxy_type_map = {
            "http": ProxyType.HTTP,
            "https": ProxyType.HTTPS,
            "socks5": ProxyType.SOCKS5,
        }

        return cls(
            host=host,
            port=int(port),
            proxy_type=proxy_type_map[scheme],
            username=username,
            password=password,
            country=country,
        )

    def __repr__(self) -> str:
        auth = " (auth)" if self.requires_auth else ""
        geo = f" [{self.country}]" if self.country else ""
        return f"Proxy({self.proxy_type.value}://{self.host}:{self.port}{auth}{geo})"


@dataclass
class ProxyPool:
    """Pool of proxies for rotation."""

    proxies: List[Proxy] = field(default_factory=list)
    _current_index: int = field(default=0, repr=False)

    def add(self, proxy: Proxy) -> None:
        """Add a proxy to the pool."""
        self.proxies.append(proxy)

    def get_current(self) -> Optional[Proxy]:
        """Get the current proxy."""
        if not self.proxies:
            return None
        return self.proxies[self._current_index % len(self.proxies)]

    def rotate(self) -> Optional[Proxy]:
        """Rotate to the next proxy and return it."""
        if not self.proxies:
            return None
        self._current_index = (self._current_index + 1) % len(self.proxies)
        return self.get_current()

    def reset(self) -> None:
        """Reset rotation to first proxy."""
        self._current_index = 0

    def __len__(self) -> int:
        return len(self.proxies)

    def __iter__(self):
        return iter(self.proxies)


@dataclass
class ProxyConfig:
    """
    Full proxy configuration.

    Usage:
        # Single proxy
        config = ProxyConfig(enabled=True, proxy=Proxy(...))

        # Proxy pool with rotation
        config = ProxyConfig(
            enabled=True,
            proxy_pool=ProxyPool([Proxy(...), Proxy(...)]),
            rotation_strategy=RotationStrategy.PER_SESSION
        )
    """

    enabled: bool = True

    # Single proxy OR pool (mutually exclusive in practice)
    proxy: Optional[Proxy] = None
    proxy_pool: Optional[ProxyPool] = None

    # Rotation settings
    rotation_strategy: RotationStrategy = RotationStrategy.NONE
    rotation_interval_seconds: int = 300  # For TIMED rotation

    # Geo-location sync
    sync_location: bool = False  # Match timezone/locale to proxy country

    def get_current_proxy(self) -> Optional[Proxy]:
        """Get the current active proxy."""
        if not self.enabled:
            return None
        if self.proxy_pool and len(self.proxy_pool) > 0:
            return self.proxy_pool.get_current()
        return self.proxy

    def rotate(self) -> Optional[Proxy]:
        """Rotate to next proxy (if using pool)."""
        if self.proxy_pool:
            return self.proxy_pool.rotate()
        return self.proxy

    @classmethod
    def from_url(cls, url: str, **kwargs) -> "ProxyConfig":
        """Create config from a proxy URL string."""
        proxy = Proxy.from_url(url)
        return cls(enabled=True, proxy=proxy, **kwargs)

    def __post_init__(self):
        # Validate configuration
        if self.enabled and not self.proxy and not self.proxy_pool:
            raise ValueError("ProxyConfig enabled but no proxy or proxy_pool provided")

        if self.proxy and self.proxy_pool:
            # Both provided - prefer pool
            self.proxy = None


# Type alias for convenience
ProxyInput = Union[str, Proxy, ProxyConfig, None]
