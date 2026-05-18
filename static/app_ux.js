/**
 * Global UX Controller
 * Theme, background, toasts, progress, transitions, and idle timeout.
 */
(() => {
    'use strict';

    const CONFIG = {
        idleTimeoutMs: 30 * 60 * 1000,
        warningBeforeMs: 60 * 1000,
        publicPaths: ['/login', '/password', '/google-login', '/authorize']
    };

    const STATE = {
        progressTimeout: null,
        fetchWrapped: false,
        idleTimer: null,
        warnTimer: null,
        countdownInterval: null,
        countdownSecs: 60
    };

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        initThemeToggle();
        injectTopographicBackground();
        injectUXContainers();
        initPageTransition();
        wrapFetchForProgress();
        initIdleTimeout();
    }

    // ---------------------------------------------------------------------
    // Theme Management
    // ---------------------------------------------------------------------

    function initThemeToggle() {
        const isDark = localStorage.getItem('darkMode') === 'enabled';
        document.body.classList.toggle('dark-mode', isDark);
        updateToggleButtons(isDark);
    }

    window.toggleDarkMode = function () {
        const isDark = !document.body.classList.contains('dark-mode');
        document.body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
        updateToggleButtons(isDark);
    };

    function updateToggleButtons(isDark) {
        document.querySelectorAll('#darkModeToggle').forEach(btn => {
            btn.textContent = isDark ? '☀️' : '🌙';
            btn.style.background = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
            btn.style.color = isDark ? '#fff' : '#000';
        });
    }

    // ---------------------------------------------------------------------
    // Topographic Background
    // ---------------------------------------------------------------------

    function injectTopographicBackground() {
        if (document.getElementById('topo-bg')) return;

        const svgContent = `
            <svg id="topo-bg" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                <defs>
                    <pattern id="topoPattern" x="0" y="0" width="400" height="300" patternUnits="userSpaceOnUse">
                        <g class="topo-pulse">
                            <path class="topo-path" d="M 0 50 Q 50 100 100 50 T 200 50 T 300 100 T 400 50" />
                            <path class="topo-path" d="M 0 100 C 100 150 150 50 250 100 S 350 50 400 100" />
                            <path class="topo-path" d="M 50 0 Q 100 150 50 300 M 150 0 C 200 100 100 200 150 300 M 250 0 S 300 200 250 300 M 350 0 Q 300 150 350 300" />
                            <path class="topo-path" d="M 0 200 Q 80 280 150 200 T 300 250 T 400 200" />
                            <path class="topo-path" d="M 0 250 C 120 200 200 280 300 250 S 380 200 400 250" />
                            <circle cx="200" cy="150" r="20" fill="none" class="topo-path" />
                            <circle cx="200" cy="150" r="40" fill="none" class="topo-path" />
                            <circle cx="200" cy="150" r="60" fill="none" class="topo-path" />
                        </g>
                    </pattern>
                </defs>
                <rect x="0" y="0" width="100%" height="100%" fill="url(#topoPattern)" />
            </svg>`;

        document.body.insertAdjacentHTML('afterbegin', svgContent);
    }

    // ---------------------------------------------------------------------
    // UX Containers
    // ---------------------------------------------------------------------

    function injectUXContainers() {
        ensureElement('app-progress', 'div', document.body);
        ensureElement('toast-container', 'div', document.body);
        injectSessionTimeoutOverlay();
    }

    function ensureElement(id, tagName, parent) {
        if (document.getElementById(id)) return document.getElementById(id);

        const el = document.createElement(tagName);
        el.id = id;
        parent.appendChild(el);
        return el;
    }

    // ---------------------------------------------------------------------
    // Progress Bar
    // ---------------------------------------------------------------------

    window.startProgress = function () {
        const el = document.getElementById('app-progress');
        if (!el) return;

        clearTimeout(STATE.progressTimeout);
        el.style.opacity = '1';
        el.style.width = '0%';
        el.style.transition = 'width 0.2s ease, opacity 0s';

        requestAnimationFrame(() => {
            el.style.transition = 'width 2s cubic-bezier(0.1, 0.8, 0.2, 1), opacity 0.4s ease';
            el.style.width = '70%';
        });
    };

    window.stopProgress = function () {
        const el = document.getElementById('app-progress');
        if (!el) return;

        clearTimeout(STATE.progressTimeout);
        el.style.transition = 'width 0.3s ease-out, opacity 0.4s ease 0.3s';
        el.style.width = '100%';

        STATE.progressTimeout = setTimeout(() => {
            el.style.opacity = '0';
            setTimeout(() => {
                el.style.transition = 'none';
                el.style.width = '0%';
            }, 400);
        }, 300);
    };

    function wrapFetchForProgress() {
        if (STATE.fetchWrapped) return;
        if (typeof window.fetch !== 'function') return;

        STATE.fetchWrapped = true;
        const originalFetch = window.fetch.bind(window);

        window.fetch = async (...args) => {
            startProgress();
            try {
                return await originalFetch(...args);
            } finally {
                stopProgress();
            }
        };
    }

    // ---------------------------------------------------------------------
    // Toasts
    // ---------------------------------------------------------------------

    window.showToast = function (message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            info: 'ℹ️',
            success: '✅',
            error: '❌',
            warning: '⚠️'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <span class="toast-message"></span>
        `;

        toast.querySelector('.toast-message').textContent = message;
        container.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add('show'));

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    };

    // ---------------------------------------------------------------------
    // Page Transitions
    // ---------------------------------------------------------------------

    function initPageTransition() {
        const selectors = '.grid-container, .table-wrap, .section-title, .nav-buttons';
        document.querySelectorAll(selectors).forEach((el, index) => {
            el.classList.add('page-enter');
            el.style.animationDelay = `${index * 0.05}s`;
            el.style.opacity = '0';
        });
    }

    // ---------------------------------------------------------------------
    // Modal Helpers
    // ---------------------------------------------------------------------

    window.openCustomModal = function (id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        modal.style.display = 'flex';
        requestAnimationFrame(() => modal.classList.add('show'));

        const firstInput = modal.querySelector('input, textarea, select, button');
        if (firstInput) firstInput.focus();
    };

    window.closeCustomModal = function (id) {
        const modal = document.getElementById(id);
        if (!modal) return;

        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    };

    // ---------------------------------------------------------------------
    // Idle Session Timeout
    // ---------------------------------------------------------------------

    function injectSessionTimeoutOverlay() {
        if (document.getElementById('session-timeout-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'session-timeout-overlay';
        overlay.innerHTML = `
            <div class="timeout-card">
                <div class="timeout-icon">⏳</div>
                <h3>انتهت مهلة الجلسة قريباً</h3>
                <p>لم يتم رصد أي نشاط. سيتم تسجيل الخروج تلقائياً خلال:</p>
                <span id="session-countdown">60</span>
                <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-top:8px;">
                    <button class="btn-primary" type="button" onclick="resetIdleTimer()" style="padding:10px 24px;font-size:1rem;">
                        أنا هنا — استمر 👋
                    </button>
                    <a href="/logout" class="btn-danger"
                       style="padding:10px 24px;font-size:1rem;border-radius:8px;text-decoration:none;display:inline-flex;align-items:center;">
                        تسجيل الخروج الآن
                    </a>
                </div>
            </div>`;

        document.body.appendChild(overlay);
    }

    function showTimeoutWarning() {
        const overlay = document.getElementById('session-timeout-overlay');
        if (!overlay) return;

        STATE.countdownSecs = 60;
        const countEl = document.getElementById('session-countdown');
        if (countEl) countEl.textContent = STATE.countdownSecs;

        overlay.classList.add('show');

        clearInterval(STATE.countdownInterval);
        STATE.countdownInterval = setInterval(() => {
            STATE.countdownSecs--;
            if (countEl) countEl.textContent = STATE.countdownSecs;

            if (STATE.countdownSecs <= 0) {
                clearInterval(STATE.countdownInterval);
                window.location.href = '/logout';
            }
        }, 1000);
    }

    function hideTimeoutWarning() {
        const overlay = document.getElementById('session-timeout-overlay');
        if (overlay) overlay.classList.remove('show');

        clearInterval(STATE.countdownInterval);
        STATE.countdownInterval = null;
    }

    window.resetIdleTimer = function () {
        hideTimeoutWarning();
        clearTimeout(STATE.idleTimer);
        clearTimeout(STATE.warnTimer);

        STATE.warnTimer = setTimeout(showTimeoutWarning, CONFIG.idleTimeoutMs - CONFIG.warningBeforeMs);
        STATE.idleTimer = setTimeout(() => {
            window.location.href = '/logout';
        }, CONFIG.idleTimeoutMs);
    };

    function initIdleTimeout() {
        const path = window.location.pathname;
        if (CONFIG.publicPaths.some(p => path.startsWith(p))) return;

        const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart', 'touchmove'];
        events.forEach(evt => {
            document.addEventListener(evt, window.resetIdleTimer, { passive: true });
        });

        window.resetIdleTimer();
    }
})();
