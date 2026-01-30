const STEALTH_CONFIG = "__STEALTH_CONFIG__";

// ========================================
// WEBDRIVER PROPERTY MASKING
// ========================================

Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
    configurable: true
});

delete navigator.__proto__.webdriver;

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
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);

// ========================================
// PLUGINS MASKING
// ========================================

const makePluginArray = () => {
    const plugins = [
        { name: "Chrome PDF Plugin", filename: "internal-pdf-viewer", description: "Portable Document Format" },
        { name: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", description: "" },
        { name: "Native Client", filename: "internal-nacl-plugin", description: "" }
    ];

    const pluginArray = Object.create(PluginArray.prototype);
    plugins.forEach((p, i) => {
        const plugin = Object.create(Plugin.prototype);
        plugin.name = p.name;
        plugin.filename = p.filename;
        plugin.description = p.description;
        pluginArray[i] = plugin;
    });
    pluginArray.length = plugins.length;
    return pluginArray;
};

Object.defineProperty(navigator, 'plugins', {
    get: () => makePluginArray(),
    configurable: true
});

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
    get: () => 'Win32',
    configurable: true
});

Object.defineProperty(navigator, 'vendor', {
    get: () => 'Google Inc.',
    configurable: true
});

// ========================================
// CANVAS FINGERPRINTING PROTECTION
// ========================================

const originalGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function (type, attributes) {
    const context = originalGetContext.call(this, type, attributes);
    if (type === '2d' && context) {
        const originalFillText = context.fillText.bind(context);
        context.fillText = function (...args) {
            context.shadowBlur = Math.random() * STEALTH_CONFIG.canvas_noise;
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
