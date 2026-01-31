import hashlib
import pytest
from stealth_scraper import create_stealth_browser, StealthIdentity, StealthLevel

def get_fingerprint_hash(browser):
    """Extract a simple hash of the browser fingerprint."""
    script = """
    return JSON.stringify({
        concurrency: navigator.hardwareConcurrency,
        memory: navigator.deviceMemory,
        webgl_vendor: document.createElement('canvas').getContext('webgl').getParameter(37445),
        canvas_noise: document.createElement('canvas').getContext('2d').shadowBlur
    });
    """
    fp_json = browser.driver.execute_script(script)
    return hashlib.md5(fp_json.encode()).hexdigest(), fp_json

def test_ghost_mode():
    hashes = []
    # Runs twice automatically with Mobile/Desktop defaults for UA
    for i in range(2):
        browser = create_stealth_browser(level=StealthLevel.LOW, identity=StealthIdentity.GHOST, headless=True)
        with browser:
            browser.navigate("https://example.com")
            fp_hash, _ = get_fingerprint_hash(browser)
            hashes.append(fp_hash)
    
    assert hashes[0] != hashes[1]

def test_consistent_mode():
    seed = "my_stable_identity_seed_123"
    hashes = []
    for i in range(2):
        browser = create_stealth_browser(level=StealthLevel.LOW, identity=StealthIdentity.CONSISTENT, identity_seed=seed, headless=True)
        with browser:
            browser.navigate("https://example.com")
            fp_hash, _ = get_fingerprint_hash(browser)
            hashes.append(fp_hash)

    assert hashes[0] == hashes[1]
