/**
 * BZ Command Palette — (Ctrl+K / ⌘K)
 * Unified, searchable command center for all actions.
 */
(function () {
    'use strict';

    // ── Command Registry ────────────────────────────────────────────
    const COMMANDS = [
        // نظرة عامة
        { group: 'نظرة عامة', icon: '🏠', label: 'الرئيسية', hint: 'لوحة القيادة', url: '/', keywords: 'home dashboard رئيسية' },
        { group: 'نظرة عامة', icon: '👑', label: 'لوحة المدير', hint: 'إدارة النظام', url: '/admin', keywords: 'admin مدير إدارة', admin: true },
        { group: 'نظرة عامة', icon: '📊', label: 'لوحة الأسطول', hint: 'مؤشرات المركبات', url: '/fleet_dashboard', keywords: 'fleet أسطول مركبات' },
        { group: 'نظرة عامة', icon: '📈', label: 'مؤشرات الأداء', hint: 'KPIs', url: '/kpis', keywords: 'kpi أداء مؤشرات' },
        { group: 'نظرة عامة', icon: '🧠', label: 'التحليلات', hint: 'Insights', url: '/insights', keywords: 'insights تحليل ذكاء' },

        // التشغيل اليومي
        { group: 'التشغيل اليومي', icon: '📋', label: 'الجدول الأسبوعي', hint: 'توزيع الحركة', url: '/schedule', keywords: 'schedule جدول أسبوعي حركة' },
        { group: 'التشغيل اليومي', icon: '🚚', label: 'نقل عام وخاص', hint: 'جدولة النقل', url: '/schedule/transport', keywords: 'transport نقل عام خاص' },
        { group: 'التشغيل اليومي', icon: '🅿️', label: 'إدارة الساحات', hint: 'دخول وخروج', url: '/yard', keywords: 'yard ساحة دخول خروج' },
        { group: 'التشغيل اليومي', icon: '🛰️', label: 'التتبع الحي', hint: 'GPS مباشر', url: '/tracking', keywords: 'tracking gps تتبع موقع' },
        { group: 'التشغيل اليومي', icon: '🔑', label: 'تسليم واستلام', hint: 'العهد', url: '/handover', keywords: 'handover تسليم استلام عهدة' },

        // الأفراد والمركبات
        { group: 'الأفراد والمركبات', icon: '👥', label: 'الموظفون', hint: 'سجل الموظفين', url: '/employees', keywords: 'employees موظف موظفين', admin: true },
        { group: 'الأفراد والمركبات', icon: '🚗', label: 'مركبات الدمام', hint: 'تفاصيل المركبات', url: '/dammam', keywords: 'dammam دمام مركبات' },
        { group: 'الأفراد والمركبات', icon: '🚛', label: 'سائقو النقل', hint: 'بيانات السائقين', url: '/drivers_info', keywords: 'drivers سائق سائقين نقل' },
        { group: 'الأفراد والمركبات', icon: '🔔', label: 'تنبيهات الوثائق', hint: 'انتهاء المستندات', url: '/alerts', keywords: 'alerts تنبيه وثائق انتهاء' },
        { group: 'الأفراد والمركبات', icon: '📂', label: 'الوثائق', hint: 'ملفات ومستندات', url: '/documents', keywords: 'documents وثائق ملفات' },

        // الصيانة والمخزون
        { group: 'الصيانة والمخزون', icon: '🔧', label: 'الورشة', hint: 'صيانة وإصلاح', url: '/workshop', keywords: 'workshop ورشة صيانة إصلاح' },
        { group: 'الصيانة والمخزون', icon: '⛽', label: 'المحروقات', hint: 'تموين واستهلاك', url: '/fuel', keywords: 'fuel وقود محروقات بنزين' },
        { group: 'الصيانة والمخزون', icon: '📜️', label: 'الزيوت والفلاتر', hint: 'سجل الزيوت', url: '/oils', keywords: 'oils زيوت فلاتر' },
        { group: 'الصيانة والمخزون', icon: '💿', label: 'الإطارات', hint: 'مخزون الإطارات', url: '/inventory/tires', keywords: 'tires إطارات كفرات' },
        { group: 'الصيانة والمخزون', icon: '🔋', label: 'البطاريات', hint: 'مخزون البطاريات', url: '/inventory/batteries', keywords: 'batteries بطاريات' },
        { group: 'الصيانة والمخزون', icon: '📦', label: 'قطع الغيار', hint: 'المخزون', url: '/spare_parts', keywords: 'spare parts قطع غيار' },
        { group: 'الصيانة والمخزون', icon: '🚿', label: 'الغسيل', hint: 'جدول الغسيل', url: '/washing', keywords: 'washing غسيل غسل' },

        // المالية والسجلات
        { group: 'المالية والسجلات', icon: '🛒', label: 'المشتريات', hint: 'أوامر الشراء', url: '/purchase', keywords: 'purchase مشتريات شراء' },
        { group: 'المالية والسجلات', icon: '💵', label: 'العهد المالية', hint: 'الصندوق الصغير', url: '/finance/petty-cash', keywords: 'petty cash عهدة مالية صندوق' },
        { group: 'المالية والسجلات', icon: '🧾', label: 'الفواتير', hint: 'إصدار وأرشفة', url: '/invoice', keywords: 'invoice فواتير فاتورة' },
        { group: 'المالية والسجلات', icon: '🚨', label: 'الحوادث', hint: 'سجل الحوادث', url: '/incidents', keywords: 'incidents حوادث حادث' },
        { group: 'المالية والسجلات', icon: '📁', label: 'السجلات', hint: 'أرشيف العمليات', url: '/records', keywords: 'records سجلات أرشيف' },

        // النظام
        { group: 'النظام', icon: '⚙️', label: 'الإعدادات', hint: 'تهيئة النظام', url: '/settings', keywords: 'settings إعدادات تهيئة' },
        { group: 'النظام', icon: '↪', label: 'تسجيل الخروج', hint: 'إنهاء الجلسة', url: '/logout', keywords: 'logout خروج إنهاء' },
    ];

    // ── DOM Creation ──────────────────────────────────────────────────
    const backdrop = document.createElement('div');
    backdrop.className = 'bz-cmd-backdrop';
    backdrop.id = 'bzCmdBackdrop';

    const dialog = document.createElement('div');
    dialog.className = 'bz-cmd-dialog';
    dialog.id = 'bzCmdDialog';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-label', 'لوحة الأوامر');
    dialog.innerHTML = `
        <div class="bz-cmd-search">
            <span class="bz-cmd-search-icon">⌕</span>
            <input id="bzCmdInput" type="text" placeholder="ابحث عن أمر أو صفحة…" autocomplete="off" />
            <span class="bz-cmd-kbd">ESC</span>
        </div>
        <div class="bz-cmd-list" id="bzCmdList"></div>
        <div class="bz-cmd-footer">
            <span><span class="bz-cmd-kbd">↑↓</span> للتنقل</span>
            <span><span class="bz-cmd-kbd">Enter</span> للفتح</span>
            <span><span class="bz-cmd-kbd">Esc</span> للإغلاق</span>
        </div>
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(dialog);

    // FAB button
    const fab = document.createElement('button');
    fab.className = 'bz-fab-cmd';
    fab.id = 'bzFabCmd';
    fab.type = 'button';
    fab.setAttribute('aria-label', 'لوحة الأوامر');
    fab.innerHTML = `⌕<span class="fab-tooltip">لوحة الأوامر (Ctrl+K)</span>`;
    document.body.appendChild(fab);

    const input = document.getElementById('bzCmdInput');
    const list = document.getElementById('bzCmdList');
    let activeIdx = -1;

    // ── Render ────────────────────────────────────────────────────────
    function render(query) {
        const q = (query || '').trim().toLowerCase();
        const isAdmin = document.body.classList.contains('bz-is-admin') ||
                        (window.BZ_IS_ADMIN === true);

        let filtered = COMMANDS.filter(c => {
            if (c.admin && !isAdmin) return false;
            if (!q) return true;
            return c.label.includes(q) || c.hint.includes(q) || c.keywords.includes(q);
        });

        if (filtered.length === 0) {
            list.innerHTML = '<div class="bz-cmd-empty">لا توجد نتائج مطابقة</div>';
            activeIdx = -1;
            return;
        }

        let html = '';
        let currentGroup = '';
        filtered.forEach((c, i) => {
            if (c.group !== currentGroup) {
                currentGroup = c.group;
                html += `<div class="bz-cmd-group-label">${c.group}</div>`;
            }
            html += `<a href="${c.url}" class="bz-cmd-item" data-cmd-idx="${i}">
                <span class="cmd-icon">${c.icon}</span>
                <span class="cmd-label">${c.label}</span>
                <span class="cmd-hint">${c.hint}</span>
            </a>`;
        });
        list.innerHTML = html;
        activeIdx = -1;
    }

    function setActive(idx) {
        const items = list.querySelectorAll('.bz-cmd-item');
        items.forEach(el => el.classList.remove('is-active'));
        if (idx >= 0 && idx < items.length) {
            items[idx].classList.add('is-active');
            items[idx].scrollIntoView({ block: 'nearest' });
        }
        activeIdx = idx;
    }

    // ── Open / Close ──────────────────────────────────────────────────
    function open() {
        backdrop.classList.add('is-open');
        dialog.classList.add('is-open');
        input.value = '';
        render('');
        setTimeout(() => input.focus(), 50);
    }

    function close() {
        backdrop.classList.remove('is-open');
        dialog.classList.remove('is-open');
        input.value = '';
    }

    function isOpen() {
        return dialog.classList.contains('is-open');
    }

    // ── Events ────────────────────────────────────────────────────────
    backdrop.addEventListener('click', close);
    fab.addEventListener('click', open);

    input.addEventListener('input', () => render(input.value));
    input.addEventListener('keydown', (e) => {
        const items = list.querySelectorAll('.bz-cmd-item');
        const count = items.length;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setActive(activeIdx < count - 1 ? activeIdx + 1 : 0);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setActive(activeIdx > 0 ? activeIdx - 1 : count - 1);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (activeIdx >= 0 && items[activeIdx]) {
                window.location.href = items[activeIdx].getAttribute('href');
            }
        } else if (e.key === 'Escape') {
            close();
        }
    });

    // Global keyboard shortcut
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            isOpen() ? close() : open();
        }
        if (e.key === 'Escape' && isOpen()) {
            close();
        }
    });

    // ── Welcome Overlay ──────────────────────────────────────────────
    function showWelcome() {
        const flag = sessionStorage.getItem('bz_welcomed');
        if (flag) return;

        // Get display name from the page or session
        const nameEl = document.querySelector('[data-welcome-name]');
        const displayName = nameEl ? nameEl.getAttribute('data-welcome-name') : null;
        if (!displayName) return;

        sessionStorage.setItem('bz_welcomed', '1');

        const roleEl = document.querySelector('[data-welcome-role]');
        const displayRole = roleEl ? roleEl.getAttribute('data-welcome-role') : '';

        const roleLabels = {
            'admin': 'مدير النظام',
            'branch_manager': 'مدير فرع',
            'data_entry': 'إدخال بيانات',
            'viewer': 'مشاهد',
            'kiosk': 'كشك'
        };

        const roleText = roleLabels[displayRole] || displayRole || '';

        // Get time-based greeting
        const hour = new Date().getHours();
        let greeting;
        if (hour < 6) greeting = 'مساء الخير';
        else if (hour < 12) greeting = 'صباح الخير';
        else if (hour < 17) greeting = 'مساء الخير';
        else greeting = 'مساء الخير';

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'bz-welcome-overlay';
        overlay.innerHTML = `
            <div class="bz-welcome-particles" id="bzWelcomeParticles"></div>
            <img src="/static/nav_logo.png" alt="" class="bz-welcome-logo" />
            <span class="bz-welcome-greeting">${greeting} 👋</span>
            <span class="bz-welcome-name">${displayName}</span>
            ${roleText ? `<span class="bz-welcome-role">${roleText} — شركة بن زومة الدولية</span>` : ''}
            <div class="bz-welcome-bar"><div class="bz-welcome-bar-fill"></div></div>
        `;
        document.body.appendChild(overlay);

        // Floating particles
        const particleBox = document.getElementById('bzWelcomeParticles');
        for (let i = 0; i < 18; i++) {
            const p = document.createElement('div');
            p.className = 'bz-welcome-particle';
            p.style.left = Math.random() * 100 + '%';
            p.style.top = Math.random() * 100 + '%';
            p.style.animationDelay = (Math.random() * 3) + 's';
            p.style.animationDuration = (3 + Math.random() * 3) + 's';
            p.style.width = p.style.height = (3 + Math.random() * 4) + 'px';
            particleBox.appendChild(p);
        }

        // Auto-dismiss after progress bar completes
        setTimeout(() => {
            overlay.classList.add('fade-out');
            setTimeout(() => overlay.remove(), 900);
        }, 3400);

        // Click to dismiss early
        overlay.addEventListener('click', () => {
            overlay.classList.add('fade-out');
            setTimeout(() => overlay.remove(), 900);
        });
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showWelcome);
    } else {
        showWelcome();
    }
})();
