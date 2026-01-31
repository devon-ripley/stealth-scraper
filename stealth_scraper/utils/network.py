
import json
import time
from typing import List, Dict, Any, Optional, Callable
from threading import Lock

class NetworkManager:
    """
    Manages network traffic capture using Chrome DevTools Protocol (CDP).
    Uses un-detected-chromedriver's native listener support if available, 
    falling back to performance logs for standard selenium.
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.is_capturing = False
        self._events: List[Dict[str, Any]] = []
        self._lock = Lock()
        self._use_listeners = hasattr(driver, 'add_cdp_listener')
        
    def _on_request_will_be_sent(self, event):
        with self._lock:
            if self.is_capturing:
                # UC passes the full event message or just params depending on version/config
                # If it's the full message, it has 'method' and 'params'
                if isinstance(event, dict) and "method" in event and "params" in event:
                    method = event["method"]
                    params = event["params"]
                else:
                    method = "Network.requestWillBeSent"
                    params = event

                self._events.append({
                    "method": method,
                    "params": params,
                    "timestamp": time.time()
                })

    def _on_response_received(self, event):
        with self._lock:
            if self.is_capturing:
                if isinstance(event, dict) and "method" in event and "params" in event:
                    method = event["method"]
                    params = event["params"]
                else:
                    method = "Network.responseReceived"
                    params = event

                self._events.append({
                    "method": method,
                    "params": params,
                    "timestamp": time.time()
                })

    def start_capture(self, capture_body: bool = False, max_body_size: int = 1024 * 1024):
        """
        Start capturing network traffic.
        """
        if self.is_capturing:
            return

        with self._lock:
            self._events = []
            self.is_capturing = True

        try:
            # Enable Network domain
            self.driver.execute_cdp_cmd("Network.enable", {
                "maxPostDataSize": max_body_size,
                "maxResourceBufferSize": max_body_size,
                "maxTotalBufferSize": max_body_size * 10
            })
            
            # Subscribe to listeners if using UC
            if self._use_listeners:
                self.driver.add_cdp_listener("Network.requestWillBeSent", self._on_request_will_be_sent)
                self.driver.add_cdp_listener("Network.responseReceived", self._on_response_received)
                # self.driver.add_cdp_listener("Network.loadingFinished", ...)
            
        except Exception as e:
            print(f"Warning: Failed to enable Network domain: {e}")

    def stop_capture(self):
        """Stop capturing network traffic and clear buffers."""
        if not self.is_capturing:
            return
            
        self.is_capturing = False
        with self._lock:
            self._events = []
            
        try:
            self.driver.execute_cdp_cmd("Network.disable", {})
        except Exception:
            pass

    def get_traffic(self) -> List[Dict[str, Any]]:
        """
        Retrieve captured network events.
        """
        if self._use_listeners:
            with self._lock:
                return list(self._events)
        
        # Fallback to Performance Logs (Standard Selenium)
        traffic_events = []
        try:
            logs = self.driver.get_log("performance")
            for entry in logs:
                try:
                    message = json.loads(entry["message"])["message"]
                    method = message.get("method")
                    params = message.get("params", {})
                    
                    if method in ["Network.requestWillBeSent", "Network.responseReceived"]:
                        traffic_events.append({
                            "method": method,
                            "params": params,
                            "timestamp": entry["timestamp"]
                        })
                except (KeyError, json.JSONDecodeError):
                    continue
        except Exception as e:
            pass # Logs might be empty or not supported
            
        return traffic_events

    def get_response_body(self, request_id: str) -> Optional[str]:
        """
        Fetch the response body for a specific request ID.
        """
        try:
            result = self.driver.execute_cdp_cmd("Network.getResponseBody", {
                "requestId": request_id
            })
            return result.get("body")
        except Exception:
            return None
            
    def wait_for_request(self, 
                        url_pattern: str, 
                        timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """
        Block and wait for a request matching a pattern.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            events = self.get_traffic()
            for event in events:
                if event["method"] == "Network.requestWillBeSent":
                    # Structure differs slightly between log and listener?
                    # Listener params IS the event params.
                    # Log message['params'] IS the event params.
                    # So structure should be consistent.
                    req = event["params"].get("request", {})
                    url = req.get("url", "")
                    if url_pattern in url:
                        return event
            time.sleep(0.1)
        return None
