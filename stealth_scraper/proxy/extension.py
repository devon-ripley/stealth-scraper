"""
Chrome extension generator for proxy authentication.

Creates a temporary Manifest V3 Chrome extension that handles proxy
authentication natively, avoiding detection patterns from selenium-wire.
"""

import os
import json
import tempfile
import shutil
from typing import Optional

from .config import Proxy, ProxyType


class ProxyExtensionGenerator:
    """
    Generates a Chrome extension for proxy authentication.

    The extension uses Chrome's native proxy API with webRequest for auth,
    which is less detectable than network interception approaches.
    """

    def __init__(self):
        self._temp_dirs: list = []

    def create_extension(self, proxy: Proxy) -> str:
        """
        Create a Chrome extension for the given proxy.

        Args:
            proxy: The proxy configuration

        Returns:
            Path to the extension directory (load via --load-extension)
        """
        # Create temp directory for extension
        ext_dir = tempfile.mkdtemp(prefix="stealth_proxy_ext_")
        self._temp_dirs.append(ext_dir)

        # Generate manifest.json
        manifest = self._generate_manifest(proxy)
        manifest_path = os.path.join(ext_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Generate background.js (service worker for MV3)
        background_js = self._generate_background_script(proxy)
        background_path = os.path.join(ext_dir, "background.js")
        with open(background_path, "w", encoding="utf-8") as f:
            f.write(background_js)

        return ext_dir

    def _generate_manifest(self, proxy: Proxy) -> dict:
        """Generate Manifest V3 manifest.json."""
        manifest = {
            "manifest_version": 3,
            "name": "Stealth Proxy Helper",
            "version": "1.0",
            "description": "Proxy configuration helper",
            "permissions": [
                "proxy",
                "webRequest",
                "webRequestAuthProvider",
            ],
            "host_permissions": [
                "<all_urls>"
            ],
            "background": {
                "service_worker": "background.js"
            },
        }

        return manifest

    def _generate_background_script(self, proxy: Proxy) -> str:
        """Generate background.js service worker."""
        # Determine proxy scheme for PAC
        if proxy.proxy_type == ProxyType.SOCKS5:
            pac_type = "SOCKS5"
        elif proxy.proxy_type == ProxyType.HTTPS:
            pac_type = "HTTPS"
        else:
            pac_type = "PROXY"

        # Build the background script
        script = f'''
// Stealth Proxy Extension - Background Service Worker

const PROXY_CONFIG = {{
    host: "{proxy.host}",
    port: {proxy.port},
    type: "{pac_type}",
    username: {json.dumps(proxy.username)},
    password: {json.dumps(proxy.password)},
}};

// Configure proxy settings
const config = {{
    mode: "fixed_servers",
    rules: {{
        singleProxy: {{
            scheme: "{proxy.proxy_type.value}",
            host: PROXY_CONFIG.host,
            port: PROXY_CONFIG.port,
        }},
        bypassList: ["localhost", "127.0.0.1"],
    }},
}};

// Set proxy configuration
chrome.proxy.settings.set(
    {{ value: config, scope: "regular" }},
    function() {{
        if (chrome.runtime.lastError) {{
            console.error("Proxy config error:", chrome.runtime.lastError);
        }}
    }}
);

// Handle proxy authentication
if (PROXY_CONFIG.username && PROXY_CONFIG.password) {{
    chrome.webRequest.onAuthRequired.addListener(
        function(details, callbackFn) {{
            // Only respond to proxy auth challenges
            if (details.isProxy) {{
                callbackFn({{
                    authCredentials: {{
                        username: PROXY_CONFIG.username,
                        password: PROXY_CONFIG.password,
                    }}
                }});
            }} else {{
                callbackFn();
            }}
        }},
        {{ urls: ["<all_urls>"] }},
        ["asyncBlocking"]
    );
}}

console.log("Stealth Proxy Extension loaded:", PROXY_CONFIG.host + ":" + PROXY_CONFIG.port);
'''
        return script.strip()

    def cleanup(self) -> None:
        """Remove all temporary extension directories."""
        for temp_dir in self._temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception:
                pass
        self._temp_dirs.clear()

    def __del__(self):
        self.cleanup()


# Alternative: PAC script approach for simpler proxies without auth
def generate_pac_script(proxy: Proxy) -> str:
    """
    Generate a PAC (Proxy Auto-Config) script.

    Note: PAC scripts don't support authentication directly.
    Use the extension approach for authenticated proxies.
    """
    if proxy.proxy_type == ProxyType.SOCKS5:
        pac_type = "SOCKS5"
    else:
        pac_type = "PROXY"

    return f'''
function FindProxyForURL(url, host) {{
    // Bypass localhost
    if (host === "localhost" || host === "127.0.0.1") {{
        return "DIRECT";
    }}
    return "{pac_type} {proxy.host}:{proxy.port}";
}}
'''.strip()
