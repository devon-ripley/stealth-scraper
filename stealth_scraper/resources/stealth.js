const STEALTH_CONFIG = "__STEALTH_CONFIG__";

(function () {
    const newProto = Object.getPrototypeOf(navigator);
    if (Object.getOwnPropertyDescriptor(newProto, 'webdriver')) {
        delete newProto.webdriver;
    }
    Object.defineProperty(newProto, 'webdriver', {
        get: () => false,
        enumerable: true,
        configurable: true
    });

    if (Object.getOwnPropertyDescriptor(navigator, 'webdriver')) {
        delete navigator.webdriver;
    }
})();

// ========================================
// CHROME RUNTIME MASKING
// ========================================

window.chrome = {
    runtime: {
        connect: function () { },
        sendMessage: function () { },
        onMessage: {
            addListener: function () { },
            removeListener: function () { }
        }
    },
    loadTimes: function () {
        return {
            commitLoadTime: Date.now() / 1000 - Math.random() * 5,
            connectionInfo: "h2",
            finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 2,
            finishLoadTime: Date.now() / 1000 - Math.random(),
            firstPaintAfterLoadTime: 0,
            firstPaintTime: Date.now() / 1000 - Math.random() * 3,
            navigationType: "Other",
            npnNegotiatedProtocol: "h2",
            requestTime: Date.now() / 1000 - Math.random() * 6,
            startLoadTime: Date.now() / 1000 - Math.random() * 5,
            wasAlternateProtocolAvailable: false,
            wasFetchedViaSpdy: true,
            wasNpnNegotiated: true
        };
    },
    csi: function () {
        return {
            onloadT: Date.now(),
            pageT: Math.random() * 1000 + 500,
            startE: Date.now() - Math.random() * 5000,
            tran: 15
        };
    },
    app: {
        isInstalled: false,
        InstallState: {
            DISABLED: "disabled",
            INSTALLED: "installed",
            NOT_INSTALLED: "not_installed"
        },
        RunningState: {
            CANNOT_RUN: "cannot_run",
            READY_TO_RUN: "ready_to_run",
            RUNNING: "running"
        }
    }
};

// ========================================
// PERMISSIONS API MASKING
// ========================================

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => {
    // Pass through to native to avoid detection of the shim itself
    // unless we strictly need to hide a denied state.
    // Since we cleared flags, 'prompt' should be default.
    return originalQuery(parameters);
};

// ========================================
// PLUGINS MASKING
// ========================================

const makePluginArray = () => {
    const plugins = STEALTH_CONFIG.is_mobile ? [] : [
        { name: "Chrome PDF Plugin", filename: "internal-pdf-viewer", description: "Portable Document Format" },
        { name: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", description: "" },
        { name: "Native Client", filename: "internal-nacl-plugin", description: "" }
    ];

    // Generic PluginArray shim using Array base (closest authentic behavior)
    const pluginArray = plugins.map(p => {
        const plugin = Object.create(Plugin.prototype);
        Object.defineProperties(plugin, {
            name: { value: p.name, writable: false, enumerable: false },
            filename: { value: p.filename, writable: false, enumerable: false },
            description: { value: p.description, writable: false, enumerable: false },
            length: { value: 1, writable: false, enumerable: false },
        });
        Object.defineProperty(plugin, Symbol.toStringTag, { value: 'Plugin', writable: false, enumerable: false, configurable: true });
        return plugin;
    });

    // Magic: Make the array look like a PluginArray
    Object.setPrototypeOf(pluginArray, PluginArray.prototype);

    // Add named access
    plugins.forEach((p, i) => {
        Object.defineProperty(pluginArray, p.name, { value: pluginArray[i], writable: false, enumerable: false });
    });

    // Add required methods
    Object.defineProperties(pluginArray, {
        item: { value: (i) => pluginArray[i] || null, writable: false, enumerable: false },
        namedItem: { value: (name) => pluginArray.find(p => p.name === name) || null, writable: false, enumerable: false },
        refresh: { value: () => { }, writable: false, enumerable: false }
    });

    Object.defineProperty(pluginArray, Symbol.toStringTag, { value: 'PluginArray', writable: false, enumerable: false, configurable: true });

    return pluginArray;
};

const makeMimeTypeArray = () => {
    const mimes = STEALTH_CONFIG.is_mobile ? [] : [
        { type: "application/pdf", suffixes: "pdf", description: "", snippets: ["pdf"] }
    ];

    const mimeArray = mimes.map(m => {
        const mime = Object.create(MimeType.prototype);
        Object.defineProperties(mime, {
            type: { value: m.type, writable: false, enumerable: false },
            suffixes: { value: m.suffixes, writable: false, enumerable: false },
            description: { value: m.description, writable: false, enumerable: false },
            enabledPlugin: { value: null, writable: false, enumerable: false }
        });
        Object.defineProperty(mime, Symbol.toStringTag, { value: 'MimeType', writable: false, enumerable: false, configurable: true });
        return mime;
    });

    Object.setPrototypeOf(mimeArray, MimeTypeArray.prototype);

    mimes.forEach((m, i) => {
        Object.defineProperty(mimeArray, m.type, { value: mimeArray[i], writable: false, enumerable: false });
    });

    Object.defineProperties(mimeArray, {
        item: { value: (i) => mimeArray[i] || null, writable: false, enumerable: false },
        namedItem: { value: (name) => mimeArray.find(m => m.type === name) || null, writable: false, enumerable: false }
    });

    Object.defineProperty(mimeArray, Symbol.toStringTag, { value: 'MimeTypeArray', writable: false, enumerable: false, configurable: true });

    return mimeArray;
};

(function () {
    if (!STEALTH_CONFIG.mask_plugins) return;
    const newProto = Object.getPrototypeOf(navigator);
    if (Object.getOwnPropertyDescriptor(newProto, 'plugins')) {
        delete newProto.plugins;
    }
    Object.defineProperty(newProto, 'plugins', {
        get: () => makePluginArray(),
        enumerable: true,
        configurable: true
    });

    if (Object.getOwnPropertyDescriptor(navigator, 'plugins')) {
        delete navigator.plugins;
    }
})();

(function () {
    if (!STEALTH_CONFIG.mask_plugins) return;
    const newProto = Object.getPrototypeOf(navigator);
    if (Object.getOwnPropertyDescriptor(newProto, 'mimeTypes')) {
        delete newProto.mimeTypes;
    }
    Object.defineProperty(newProto, 'mimeTypes', {
        get: () => makeMimeTypeArray(),
        enumerable: true,
        configurable: true
    });

    if (Object.getOwnPropertyDescriptor(navigator, 'mimeTypes')) {
        delete navigator.mimeTypes;
    }
})();

// ========================================
// IDENTITY MASKING (MODULAR)
// ========================================

Object.defineProperty(navigator, 'hardwareConcurrency', {
    get: () => STEALTH_CONFIG.hardware_concurrency,
    configurable: true
});

Object.defineProperty(navigator, 'deviceMemory', {
    get: () => STEALTH_CONFIG.device_memory,
    configurable: true
});

Object.defineProperty(navigator, 'platform', {
    get: () => STEALTH_CONFIG.is_mobile ? 'Linux armv8l' : 'Win32',
    configurable: true
});

Object.defineProperty(navigator, 'vendor', {
    get: () => 'Google Inc.',
    configurable: true
});

Object.defineProperty(navigator, 'maxTouchPoints', {
    get: () => STEALTH_CONFIG.is_mobile ? 5 : 0,
    configurable: true
});

// ========================================
// CANVAS FINGERPRINTING PROTECTION
// ========================================

const originalGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function (type, attributes) {
    const context = originalGetContext.call(this, type, attributes);
    if (type === '2d' && context) {
        // Apply entropy immediately from Config (controlled by Python seed)
        // Use 0.001 as minimum to avoid clamping if config is missing
        context.shadowBlur = (STEALTH_CONFIG.canvas_noise || 0.001);

        const originalFillText = context.fillText.bind(context);
        context.fillText = function (...args) {
            // For fillText, we can slightly jitter it if desired, but for consistency mode we must be careful.
            // Safest to keep it stable or use a deterministic modifier.
            // Ideally, text rendering is noisy enough due to shadowBlur having a value.
            return originalFillText(...args);
        };
    }
    return context;
};

// ========================================
// WEBGL FINGERPRINTING PROTECTION
// ========================================

const getParameterProxyHandler = {
    apply: function (target, thisArg, argumentsList) {
        const param = argumentsList[0];
        if (param === 37445) return STEALTH_CONFIG.webgl_vendor;
        if (param === 37446) return STEALTH_CONFIG.webgl_renderer;
        return Reflect.apply(target, thisArg, argumentsList);
    }
};

try {
    WebGLRenderingContext.prototype.getParameter = new Proxy(WebGLRenderingContext.prototype.getParameter, getParameterProxyHandler);
    if (typeof WebGL2RenderingContext !== 'undefined') {
        WebGL2RenderingContext.prototype.getParameter = new Proxy(WebGL2RenderingContext.prototype.getParameter, getParameterProxyHandler);
    }
} catch (e) { }
