/**
 * GLOBAL UX & UI CONTROLLER
 * Handles Theme Toggling, Topographic Background, Toasts, Progress Bar,
 * Page Transitions, and Idle Session Timeout.
 */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    injectTopographicBackground();
    injectUXContainers();
    initPageTransition();
    wrapFetchForProgress();
    initIdleTimeout();
});

// --- Theme Management ---
function initThemeToggle() {
    // تم إيقاف الوضع الليلي وإزالته بالكامل
    document.body.classList.remove('dark-mode');
    localStorage.removeItem('darkMode');
    
    // إخفاء أي زر قديم لو تبقّى في الصفحة
    document.querySelectorAll('#darkModeToggle').forEach(btn => {
        btn.style.display = 'none';
    });
}

window.toggleDarkMode = function() {
    // معطل
};

function updateToggleButtons(isDark) {
    // معطل
}

// --- Topographic Texture ---
function injectTopographicBackground() {
    if (document.getElementById('topo-bg')) return;

    const svgContent = `
    <svg id="topo-bg" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="position: fixed; top: 0; left: 0; z-index: -1; pointer-events: none; opacity: 0.4;">
        <defs>
            <pattern id="topoPattern" x="0" y="0" width="400" height="300" patternUnits="userSpaceOnUse">
                <g class="topo-pulse" style="stroke: var(--accent); stroke-width: 1; fill: none; opacity: 0.15;">
                    <path class="topo-path" d="M 0 50 Q 50 100 100 50 T 200 50 T 300 100 T 400 50" />
                    <path class="topo-path" d="M 0 100 C 100 150 150 50 250 100 S 350 50 400 100" />
                    <path class="topo-path" d="M 50 0 Q 100 150 50 300 M 150 0 C 200 100 100 200 150 300 M 250 0 S 300 200 250 300 M 350 0 Q 300 150 350 300" />
                    <path class="topo-path" d="M 0 200 Q 80 280 150 200 T 300 250 T 400 200" />
                    <path class="topo-path" d="M 0 250 C 120 200 200 280 300 250 S 380 200 400 250" />
                    <!-- Clusters -->
                    <circle cx="200" cy="150" r="20" class="topo-path" />
                    <circle cx="200" cy="150" r="40" class="topo-path" />
                    <circle cx="200" cy="150" r="60" class="topo-path" />
                </g>
            </pattern>
        </defs>
        <rect x="0" y="0" width="100%" height="100%" fill="url(#topoPattern)"></rect>
    </svg>`;

    document.body.insertAdjacentHTML('afterbegin', svgContent);
}

// --- UX Containers (Toasts & Progress) ---
function injectUXContainers() {
    if (!document.getElementById('app-progress')) {
        const progress = document.createElement('div');
        progress.id = 'app-progress';
        document.body.appendChild(progress);
    }
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }
    injectSessionTimeoutOverlay();
}

// --- Progress Bar Controller ---
let progressTimer = null;
window.startProgress = function() {
    const el = document.getElementById('app-progress');
    if (!el) return;
    clearInterval(progressTimer);
    el.style.opacity = '1';
    el.style.width = '0%';
    el.style.transition = 'width 0.2s ease, opacity 0s';
    setTimeout(() => {
        el.style.transition = 'width 2s cubic-bezier(0.1, 0.8, 0.2, 1), opacity 0.4s ease';
        el.style.width = '70%';
    }, 50);
};

window.stopProgress = function() {
    const el = document.getElementById('app-progress');
    if (!el) return;
    clearInterval(progressTimer);
    el.style.transition = 'width 0.3s ease-out, opacity 0.4s ease 0.3s';
    el.style.width = '100%';
    progressTimer = setTimeout(() => {
        el.style.opacity = '0';
        setTimeout(() => {
            el.style.transition = 'none';
            el.style.width = '0%';
        }, 400);
    }, 300);
};

// --- Fetch Wrapper for Progress ---
function wrapFetchForProgress() {
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        startProgress();
        try {
            const response = await originalFetch(...args);
            return response;
        } finally {
            stopProgress();
        }
    };
}

// --- Toast Controller ---
window.showToast = function(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
};

// --- Page Transitions ---
function initPageTransition() {
    const wrappers = document.querySelectorAll(
        '.grid-container, .table-wrap, .section-title, .nav-buttons'
    );
    wrappers.forEach((el, index) => {
        el.classList.add('page-enter');
        el.style.animationDelay = `${index * 0.05}s`;
        el.style.opacity = '0';
    });
}

// --- Modal Helpers ---
window.openCustomModal = function(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('show'), 10);
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) firstInput.focus();
    }
};

window.closeCustomModal = function(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => { modal.style.display = 'none'; }, 300);
    }
};

// =============================================================================
// IDLE SESSION TIMEOUT
// Warning at 29 min → auto-logout at 30 min of inactivity.
// =============================================================================

const IDLE_TIMEOUT_MS = 30 * 60 * 1000;   // 30 minutes total
const WARN_BEFORE_MS  = 60 * 1000;         // show warning 60 sec before logout
const WARN_TIMEOUT_MS = IDLE_TIMEOUT_MS - WARN_BEFORE_MS;

let _idleTimer         = null;
let _warnTimer         = null;
let _countdownInterval = null;
let _countdownSecs     = 60;

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
                <button class="btn-primary" onclick="resetIdleTimer()" style="padding:10px 24px;font-size:1rem;">
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

    _countdownSecs = 60;
    const countEl = document.getElementById('session-countdown');
    if (countEl) countEl.textContent = _countdownSecs;
    overlay.classList.add('show');

    clearInterval(_countdownInterval);
    _countdownInterval = setInterval(() => {
        _countdownSecs--;
        if (countEl) countEl.textContent = _countdownSecs;
        if (_countdownSecs <= 0) {
            clearInterval(_countdownInterval);
            window.location.href = '/logout';
        }
    }, 1000);

    // Hard failsafe logout
    clearTimeout(_idleTimer);
    _idleTimer = setTimeout(() => { window.location.href = '/logout'; }, WARN_BEFORE_MS);
}

function hideTimeoutWarning() {
    const overlay = document.getElementById('session-timeout-overlay');
    if (overlay) overlay.classList.remove('show');
    clearInterval(_countdownInterval);
}

window.resetIdleTimer = function() {
    hideTimeoutWarning();
    clearTimeout(_idleTimer);
    clearTimeout(_warnTimer);

    _warnTimer = setTimeout(showTimeoutWarning, WARN_TIMEOUT_MS);
    _idleTimer = setTimeout(() => { window.location.href = '/logout'; }, IDLE_TIMEOUT_MS);
};

function initIdleTimeout() {
    // Skip on public pages
    const path = window.location.pathname;
    const publicPaths = ['/login', '/password', '/google-login', '/authorize'];
    if (publicPaths.some(p => path.startsWith(p))) return;

    // Reset timer on any user interaction
    ['mousemove', 'keydown', 'click', 'scroll', 'touchstart', 'touchmove'].forEach(evt => {
        document.addEventListener(evt, window.resetIdleTimer, { passive: true });
    });

    // Kick off the idle timer
    window.resetIdleTimer();
}

