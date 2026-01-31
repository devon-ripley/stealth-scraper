"""
Examples demonstrating how to capture and inspect network traffic.
"""

import time
import json
from stealth_scraper import create_stealth_browser, StealthLevel

def example_capture_basic_traffic():
    """Demonstrates basic network traffic capturing."""
    print("\n=== BASIC NETWORK TRAFFIC CAPTURE ===")
    print("Capturing all request and response metadata...\n")

    with create_stealth_browser(level=StealthLevel.FAST) as browser:
        # Start the network capture
        browser.network.start_capture()

        # Navigate to a site
        print("Navigating to example.com...")
        browser.navigate("https://example.com")
        
        # Buffer timing for async requests
        time.sleep(2)

        # Retrieve traffic logs
        traffic = browser.network.get_traffic()
        print(f"Captured {len(traffic)} network events.")

        # Print the first few requests
        requests = [e for e in traffic if e["method"] == "Network.requestWillBeSent"]
        for req in requests[:5]:
            print(f" -> Request focus: {req['params']['request']['url'][:80]}...")


def example_capture_response_bodies():
    """Demonstrates capturing and reading full response bodies."""
    print("\n=== CAPTURING RESPONSE BODIES ===")
    print("Using CDP to retrieve raw response payloads (JSON)...\n")

    with create_stealth_browser(level=StealthLevel.FAST) as browser:
        # Enable capture with body buffering
        browser.network.start_capture(capture_body=True)

        url = "https://httpbin.org/json"
        print(f"Navigating to {url}...")
        browser.navigate(url)
        time.sleep(2)

        traffic = browser.network.get_traffic()
        
        for event in traffic:
            if event["method"] == "Network.responseReceived":
                resp_url = event["params"]["response"]["url"]
                
                # Check if this is our target JSON request
                if "httpbin.org/json" in resp_url:
                    print(f"Found target URL: {resp_url}")
                    req_id = event["params"]["requestId"]
                    
                    # Fetch the actual body
                    body = browser.network.get_response_body(req_id)
                    if body:
                        print(f"Successfully captured body ({len(body)} bytes)")
                        try:
                            # Parse JSON if applicable
                            data = json.loads(body)
                            print(f"Data summary: {list(data.keys())}")
                        except json.JSONDecodeError:
                            print(f"Snippet: {body[:100]}...")


def example_wait_for_specific_request():
    """Demonstrates waiting for a specific request pattern to appear."""
    print("\n=== WAITING FOR SPECIFIC REQUESTS ===")
    print("Handy for Single Page Apps (SPAs) and dynamic loading...\n")

    with create_stealth_browser(level=StealthLevel.FAST) as browser:
        browser.network.start_capture()
        
        print("Navigating to site and waiting for async data...")
        browser.navigate("https://httpbin.org/get?q=stealth")
        
        # Block until a matching request is seen (or timeout)
        match = browser.network.wait_for_request("httpbin.org/get", timeout=10)
        
        if match:
            url = match["params"]["request"]["url"]
            print(f"✅ Caught request: {url}")
        else:
            print("❌ Timeout reached without seeing matching request")


if __name__ == "__main__":
    try:
        example_capture_basic_traffic()
        example_capture_response_bodies()
        example_wait_for_specific_request()
    except Exception as e:
        print(f"An error occurred: {e}")
