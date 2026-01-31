import pytest
import time
from stealth_scraper import Proxy, ProxyConfig, ProxyPool, RotationStrategy, ProxyManager

def test_proxy_parsing():
    p1 = Proxy.from_url("http://user:pass@1.2.3.4:8080")
    assert p1.host == "1.2.3.4"
    assert p1.username == "user"
    assert p1.password == "pass"

def test_rotation_logical_per_session():
    pool = ProxyPool([
        Proxy(host="1.1.1.1", port=80),
        Proxy(host="2.2.2.2", port=80),
        Proxy(host="3.3.3.3", port=80)
    ])
    config = ProxyConfig(proxy_pool=pool, rotation_strategy=RotationStrategy.PER_SESSION)
    manager = ProxyManager(config)
    assert manager.current_proxy.host == "1.1.1.1"
    manager.rotate()
    assert manager.current_proxy.host == "2.2.2.2"

def test_timed_rotation():
    pool = ProxyPool([Proxy(host="1.1.1.1", port=80), Proxy(host="2.2.2.2", port=80)])
    config = ProxyConfig(proxy_pool=pool, rotation_strategy=RotationStrategy.TIMED, rotation_interval_seconds=1)
    manager = ProxyManager(config)
    time.sleep(1.1)
    assert manager.should_rotate() is True
    manager.check_and_rotate()
    assert manager.current_proxy.host == "2.2.2.2"
