(function () {
    const ID = 'stealth-cursor-tracker';
    if (document.getElementById(ID)) return;

    const cursor = document.createElement('div');
    cursor.id = ID;

    // Add pulse animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes stealth-cursor-pulse {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(2.5); opacity: 0; }
        }
        .stealth-cursor-click-effect {
            position: fixed;
            border: 3px solid #ff4757;
            border-radius: 50%;
            pointer-events: none;
            z-index: 999998;
            animation: stealth-cursor-pulse 0.4s ease-out forwards;
        }
    `;
    document.head.appendChild(style);

    Object.assign(cursor.style, {
        width: '14px',
        height: '14px',
        backgroundColor: 'rgba(255, 71, 87, 0.6)',
        border: '2px solid #ff4757',
        borderRadius: '50%',
        position: 'fixed',
        pointerEvents: 'none',
        zIndex: '999999',
        transition: 'transform 0.1s ease-out, background-color 0.1s',
        transform: 'translate3d(0, 0, 0)',
        left: '0',
        top: '0',
        willChange: 'transform',
        boxShadow: '0 0 8px rgba(255, 71, 87, 0.5)'
    });

    const inject = () => {
        if (document.getElementById(ID)) return;
        (document.body || document.documentElement).appendChild(cursor);
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inject);
    } else {
        inject();
    }

    let lastX = 0, lastY = 0;
    window.addEventListener('mousemove', (e) => {
        lastX = e.clientX;
        lastY = e.clientY;
        cursor.style.transform = `translate3d(${lastX - 7}px, ${lastY - 7}px, 0)`;
    }, { passive: true });

    window.addEventListener('mousedown', (e) => {
        cursor.style.backgroundColor = 'rgba(255, 71, 87, 1)';
        cursor.style.transform = `translate3d(${lastX - 7}px, ${lastY - 7}px, 0) scale(0.7)`;

        // Visual click wave
        const wave = document.createElement('div');
        wave.className = 'stealth-cursor-click-effect';
        Object.assign(wave.style, {
            left: `${lastX - 7}px`,
            top: `${lastY - 7}px`,
            width: '14px',
            height: '14px'
        });
        document.body.appendChild(wave);
        setTimeout(() => wave.remove(), 400);
    }, { passive: true });

    window.addEventListener('mouseup', () => {
        cursor.style.backgroundColor = 'rgba(255, 71, 87, 0.6)';
        cursor.style.transform = `translate3d(${lastX - 7}px, ${lastY - 7}px, 0) scale(1)`;
    }, { passive: true });
})();
