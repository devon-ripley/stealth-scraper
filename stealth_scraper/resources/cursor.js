(function () {
    const ID = 'stealth-cursor-tracker';
    if (document.getElementById(ID)) return;

    const cursor = document.createElement('div');
    cursor.id = ID;
    Object.assign(cursor.style, {
        width: '20px',
        height: '20px',
        backgroundColor: 'rgba(255, 0, 0, 0.4)',
        border: '2px solid red',
        borderRadius: '50%',
        position: 'fixed',
        pointerEvents: 'none',
        zIndex: '999999',
        transition: 'transform 0.05s linear, background-color 0.1s',
        transform: 'translate3d(0, 0, 0)',
        left: '0',
        top: '0',
        willChange: 'transform'
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

    window.addEventListener('mousemove', (e) => {
        cursor.style.transform = `translate3d(${e.clientX - 10}px, ${e.clientY - 10}px, 0)`;
    }, { passive: true });

    window.addEventListener('mousedown', () => {
        cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.8)';
        cursor.style.transform += ' scale(0.8)';
    }, { passive: true });

    window.addEventListener('mouseup', () => {
        cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.4)';
    }, { passive: true });
})();
