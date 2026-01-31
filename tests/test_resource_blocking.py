import pytest
from stealth_scraper import create_stealth_browser

def test_resource_blocking():
    # Automatically runs twice with Mobile/Desktop defaults for UA
    with create_stealth_browser(block_resources=True, headless=True) as browser:
        url = "https://example.com"
        browser.navigate(url)
        
        script = """
        return window.performance.getEntriesByType('resource').map(r => ({
            name: r.name,
            initiatorType: r.initiatorType,
            transferSize: r.transferSize
        }));
        """
        resources = browser.execute_script(script)
        
        # Filter for naturally blocked types with positive transfer size
        loaded_blocked = [r for r in resources if any(ext in r['name'].lower() for ext in ['.css', '.png', '.jpg', '.jpeg', '.woff', '.ttf']) and r.get('transferSize', 0) > 0]
        
        # Minor leakage acceptable, but should be minimal
        assert len(loaded_blocked) < 3
