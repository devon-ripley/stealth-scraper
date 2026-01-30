import time
import hashlib
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
    print("\n👻 Testing GHOST Mode (Should be random)...")
    hashes = []
    
    for i in range(2):
        print(f"  Run {i+1}...")
        try:
            browser = create_stealth_browser(
                level=StealthLevel.LOW, 
                identity=StealthIdentity.GHOST,
                headless=True
            )
            with browser:
                browser.navigate("https://www.google.com")
                fp_hash, fp_json = get_fingerprint_hash(browser)
                hashes.append(fp_hash)
                print(f"    Hash: {fp_hash}")
        except Exception as e:
            print(f"    Error: {e}")

    if hashes[0] != hashes[1]:
        print("✅ GHOST Mode Passed: Fingerprints are different.")
    else:
        print("❌ GHOST Mode Failed: Fingerprints are identical!")

def test_consistent_mode():
    print("\n🔒 Testing CONSISTENT Mode (Should be identical)...")
    seed = "my_stable_identity_seed_123"
    hashes = []
    
    for i in range(2):
        print(f"  Run {i+1}...")
        try:
            browser = create_stealth_browser(
                level=StealthLevel.LOW, 
                identity=StealthIdentity.CONSISTENT,
                identity_seed=seed,
                headless=True
            )
            with browser:
                browser.navigate("https://www.google.com")
                fp_hash, fp_json = get_fingerprint_hash(browser)
                hashes.append(fp_hash)
                print(f"    Hash: {fp_hash}")
        except Exception as e:
            print(f"    Error: {e}")

    if hashes[0] == hashes[1]:
        print("✅ CONSISTENT Mode Passed: Fingerprints are identical.")
    else:
        print("❌ CONSISTENT Mode Failed: Fingerprints are different!")

if __name__ == "__main__":
    test_ghost_mode()
    test_consistent_mode()
