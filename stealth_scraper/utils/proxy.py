
import os
import zipfile
import tempfile
from typing import Optional
from ..config import ProxyConfig

class ProxyExtensionGenerator:
    """Generates a temporary Chrome extension to handle proxy authentication."""
    
    @staticmethod
    def generate(proxy_config: ProxyConfig) -> str:
        """
        Creates a zip file containing a Chrome extension that authenticates the proxy.
        Returns the path to the generated zip file.
        """
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Stealth Proxy Auth",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }
        """

        background_js = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "{proxy_config.protocol}",
                    host: "{proxy_config.host}",
                    port: parseInt({proxy_config.port})
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_config.username}",
                    password: "{proxy_config.password}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """

        # Create a temporary file for the extension
        t = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        extension_path = t.name
        t.close()

        with zipfile.ZipFile(extension_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return extension_path
