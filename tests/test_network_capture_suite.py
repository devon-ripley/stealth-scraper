import pytest
import time
from stealth_scraper import create_stealth_browser, StealthLevel

@pytest.fixture
def browser():
    with create_stealth_browser(level=StealthLevel.FAST, headless=True) as b:
        yield b

def test_network_capture_metadata(browser):
    """Test that we can capture basic request/response metadata."""
    browser.network.start_capture()
    browser.navigate("https://httpbin.org/status/201")
    
    time.sleep(2)
    traffic = browser.network.get_traffic()
    assert len(traffic) > 0
    
    responses = [e for e in traffic if e["method"] == "Network.responseReceived"]
    target = next((r for r in responses if "status/201" in r["params"]["response"]["url"]), None)
    
    assert target is not None
    assert target["params"]["response"]["status"] == 201

def test_network_capture_body(browser):
    """Test that we can capture response bodies."""
    browser.network.start_capture(capture_body=True)
    browser.navigate("https://httpbin.org/json")
    
    event = browser.network.wait_for_request("httpbin.org/json", timeout=10)
    assert event is not None
    
    time.sleep(1)
    traffic = browser.network.get_traffic()
    response_event = next((e for e in traffic if e["method"] == "Network.responseReceived" and "httpbin.org/json" in e["params"]["response"]["url"]), None)
    
    assert response_event is not None
    req_id = response_event["params"]["requestId"]
    
    body = browser.network.get_response_body(req_id)
    assert body is not None
    assert "slideshow" in body

def test_wait_for_request_timeout(browser):
    browser.network.start_capture()
    start_time = time.time()
    event = browser.network.wait_for_request("non_existent_pattern", timeout=2.0)
    duration = time.time() - start_time
    assert event is None
    assert 2.0 <= duration <= 3.5

def test_capture_stop_and_clear(browser):
    browser.network.start_capture()
    browser.navigate("https://example.com")
    time.sleep(1)
    assert len(browser.network.get_traffic()) > 0
    browser.network.stop_capture()
    assert len(browser.network.get_traffic()) == 0
