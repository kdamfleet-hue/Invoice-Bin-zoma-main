/**
 * GLOBAL UX & UI CONTROLLER
 * Handles Theme Toggling, Topographic Background, Toasts, Progress Bar,
 * Page Transitions, Idle Session Timeout, and Bilingual Translation.
 */

// Global flag: are we inside the open /importantworkstation sandbox? Every tab uses this
// to start EMPTY and persist to the server (id=2) instead of showing the main site's data.
// Purely path-based, so the main site (/) is never affected — even in the same browser.
window.BZ_WS = window.location.pathname.indexOf('/importantworkstation') === 0;

// Active branch id (injected per-page before this script runs; الدمام = 1 by default).
// Non-الدمام branches are "isolated" like the workstation: they start EMPTY and must never
// inherit الدمام's locally-cached data or its bundled seed files.
window.BZ_BRANCH_ID = window.BZ_BRANCH_ID || 1;
window.BZ_ISOLATED = window.BZ_WS || (window.BZ_BRANCH_ID !== 1);

// Isolate this mode's browser storage so cached edits can NEVER bleed across branches or
// into الدمام. Runs first, before any tab code touches localStorage. الدمام (id=1) keeps
// NO prefix → byte-for-byte unchanged; workstation = 'ws:'; other branches = 'b<id>:'.
(function () {
    try {
        var ns = window.BZ_WS ? 'ws:' : (window.BZ_BRANCH_ID !== 1 ? ('b' + window.BZ_BRANCH_ID + ':') : '');
        if (!ns) return;
        var ls = window.localStorage;
        var g = ls.getItem.bind(ls), s = ls.setItem.bind(ls), r = ls.removeItem.bind(ls);
        ls.getItem = function (k) { return g(ns + k); };
        ls.setItem = function (k, v) { return s(ns + k, v); };
        ls.removeItem = function (k) { return r(ns + k); };
    } catch (e) { /* ignore */ }
})();

// A fresh non-الدمام branch must NOT inherit الدمام's static seed files (employees/schedule/
// fleet defaults), so make those specific fetches resolve empty. الدمام and the workstation
// keep their existing behavior untouched.
(function () {
    try {
        if (window.BZ_BRANCH_ID === 1 || window.BZ_WS) return;   // only the other branches
        var SEED = /\/static\/(employees_default|schedule_data|fleet_data)\.json(\?|$)/;
        var of = window.fetch ? window.fetch.bind(window) : null;
        if (!of) return;
        window.fetch = function (input, init) {
            var url = (typeof input === 'string') ? input : (input && input.url) || '';
            if (SEED.test(url)) {
                return Promise.resolve(new Response('null', { status: 200, headers: { 'Content-Type': 'application/json' } }));
            }
            return of(input, init);
        };
    } catch (e) { /* ignore */ }
})();

const translations = {
    "en": {
        // Titles and headers
        "منشئ الفواتير الاحترافي | شركة بن زومة": "Professional Invoice Builder | Bin Zoma Co.",
        "نظام الفواتير الذكي": "Smart Invoice System",
        "اختر السائق وسيتم تعبئة البيانات تلقائياً": "Select a driver to auto-populate fields",
        "بيان استهلاك الزيوت والفلاتر للسيارات الديزل (فرع الدمام) من تاريخ 2025/12/17 الى تاريخ 2026/2/7": "Statement of Oil & Filter Consumption for Diesel Vehicles (Dammam Branch) from 2025/12/17 to 2026/2/7",
        "بيان الزيوت والفلاتر | شركة بن زومة": "Oils & Filters Statement | Bin Zoma Co.",
        "نظام إدارة الأسطول": "Fleet Management System",
        "فرع الدمام - إدارة الصيانة": "Dammam Branch - Maintenance Dept",
        
        // Navigation links
        "الرئيسية": "Home",
        "الخدمات": "Services",
        "من نحن": "About Us",
        "موقعنا الرسمي": "Official Website",
        "تواصل معنا": "Contact Us",
        "العودة للفواتير": "Back to Invoices",
        "العودة للرئيسية": "Back to Home",
        "طلب شراء وإصلاح": "Purchase Order & Repair",
        "تحديث الجدول الأسبوعي": "Update Weekly Schedule",
        "جدول الغسيل": "Washing Schedule",
        "نظام التتبع GPS": "GPS Tracking System",
        "بيانات موظفين الفرع": "Branch Employees Data",
        "تحضير جدول الغسيل": "Prepare Washing List",
        "التتبع المباشر": "Live Tracking",
        "مزامنة كشف GPS": "Sync GPS Report",
        "تسجيل الخروج": "Logout",
        "تسجيل خروج": "Logout",
        
        // Buttons
        "⚙️ إدارة السائقين وقاعدة البيانات": "⚙️ Manage Drivers & Database",
        "📄 إنشاء بيان زيوت وفلاتر": "📄 Oils & Filters Statement",
        "🛒 طلبات الشراء": "🛒 Purchase Orders",
        "📋 الجدول الأسبوعي": "📋 Weekly Schedule",
        "👥 بيانات موظفين الفرع": "👥 Branch Employees Data",
        "🚿 تحضير جدول الغسيل": "🚿 Washing List",
        "🛰️ التتبع المباشر": "🛰️ Live Tracking",
        "📡 مزامنة كشف GPS": "📡 Sync GPS Report",
        "+ إضافة صف جديد": "+ Add New Row",
        "إضافة صف جديد": "Add New Row",
        "📥 تحميل كملف Excel": "📥 Download Excel File",
        "🖨 طباعة الجدول": "🖨 Print Table",
        "إرسال رسالة واتساب": "Send WhatsApp Message",
        "إضافة إلى قاعدة البيانات ➕": "Add to Database ➕",
        "إغلاق ✖": "Close ✖",
        "تعديل": "Edit",
        "حذف": "Delete",
        
        // Invoice Form
        "اسم السائق (اكتب للبحث)": "Driver Name (Type to search)",
        "ابحث عن اسم السائق هنا...": "Search for driver name here...",
        "نوع السيارة": "Vehicle Type",
        "مثال: ايسوزو دينا 2024": "e.g., Isuzu Dina 2024",
        "رقم اللوحة": "Plate Number",
        "مثال: ا ب ج 1234": "e.g., ABC 1234",
        "نوع الطلب": "Request Type",
        "صيانة دورية": "Periodic Maintenance",
        "إصلاح عطل": "Repair Fault",
        "إصلاح بنشر": "Tire Repair",
        "تغيير قطع غيار": "Change Spare Parts",
        "غيار زيت": "Oil Change",
        "أخرى": "Other",
        "رقم الإقامة": "Iqama Number",
        "مثال: 2441077944": "e.g., 2441077944",
        "التاريخ": "Date",
        "الكمية": "Quantity",
        "السعر الإفرادي (ريال)": "Unit Price (SAR)",
        "الوصف / التفاصيل": "Description / Details",
        "أدخل تفاصيل الفاتورة أو القطع المستبدلة...": "Enter invoice details or replaced parts...",
        "الحسابات المالية": "Financial Calculations",
        "المبلغ": "Subtotal",
        "الضريبة (15%)": "Tax (15%)",
        "الإجمالي النهائي": "Grand Total",
        "المبلغ الإجمالي (قبل الضريبة)": "Subtotal (Before Tax)",
        "ضريبة القيمة المضافة (15%)": "VAT (15%)",
        "المجموع الكلي (مع الضريبة)": "Grand Total (With Tax)",
        
        // Submit buttons
        "تصدير PDF / Excel": "Export PDF / Excel",
        "📧 إرسال الفاتورة للإيميل": "📧 Email Invoice",
        "💬 إرسال عبر الواتساب": "💬 Send via WhatsApp",
        "🗑️ إفراغ الفاتورة": "🗑️ Clear Invoice",
        
        // Modals / Database management
        "إدارة قاعدة بيانات السائقين": "Manage Drivers Database",
        "الاسم الرباعي (مطلوب)": "Full Name (Required)",
        "الرقم الوظيفي": "Employee ID",
        "نوع السيارة وموديلها": "Vehicle Type & Model",
        "تاريخ انتهاء بطاقة السائق": "Driver Card Expiry Date",
        "الاسم": "Name",
        "السيارة": "Vehicle",
        "اللوحة": "Plate",
        "الإقامة": "Iqama",
        "بطاقة السائق": "Driver Card",
        "الجوال": "Phone",
        "الإجراءات": "Actions",
        "تحميل البيانات...": "Loading data...",
        "حذف الصف": "Delete Row",
        
        // Oils page table headers
        "م": "No.",
        "رقم لوحة السيارة": "Vehicle Plate Number",
        "المستخدم": "User",
        "تاريخ تغيير الزيت": "Oil Change Date",
        "رقم العداد": "Odometer",
        "عدد اللترات": "Liters Count",
        "عدد فلاتر الزيت والديزل والهواء": "Oil, Diesel & Air Filters Count",
        "حذف": "Delete",
        
        // Purchase Page
        "استمارة طلب شراء قطع غيار وإصلاح سيارات": "Purchase Request Form for Spare Parts & Vehicle Repair",
        "الاسم الوظيفي": "Job Title",
        "فرع": "Branch",
        "الموديل": "Model",
        "أولا : قطع غيار": "First: Spare Parts",
        "الوصف": "Description",
        "سعر الوحدة": "Unit Price",
        "القيمة": "Value",
        "ملاحظات": "Notes",
        "ثانيا : أجور إصلاح": "Second: Repair Labor",
        "ثالثا : إطارات": "Third: Tires",
        "تاريخ التركيب": "Installation Date",
        "العدد": "Count",
        "أمامي": "Front",
        "خلفي": "Back",
        "السابق": "Previous",
        "الحالي": "Current",
        "المسافة المقطوعة": "Distance Driven",
        "رابعا : بطاريات": "Fourth: Batteries",
        "المقاس": "Size",
        "الأمبير": "Amps",
        "خامسا : ملخص الحسابات": "Fifth: Financial Summary",
        "الإجمالي لقطع الغيار": "Total Spare Parts",
        "الإجمالي لأجور الإصلاح": "Total Repair Labor",
        "الإجمالي للإطارات": "Total Tires",
        "الإجمالي للبطاريات": "Total Batteries",
        "ملاحظات وتوصية الورشة": "Workshop Recommendation & Notes",
        "حفظ وإرسال": "Save & Send",
        
        // Washing Page
        "كشف غسيل السيارات فرع الدمام": "Vehicle Washing List - Dammam Branch",
        "يناير": "January",
        "فبراير": "February",
        "مارس": "March",
        "أبريل": "April",
        "مايو": "May",
        "يونيو": "June",
        "يوليو": "July",
        "أغسطس": "August",
        "سبتمبر": "September",
        "أكتوبر": "October",
        "نوفمبر": "November",
        "ديسمبر": "December",
        "استلم": "Received",
        "لم يستلم": "Not Received",
        
        // GPS page
        "مزامنة لوحة التتبع مع كشف السيارات": "Sync Tracking Board with Vehicle List",
        "تحميل ملف كشف سيارات GPS": "Upload GPS Vehicle List File",
        "تحميل ملف كشف السائقين (الجدول الأسبوعي)": "Upload Drivers List File (Weekly Schedule)",
        "مزامنة ومطابقة البيانات": "Sync & Match Data",
        "النتائج والتقارير": "Results & Reports",
        
        // Employees page headers
        "بيانات جميع الموظفين في الفرع": "All Branch Employees Data",
        "بيانات الموظف العامة": "General Employee Data",
        "مقيم": "Muqeem Data",
        "قوى": "Qiwa Data",
        "مسيرات الشركة": "Company Payroll",
        "البصمة": "Fingerprint",
        "المركبة": "Vehicle Details",
        "السكن والسند والتامين": "Housing, Bond & Insurance",
        "اسم العامل": "Employee Name",
        "الاسم بالانجليزي": "English Name",
        "الجنسية": "Nationality",
        "المسمئ الوظيفي": "Job Title",
        "الايميل": "Email",
        "تاريخ انتهاء الاقامة": "Iqama Expiry",
        "تاريخ انتهاء الجواز": "Passport Expiry",
        "تاريح الميلاد": "Date of Birth",
        "العمر": "Age",
        "المهنة": "Profession",
        "رقم صاحب العمل": "Employer Number",
        "تاريخ التعين": "Hire Date",
        "تاريخ انتهاء العقد": "Contract Expiry",
        "التامينات": "Social Insurance",
        "الاساسي في قوى": "Basic in Qiwa",
        "بدل السكن في قوى": "Housing Allowance in Qiwa",
        "النقل في قوى": "Transport in Qiwa",
        "اخرى في قوى": "Others in Qiwa",
        "المنشئة": "Establishment",
        "التنبيه بتجديد العقد": "Contract Renewal Alert",
        "في الشركة الاساسي": "Company Basic",
        "في الشركة بدل السكن": "Company Housing Allowance",
        "بدل نقل": "Transport Allowance",
        "بدل اتصال": "Communication Allowance",
        "ملاحظات الرواتب": "Payroll Notes",
        "رقم البصمة": "Fingerprint Number",
        "الدخول": "Access/Entry",
        "الرخصة": "License",
        "الايبان": "IBAN",
        "نوع النقل": "Transport Type",
        "حمولة المركبة(عدد الركاب)": "Vehicle Capacity (Passengers)",
        "الماركة": "Make",
        "الطراز": "Model Series",
        "رقم الهيكل": "Chassis Number",
        "السكن": "Housing",
        "سند امر": "Promissory Note",
        "كرت البلدية": "Municipality Card",
        "الكرت الوظيفي": "Work ID Card",
        "حالة التامين": "Insurance Status",
        "الاستحقاقات السنوية": "Annual Entitlements"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    injectGlobalNavLinks();
    applyWorkstationRestrictions();
    buildEnterpriseShell();
    injectBranchSwitcher();
    injectContactDock();
    injectHeroLogo();
    injectClock();
    injectTabHistory();
    initThemeToggle();
    injectTopographicBackground();
    injectUXContainers();
    initPageTransition();
    wrapFetchForProgress();
    initIdleTimeout();
    initLanguageTranslation();
    registerPWA();
    injectLucide();
});

// --- Branch switcher: swap the active branch site-wide (multi-branch data isolation) ---
// Skips workstation pages (the workstation is its own isolated mode). Updates the header
// subtitle on every tab, exposes window.BZ_BRANCH, and reloads after switching so all data refreshes.
function injectBranchSwitcher() {
    try {
        if (typeof WS_PREFIX === 'string' && location.pathname.indexOf(WS_PREFIX) === 0) return;
        var actions = document.querySelector('.bz-topbar .bz-actions');
        if (!actions || document.getElementById('bzBranchWrap')) return;
        fetch('/api/branch', { headers: { 'Accept': 'application/json' } })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (j) {
                if (!j || !j.branches) return;
                window.BZ_BRANCH = j.name || 'الدمام';
                var sub = document.querySelector('.bz-brand-text span');
                if (sub) sub.textContent = 'نظام إدارة الأسطول — فرع ' + window.BZ_BRANCH;
                window.bzApplyBranchLabel();                          // sync all chrome to the branch
                setTimeout(window.bzApplyBranchLabel, 500);           // catch late JS-rendered titles
                setTimeout(window.bzApplyBranchLabel, 1500);
                if (j.is_admin) {                               // HQ: admin links + live notifications (bell dropdown + corner toasts)
                    injectAdminLinks();
                    setupNotifications();
                }
                if (document.getElementById('bzBranchWrap')) return;
                var wrap = document.createElement('label');
                wrap.className = 'bz-branch-wrap';
                wrap.id = 'bzBranchWrap';
                if (j.can_switch) {
                    wrap.title = 'الفرع النشط — تبديله يبدّل كل بيانات الموقع';
                    var sel = document.createElement('select');
                    sel.id = 'bzBranchSel';
                    sel.className = 'bz-branch-select';
                    var opts = j.branches.map(function (b) {
                        return '<option value="' + b.id + '"' + (b.id === j.id ? ' selected' : '') + '>🏢 فرع ' + b.name + '</option>';
                    }).join('');
                    if (j.is_admin) opts = '<option value="__all__">🏢 جميع الفروع</option>' + opts;   // HQ shortcut
                    sel.innerHTML = opts;
                    sel.addEventListener('change', function () {
                        if (sel.value === '__all__') { location.href = '/branches'; return; }   // open the all-branches page
                        var id = parseInt(sel.value, 10);
                        var name = sel.options[sel.selectedIndex].text.replace('🏢 فرع ', '');
                        window.bzConfirm('تبديل الفرع إلى «' + name + '»؟\nستظهر بيانات هذا الفرع في كل التبويبات.').then(function (ok) {
                            if (!ok) { sel.value = String(j.id); return; }
                            sel.disabled = true;
                            fetch('/api/branch', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: id }) })
                                .then(function (r) { return r.json(); })
                                .then(function (res) {
                                    if (res && res.success) { location.reload(); }
                                    else { sel.disabled = false; sel.value = String(j.id); if (window.showToast) showToast('تعذّر تبديل الفرع', 'error'); }
                                })
                                .catch(function () { sel.disabled = false; sel.value = String(j.id); });
                        });
                    });
                    wrap.appendChild(sel);
                } else {
                    // branch-locked account: static badge, no switching
                    wrap.title = 'فرعك (مقفل على حسابك)';
                    var badge = document.createElement('span');
                    badge.className = 'bz-branch-badge';
                    badge.textContent = '🏢 فرع ' + window.BZ_BRANCH;
                    wrap.appendChild(badge);
                }
                actions.insertBefore(wrap, actions.firstChild);
            })
            .catch(function () {});
    } catch (e) { /* non-critical */ }
}

function injectAdminLinks() {
    try {
        var items = [
            { href: '/overview', text: 'مركز الفروع', icon: 'building-2', emoji: '🏢' },
            { href: '/branches', text: 'جميع الفروع', icon: 'chart-column', emoji: '📊' },
            { href: '/absher_import', text: 'مزامنة أبشر', icon: 'refresh-cw', emoji: '🔄' }
        ];
        var side = document.querySelector('.bz-sidebar nav');     // الشريط الجانبي هو القائمة الظاهرة فعلياً
        var top = document.querySelector('.bz-topbar .bz-nav');
        items.forEach(function (L) {
            if (side && !side.querySelector('a[href="' + L.href + '"]')) {
                var a = document.createElement('a');
                a.href = L.href;
                a.innerHTML = '<span class="si"><i data-lucide="' + L.icon + '">' + L.emoji + '</i></span><span class="slab">' + L.text + '</span>';
                if (location.pathname === L.href) a.className = 'active';
                side.insertBefore(a, side.firstChild);
            }
            if (top && !top.querySelector('a[href="' + L.href + '"]')) {  // للصفحات بلا shell (احتياطي)
                var b = document.createElement('a');
                b.href = L.href;
                b.textContent = L.emoji + ' ' + L.text;
                if (location.pathname === L.href) b.className = 'active';
                top.insertBefore(b, top.firstChild);
            }
        });
        if (window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
    } catch (e) { /* non-critical */ }
}

// --- Per-tab dated version history: list previous snapshots + restore any with one click ---
function injectTabHistory() {
    try {
        var tab = window.BZ_SNAP_TAB;
        if (!tab) return;                                    // only on data tabs that are snapshotted
        var shell = document.querySelector('.bz-shell');
        if (!shell || document.getElementById('bzHistWrap')) return;

        var wrap = document.createElement('div');
        wrap.id = 'bzHistWrap'; wrap.className = 'bz-hist-wrap';
        var btn = document.createElement('button');
        btn.type = 'button'; btn.className = 'bz-hist-btn';
        btn.innerHTML = '🕓 السجل الزمني — النسخ المؤرّخة';
        var panel = document.createElement('div');
        panel.className = 'bz-hist-panel'; panel.style.display = 'none';
        wrap.appendChild(btn); wrap.appendChild(panel);

        var title = shell.querySelector('.bz-section-title');
        if (title && title.nextSibling) shell.insertBefore(wrap, title.nextSibling);
        else shell.insertBefore(wrap, shell.firstChild);

        var loaded = false;
        btn.addEventListener('click', function () {
            var show = panel.style.display === 'none';
            panel.style.display = show ? 'block' : 'none';
            if (show && !loaded) { loaded = true; loadHist(); }
        });

        function loadHist() {
            panel.innerHTML = '<div class="bz-hist-empty">جارٍ التحميل…</div>';
            fetch('/api/tab_history?tab=' + encodeURIComponent(tab), { headers: { 'Accept': 'application/json' } })
                .then(function (r) { return r.json(); })
                .then(function (j) {
                    var snaps = (j && j.snapshots) || [];
                    if (!snaps.length) { panel.innerHTML = '<div class="bz-hist-empty">لا توجد نسخ محفوظة بعد — تُحفظ نسخة تلقائياً عند كل تعديل.</div>'; return; }
                    panel.innerHTML = '<div class="bz-hist-hd">انقر تاريخاً للرجوع إليه (آخر ' + snaps.length + ' نسخة):</div>' +
                        snaps.map(function (s, i) {
                            return '<button class="bz-hist-item" data-id="' + s.id + '"><span class="t">' + s.ts + '</span>' +
                                (i === 0 ? '<span class="cur">الأحدث</span>' : '<span class="go">↩ رجوع</span>') + '</button>';
                        }).join('');
                    Array.prototype.forEach.call(panel.querySelectorAll('.bz-hist-item'), function (b) {
                        b.addEventListener('click', function () { restoreHist(b.getAttribute('data-id'), b.querySelector('.t').textContent); });
                    });
                })
                .catch(function () { panel.innerHTML = '<div class="bz-hist-empty">تعذّر تحميل السجل.</div>'; });
        }

        function restoreHist(id, ts) {
            window.bzConfirm('الرجوع إلى نسخة ' + ts + '؟\nستحلّ محل البيانات الحالية لهذا التبويب — والحالة الحالية تبقى محفوظة في السجل.').then(function (ok) {
            if (!ok) return;
            fetch('/api/tab_history/restore', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: parseInt(id, 10), tab: tab }) })
                .then(function (r) { return r.json(); })
                .then(function (res) {
                    if (res && res.success) {
                        if (window.showToast) showToast('تمت الاستعادة ✓ — يُعاد التحميل', 'success');
                        setTimeout(function () { location.reload(); }, 600);
                    } else if (window.showToast) showToast('تعذّرت الاستعادة', 'error');
                })
                .catch(function () { if (window.showToast) showToast('تعذّر الاتصال', 'error'); });
            });
        }
    } catch (e) { /* non-critical */ }
}

// --- Lucide icons: replace UI emoji with Lucide line-icons across the whole app ---
// Centralized + DOM-based: only converts emoji rendered in the page (UI), never the emoji
// inside WhatsApp/email/Excel message strings (those are built in JS, not in the DOM).
// Colored status dots (🔴🟢🔵🟠🟡) are intentionally left as-is (they carry color meaning).
var EMOJI_TO_LUCIDE = {
    '🏠': 'house', '🚗': 'car', '🚙': 'car', '🚘': 'car', '🚚': 'truck', '🚛': 'truck',
    '🛒': 'shopping-cart', '📋': 'clipboard-list', '🛢️': 'fuel', '🛢': 'fuel', '🚿': 'droplets',
    '🔧': 'wrench', '🛠️': 'wrench', '🛠': 'wrench', '👥': 'users', '👤': 'user', '🔍': 'search',
    '📁': 'folder', '📂': 'folder-open', '📡': 'satellite-dish', '🛰️': 'satellite', '🛰': 'satellite',
    '📹': 'video', '📷': 'camera', '⚙️': 'settings', '⚙': 'settings', '🏢': 'building-2',
    '📊': 'chart-column', '📈': 'trending-up', '📉': 'trending-down', '🕓': 'history', '🕒': 'clock',
    '🕙': 'clock', '⏰': 'alarm-clock', '🔔': 'bell', '📄': 'file-text', '📝': 'file-pen',
    '✅': 'circle-check', '✔️': 'check', '✔': 'check', '🖨️': 'printer', '🖨': 'printer', '➕': 'plus',
    '🗑️': 'trash-2', '🗑': 'trash-2', '📧': 'mail', '✉️': 'mail', '📨': 'mail', '📩': 'mail',
    '📲': 'smartphone', '📱': 'smartphone', '🔢': 'hash', '📅': 'calendar', '🗓️': 'calendar',
    '🌴': 'tree-palm', '🏖️': 'umbrella', '🏖': 'umbrella', '⚠️': 'triangle-alert', '⚠': 'triangle-alert',
    '🚨': 'siren', '🔒': 'lock', '🔓': 'lock-open', '🔑': 'key', '👁️': 'eye', '👁': 'eye',
    '📍': 'map-pin', '🌙': 'moon', '☀️': 'sun', '↩': 'undo-2', '↪': 'redo-2', '↻': 'refresh-cw',
    '🔄': 'refresh-cw', '🚀': 'rocket', '💾': 'save', '🏷️': 'tag', '💬': 'message-circle',
    '📞': 'phone', '🧾': 'receipt', '📥': 'download', '📤': 'upload', '🖼️': 'image', '👷': 'hard-hat',
    '☰': 'menu', '✕': 'x', '✖': 'x', '×': 'x'
};
var _emTest = null, _emSplit = null;
function _emBuild() {
    var keys = Object.keys(EMOJI_TO_LUCIDE).sort(function (a, b) { return b.length - a.length; })
        .map(function (e) { return e.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
    var src = '(' + keys.join('|') + ')';
    _emTest = new RegExp(src);
    _emSplit = new RegExp(src, 'g');
}
function bzReplaceEmojis(root) {
    if (!_emTest) _emBuild();
    root = root || document.body; if (!root) return;
    var SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, TITLE: 1, OPTION: 1, SELECT: 1, NOSCRIPT: 1, CODE: 1, PRE: 1, INPUT: 1 };
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: function (n) {
            if (!n.nodeValue || !_emTest.test(n.nodeValue)) return NodeFilter.FILTER_REJECT;
            var p = n.parentNode;
            if (!p || !p.nodeName || SKIP[p.nodeName]) return NodeFilter.FILTER_REJECT;
            if (p.closest && p.closest('[data-lucide],.bz-licon')) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
        }
    });
    var nodes = [], n; while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function (node) {
        var val = node.nodeValue, frag = document.createDocumentFragment(), last = 0, m;
        _emSplit.lastIndex = 0;
        while ((m = _emSplit.exec(val))) {
            if (m.index > last) frag.appendChild(document.createTextNode(val.slice(last, m.index)));
            var ic = document.createElement('i');
            ic.setAttribute('data-lucide', EMOJI_TO_LUCIDE[m[1]]);
            ic.className = 'bz-licon';
            ic.textContent = m[1];                 // graceful fallback if the icon name is unknown
            frag.appendChild(ic);
            last = m.index + m[1].length;
        }
        if (last < val.length) frag.appendChild(document.createTextNode(val.slice(last)));
        if (node.parentNode) node.parentNode.replaceChild(frag, node);
    });
    if (window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
}
var _emObs = null, _emT = null;
function _startEmojiObserver() {
    if (_emObs || !window.MutationObserver || !document.body) return;
    _emObs = new MutationObserver(function (muts) {
        // ignore the once-a-second clock tick (it has no emoji) to avoid needless re-walks
        var relevant = muts.some(function (mu) { var t = mu.target; return !(t && t.closest && t.closest('.bz-clockline')); });
        if (!relevant) return;
        clearTimeout(_emT);
        _emT = setTimeout(function () {
            if (!_emObs) return;
            _emObs.disconnect();
            try { bzReplaceEmojis(document.body); } catch (e) { }
            try { window.bzApplyBranchLabel(); } catch (e) { }
            _emObs.observe(document.body, { childList: true, subtree: true });
        }, 300);
    });
    _emObs.observe(document.body, { childList: true, subtree: true });
}
// Make every "فرع الدمام" in the visible chrome follow the active branch (titles, subtitles,
// footers…). Skips data tables, the team section, and form controls so real data is untouched.
window.bzApplyBranchLabel = function () {
    try {
        var b = window.BZ_BRANCH;
        if (!b || b === 'الدمام') return;            // الدمام = النص الأصلي بلا تغيير
        var FIND = 'فرع الدمام', REP = 'فرع ' + b;
        var SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, INPUT: 1, OPTION: 1, SELECT: 1, TITLE: 1, CODE: 1, PRE: 1 };
        var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
            acceptNode: function (n) {
                if (!n.nodeValue || n.nodeValue.indexOf(FIND) === -1) return NodeFilter.FILTER_REJECT;
                var p = n.parentNode;
                if (!p || !p.nodeName || SKIP[p.nodeName]) return NodeFilter.FILTER_REJECT;
                if (p.closest && p.closest('table, #team, .team-section, [contenteditable="true"]')) return NodeFilter.FILTER_REJECT;
                return NodeFilter.FILTER_ACCEPT;
            }
        });
        var nodes = [], n;
        while ((n = walker.nextNode())) nodes.push(n);
        nodes.forEach(function (node) { node.nodeValue = node.nodeValue.split(FIND).join(REP); });
    } catch (e) { /* non-critical */ }
};

function injectLucide() {
    try {
        if (document.getElementById('bzLucideLib')) { bzReplaceEmojis(document.body); _startEmojiObserver(); return; }
        var s = document.createElement('script');
        s.id = 'bzLucideLib';
        s.src = 'https://unpkg.com/lucide@latest';
        s.onload = function () { bzReplaceEmojis(document.body); try { window.bzApplyBranchLabel(); } catch (e) { } _startEmojiObserver(); };
        s.onerror = function () { /* offline: emoji simply remain */ };
        document.head.appendChild(s);
    } catch (e) { /* non-critical */ }
}

// ── Custom popup dialogs (بديل نوافذ المتصفح alert/confirm/prompt) ──────────────
function _bzEscHtml(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; }); }
function _bzDialog(opts) {
    return new Promise(function (resolve) {
        var back = document.createElement('div');
        back.className = 'bz-dialog-back';
        var msgHtml = _bzEscHtml(opts.msg).replace(/\n/g, '<br>');
        var h = '<div class="bz-dialog"><div class="bz-dialog-msg">' + msgHtml + '</div>';
        if (opts.prompt) h += '<input class="bz-dialog-input" type="' + (opts.password ? 'password' : 'text') + '" value="' + _bzEscHtml(opts.def || '') + '">';
        h += '<div class="bz-dialog-acts">';
        if (opts.cancel) h += '<button class="bz-dlg-btn cancel" type="button">' + _bzEscHtml(opts.cancelText || 'إلغاء') + '</button>';
        h += '<button class="bz-dlg-btn ok" type="button">' + _bzEscHtml(opts.okText || 'موافق') + '</button></div></div>';
        back.innerHTML = h;
        document.body.appendChild(back);
        requestAnimationFrame(function () { back.classList.add('show'); });
        var box = back.querySelector('.bz-dialog');
        var inp = back.querySelector('.bz-dialog-input');
        if (inp) setTimeout(function () { inp.focus(); inp.select && inp.select(); }, 60);
        function done(val) { back.classList.remove('show'); setTimeout(function () { if (back.parentNode) back.remove(); }, 200); document.removeEventListener('keydown', onKey); resolve(val); }
        back.querySelector('.bz-dlg-btn.ok').addEventListener('click', function () { done(opts.prompt ? (inp ? inp.value : '') : true); });
        var cx = back.querySelector('.bz-dlg-btn.cancel'); if (cx) cx.addEventListener('click', function () { done(opts.prompt ? null : false); });
        back.addEventListener('click', function (e) { if (e.target === back && opts.cancel) done(opts.prompt ? null : false); });
        function onKey(e) {
            if (e.key === 'Escape' && opts.cancel) done(opts.prompt ? null : false);
            else if (e.key === 'Enter') done(opts.prompt ? (inp ? inp.value : '') : true);
        }
        document.addEventListener('keydown', onKey);
        if (box && window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
    });
}
window.bzAlert = function (msg, opts) { opts = opts || {}; return _bzDialog({ msg: msg, cancel: false, okText: opts.okText }); };
window.bzConfirm = function (msg, opts) { opts = opts || {}; return _bzDialog({ msg: msg, cancel: true, okText: opts.okText || 'تأكيد', cancelText: opts.cancelText }); };
window.bzPrompt = function (msg, def, opts) { opts = opts || {}; return _bzDialog({ msg: msg, prompt: true, def: def, cancel: true, password: opts.password }); };
// استبدال alert الأصلي بنافذة منبثقة مخصّصة (لا حاجة لقيمة إرجاع)
try { window.alert = function (m) { window.bzAlert(m); }; } catch (e) { }

// ── إشعارات حيّة للمدير: نوافذ منبثقة في الزاوية + قائمة منسدلة على الجرس ──────────
function setupNotifications() {
    if (window._bzNotiSetup) return; window._bzNotiSetup = true;
    var TKEY = 'bz_noti_toasted', OKEY = 'bz_noti_lastopen';
    function getToasted() { try { return JSON.parse(localStorage.getItem(TKEY) || '[]'); } catch (e) { return []; } }
    function setToasted(a) { try { localStorage.setItem(TKEY, JSON.stringify(a.slice(-800))); } catch (e) { } }
    function lastOpen() { return localStorage.getItem(OKEY) || ''; }
    function setLastOpen(v) { try { localStorage.setItem(OKEY, v); } catch (e) { } }
    function nowStr() { var d = new Date(); function p(n) { return (n < 10 ? '0' : '') + n; } return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()) + ':' + p(d.getSeconds()); }
    function esc(s) { return _bzEscHtml(s); }

    var toasts = document.createElement('div'); toasts.className = 'bz-toasts'; document.body.appendChild(toasts);
    var menu = document.createElement('div'); menu.className = 'bz-noti-menu';
    menu.innerHTML = '<div class="bz-noti-hd"><span>🔔 الإشعارات</span><button class="bz-noti-clear" type="button">تعليم الكل كمقروء</button></div><div class="bz-noti-list"></div>';
    document.body.appendChild(menu);
    var listEl = menu.querySelector('.bz-noti-list');
    var bell = document.getElementById('bzBell');
    var lastItems = [];

    function badge(n) {
        if (!bell) return;
        bell.innerHTML = '🔔' + (n > 0 ? '<span class="badge-dot">' + (n > 99 ? '99+' : n) + '</span>' : '');
        if (window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
    }
    function renderMenu(items) {
        if (!items.length) { listEl.innerHTML = '<div class="bz-noti-empty">لا توجد إشعارات</div>'; return; }
        var lo = lastOpen();
        listEl.innerHTML = items.slice(0, 50).map(function (it) {
            return '<div class="bz-noti-item' + (it.ts > lo ? ' unread' : '') + '"><span class="ic">' + (it.icon || '🔔') +
                '</span><div class="tx"><div class="tt">' + esc(it.title) + '</div><div class="mt">🏢 فرع ' + esc(it.branch) +
                (it.user ? ' · 👤 ' + esc(it.user) : '') + ' · ' + esc(it.ts) + '</div></div></div>';
        }).join('');
        if (window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
    }
    function toast(it) {
        var el = document.createElement('div'); el.className = 'bz-toast ' + (it.kind || '');
        el.innerHTML = '<span class="ic">' + (it.icon || '🔔') + '</span><div class="tx"><div class="tt">' + esc(it.title) +
            '</div><div class="mt">🏢 فرع ' + esc(it.branch) + (it.user ? ' · 👤 ' + esc(it.user) : '') + '</div></div>';
        toasts.appendChild(el);
        if (window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
        setTimeout(function () { el.classList.add('out'); setTimeout(function () { if (el.parentNode) el.remove(); }, 420); }, 7000);
    }
    function toggle() {
        var open = menu.classList.toggle('open');
        if (open) { setLastOpen(nowStr()); badge(0); renderMenu(lastItems); }
    }
    if (bell) { bell.removeAttribute('href'); bell.style.cursor = 'pointer'; bell.title = 'الإشعارات'; bell.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); toggle(); }); }
    menu.querySelector('.bz-noti-clear').addEventListener('click', function () { setLastOpen(nowStr()); badge(0); renderMenu(lastItems); });
    document.addEventListener('click', function (e) { if (menu.classList.contains('open') && !menu.contains(e.target) && !(bell && bell.contains(e.target))) menu.classList.remove('open'); });

    function load(first) {
        fetch('/api/notifications', { headers: { 'Accept': 'application/json' } })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (j) {
                if (!j || !j.success) return;
                lastItems = j.items || [];
                var toasted = getToasted(), tset = {}; toasted.forEach(function (k) { tset[k] = 1; });
                if (first) {
                    lastItems.forEach(function (it) { if (!tset[it.key]) { tset[it.key] = 1; toasted.push(it.key); } });   // baseline — no burst
                } else {
                    lastItems.slice().reverse().forEach(function (it) { if (!tset[it.key]) { tset[it.key] = 1; toasted.push(it.key); toast(it); } });
                }
                setToasted(toasted);
                var lo = lastOpen();
                badge(lastItems.filter(function (it) { return it.ts > lo; }).length);
                if (menu.classList.contains('open')) renderMenu(lastItems);
            }).catch(function () { });
    }
    load(true);
    setInterval(function () { load(false); }, 20000);
}

// --- PWA: manifest + theme color + service worker (تثبيت كتطبيق + عمل دون اتصال) ---
function registerPWA() {
    try {
        if (!document.querySelector('link[rel="manifest"]')) {
            var l = document.createElement('link');
            l.rel = 'manifest'; l.href = '/static/manifest.json';
            document.head.appendChild(l);
        }
        if (!document.querySelector('meta[name="theme-color"]')) {
            var m = document.createElement('meta');
            m.name = 'theme-color'; m.content = '#0C2340';
            document.head.appendChild(m);
        }
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function () {
                navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
            });
        }
    } catch (e) {}
}

// --- Workstation namespace (/importantworkstation/*) ---
// A separate, open mirror of the site under a URL prefix. Detected purely by the path,
// so the MAIN site is never affected. Internal links and /api calls are kept under the
// prefix; the Employees/GPS-Sync/Cameras tabs show a 🔒 until unlocked.
const WS_PREFIX = '/importantworkstation';
function inWorkstation() { return window.location.pathname.indexOf(WS_PREFIX) === 0; }
function getCookie(name) {
    const m = document.cookie.match('(?:^|; )' + name + '=([^;]*)');
    return m ? decodeURIComponent(m[1]) : '';
}
// Inject the "الحوادث والمخالفات" tab into every top-bar nav from one place, so the link
// stays consistent site-wide without editing each template. Runs BEFORE the workstation
// rewrite so its href is prefixed automatically inside /importantworkstation. Additive only —
// the main site is unaffected apart from gaining this link.
function injectGlobalNavLinks() {
    const nav = document.querySelector('.bz-topbar .bz-nav');
    if (!nav) return;
    function addLink(href, text, afterSel) {
        if (nav.querySelector('a[href$="' + href + '"]')) return; // already present
        const a = document.createElement('a');
        a.setAttribute('href', href);
        a.textContent = text;
        const after = afterSel ? nav.querySelector(afterSel) : null;
        if (after && after.nextSibling) nav.insertBefore(a, after.nextSibling);
        else nav.appendChild(a);
    }
    addLink('/incidents', '🚨 الحوادث والمخالفات', 'a[href$="/records"]');
    addLink('/handover', '🚗 تسليم واستلام مركبة', 'a[href$="/"]');
    addLink('/settings', '⚙️ الإعدادات', 'a[href$="/cameras"]');
    // (no separate "الفاتورة" link — the homepage "الرئيسية" IS the invoice; /invoice aliases to it)
}

// Floating contact dock (WhatsApp + Email), bottom-left, on EVERY tab.
// Skips if the page already provides its own dock (e.g. the homepage).
function injectContactDock() {
    try {
        if (document.querySelector('.bz-dock')) return;
        const dock = document.createElement('div');
        dock.className = 'bz-dock';
        dock.setAttribute('aria-label', 'إجراءات سريعة');
        dock.innerHTML =
            '<a class="bz-dock-btn wa" href="https://wa.me/966570310909?text=مرحباً" target="_blank" rel="noopener" data-label="واتساب" title="تواصل عبر واتساب" aria-label="واتساب">💬</a>' +
            '<a class="bz-dock-btn mail" href="mailto:damfleet@bz.sa" data-label="إرسال بالإيميل" title="إرسال عبر الإيميل" aria-label="إرسال عبر الإيميل">📧</a>';
        document.body.appendChild(dock);
    } catch (e) { /* non-critical */ }
}

// Big company logo at the top of EVERY content tab (skips pages that already show one).
function injectHeroLogo() {
    try {
        const shell = document.querySelector('.bz-shell');
        if (!shell) return;
        if (document.querySelector('.bz-hero-logo, .logo, .ho-head, .site-logo')) return;
        const div = document.createElement('div');
        div.className = 'bz-hero-logo';
        div.innerHTML = '<img src="/static/main_logo_v2.jpg" alt="شركة بن زومة">';
        shell.insertBefore(div, shell.firstChild);
    } catch (e) { /* non-critical */ }
}

// Live date/time line at the very top of every content tab (same format site-wide).
function injectClock() {
    try {
        const shell = document.querySelector('.bz-shell');
        if (!shell || document.querySelector('.bz-clockline')) return;
        const line = document.createElement('div');
        line.className = 'bz-clockline';
        shell.insertBefore(line, shell.firstChild);
        function weekNo(d) { var t = new Date(d); t.setHours(0, 0, 0, 0); t.setDate(t.getDate() + 3 - ((t.getDay() + 6) % 7)); var w1 = new Date(t.getFullYear(), 0, 4); return 1 + Math.round(((t - w1) / 86400000 - 3 + ((w1.getDay() + 6) % 7)) / 7); }
        function tick() {
            const n = new Date();
            line.innerHTML = 'التاريخ: <b>' + n.toLocaleDateString('ar-EG', { dateStyle: 'medium' }) +
                '</b> · الوقت: <b>' + n.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
                '</b> · الأسبوع <b>' + weekNo(n) + '</b>';
        }
        tick(); setInterval(tick, 1000);
    } catch (e) { /* non-critical */ }
}

// ===== Enterprise unified shell (deep-dark + right sidebar + rich topbar) =====
// Built from one place so every tab gets the same chrome. The sidebar is CLONED from
// the page's existing horizontal nav (so links + active state + workstation prefix/lock
// all stay correct). Defensive: only runs on pages that have a .bz-topbar (skips the
// dashboard — it has its own shell — plus login/lock pages). Adds NO fabricated data.
function buildEnterpriseShell() {
    try {
        const topbar = document.querySelector('.bz-topbar');
        if (!topbar) return;                               // dashboard / login / tab_lock → skip
        if (document.querySelector('.bz-sidebar')) return; // already built (defensive)

        document.body.classList.add('bz-enterprise');

        // ---- sidebar (cloned from the horizontal nav) ----
        let navHtml = '';
        topbar.querySelectorAll('.bz-nav a').forEach(a => {
            const txt = (a.textContent || '').trim();
            const sp = txt.indexOf(' ');
            const icon = sp > 0 ? txt.slice(0, sp) : '•';
            const label = sp > 0 ? txt.slice(sp + 1).trim() : txt;
            const cls = a.classList.contains('active') ? ' class="active"' : '';
            navHtml += `<a href="${a.getAttribute('href')}"${cls}><span class="si">${icon}</span><span class="slab">${escapeHtml(label)}</span></a>`;
        });
        const aside = document.createElement('aside');
        aside.className = 'bz-sidebar';
        aside.innerHTML =
            '<div class="side-brand"><img src="/static/nav_logo.png" alt="BIN ZOMAH"><div class="brand-text"><b>BIN ZOMAH INTL.</b><span>نظام إدارة الأسطول والتوثيق</span></div></div>' +
            '<nav>' + navHtml + '</nav>';
        document.body.appendChild(aside);

        // ---- mobile drawer: dim backdrop + a clear close button + easy dismiss ----
        let backdrop = document.querySelector('.bz-side-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'bz-side-backdrop';
            document.body.appendChild(backdrop);
        }
        const isMobileNav = () => window.matchMedia('(max-width: 1024px)').matches;
        function bzSetDrawer(open) {
            aside.classList.toggle('open', open);
            backdrop.classList.toggle('show', open);
            document.body.classList.toggle('bz-drawer-open', open);
        }
        window.bzCloseDrawer = function () { bzSetDrawer(false); };
        backdrop.addEventListener('click', () => bzSetDrawer(false));
        document.addEventListener('keydown', (e) => { if (e.key === 'Escape') bzSetDrawer(false); });
        aside.querySelectorAll('nav a').forEach(a => a.addEventListener('click', () => { if (isMobileNav()) bzSetDrawer(false); }));
        const sideClose = document.createElement('button');
        sideClose.type = 'button'; sideClose.className = 'bz-side-close'; sideClose.title = 'إغلاق';
        sideClose.setAttribute('aria-label', 'إغلاق القائمة'); sideClose.textContent = '✕';
        sideClose.addEventListener('click', () => bzSetDrawer(false));
        const sBrand = aside.querySelector('.side-brand'); if (sBrand) sBrand.appendChild(sideClose);

        // ---- enrich the topbar ----
        const actions = topbar.querySelector('.bz-actions');
        const brand = topbar.querySelector('.bz-brand');

        if (brand && !document.getElementById('bzBurger')) {
            const burger = document.createElement('button');
            burger.id = 'bzBurger'; burger.type = 'button'; burger.className = 'bz-icon-btn bz-side-burger';
            burger.title = 'القائمة'; burger.setAttribute('aria-label', 'القائمة'); burger.textContent = '☰';
            burger.addEventListener('click', () => {
                if (isMobileNav()) bzSetDrawer(!aside.classList.contains('open'));   // mobile: slide-in drawer + backdrop
                else document.body.classList.toggle('side-hidden');                  // desktop: hide/show the sidebar
            });
            brand.parentNode.insertBefore(burger, brand);
        }

        if (!document.getElementById('bzTopSearch')) {
            const sw = document.createElement('div');
            sw.className = 'bz-top-search';
            sw.innerHTML = '<span class="si">🔍</span><input id="bzTopSearch" type="text" placeholder="بحث سريع في هذه الصفحة…">';
            topbar.insertBefore(sw, actions || null);
            document.getElementById('bzTopSearch').addEventListener('input', function () { bzQuickFilter(this.value); });
        }

        if (actions) {
            if (!document.getElementById('bzBell')) {
                const bell = document.createElement('a');
                bell.id = 'bzBell'; bell.className = 'bz-top-ico'; bell.href = '/dashboard#alerts';
                bell.title = 'تنبيهات الوثائق'; bell.textContent = '🔔';
                actions.insertBefore(bell, actions.firstChild);
            }
            if (!document.getElementById('bzUser')) {
                const user = document.createElement('div');
                user.id = 'bzUser'; user.className = 'bz-top-user';
                user.innerHTML = '<div class="u-meta"><b id="bzUserName">—</b><span>إدارة الأسطول</span></div><div class="u-av" id="bzUserAv">BZ</div>';
                actions.appendChild(user);
            }
        }

        // fill the user chip + alerts badge from REAL data only (best-effort; no fabrication)
        fetch('/api/whoami', { headers: { 'Accept': 'application/json' } })
            .then(r => r.ok ? r.json() : null)
            .then(j => {
                if (!j) return;
                const nm = document.getElementById('bzUserName'); if (nm && j.name) nm.textContent = j.name;
                const av = document.getElementById('bzUserAv'); if (av && j.name) av.textContent = ((j.name.trim()[0]) || 'B');
            }).catch(() => {});
        fetch('/api/expiry_alerts_preview', { headers: { 'Accept': 'application/json' } })
            .then(r => r.ok ? r.json() : null)
            .then(j => {
                const bell = document.getElementById('bzBell');
                if (j && bell && j.total > 0) bell.innerHTML = '🔔<span class="badge-dot">' + (j.total > 99 ? '99+' : j.total) + '</span>';
            }).catch(() => {});
    } catch (e) { console.error('enterprise shell error', e); }
}

// Top-bar quick search: forward into the page's own search box when present (keeps its
// filtering/counters correct); otherwise generically hide non-matching rows of the
// largest table (checks both text cells and input/select values).
function bzQuickFilter(q) {
    const known = ['empSearch', 'searchInput', 'assetSearch', 'seInput'];
    for (const id of known) {
        const el = document.getElementById(id);
        if (el) { el.value = q; el.dispatchEvent(new Event('input', { bubbles: true })); return; }
    }
    const term = (q || '').trim().toLowerCase();
    let best = null, bestN = -1;
    document.querySelectorAll('table').forEach(t => {
        const n = t.querySelectorAll('tbody tr').length;
        if (n > bestN) { bestN = n; best = t; }
    });
    if (!best) return;
    best.querySelectorAll('tbody tr').forEach(tr => {
        if (!term) { tr.style.display = ''; return; }
        let hit = (tr.textContent || '').toLowerCase().indexOf(term) !== -1;
        if (!hit) {
            const f = tr.querySelectorAll('input,textarea,select');
            for (let i = 0; i < f.length; i++) { if ((f[i].value || '').toLowerCase().indexOf(term) !== -1) { hit = true; break; } }
        }
        tr.style.display = hit ? '' : 'none';
    });
}

function applyWorkstationRestrictions() {
    if (!inWorkstation()) return; // MAIN SITE: do nothing at all
    // 1) keep every internal nav link inside the workstation prefix
    document.querySelectorAll('a[href^="/"]').forEach(a => {
        const h = a.getAttribute('href');
        if (!h || h.indexOf(WS_PREFIX) === 0) return;
        if (h === '/logout' || h.indexOf('/static') === 0 || h.indexOf('/api') === 0 || h.indexOf('//') === 0) return;
        a.setAttribute('href', WS_PREFIX + (h === '/' ? '' : h));
    });
    // 3) inject a workstation-only "clear all data" button so the user can wipe the
    //    sandbox to a truly empty start (removes any leftover id=2 data from earlier use).
    const actions = document.querySelector('.bz-topbar .bz-actions');
    if (actions && !document.getElementById('wsResetBtn')) {
        const btn = document.createElement('button');
        btn.id = 'wsResetBtn';
        btn.type = 'button';
        btn.className = 'bz-icon-btn';
        btn.title = 'تفريغ كل بيانات محطة العمل (بداية فارغة) — لا يؤثر على الموقع الأساسي';
        btn.textContent = '🗑️';
        btn.style.cssText = 'background:rgba(220,38,38,.18);border-color:rgba(220,38,38,.45);';
        btn.addEventListener('click', window.bzResetWorkstation);
        actions.insertBefore(btn, actions.firstChild);
        // "fill example data" button next to it
        const seedBtn = document.createElement('button');
        seedBtn.id = 'wsSeedBtn';
        seedBtn.type = 'button';
        seedBtn.className = 'bz-icon-btn';
        seedBtn.title = 'تعبئة كل التبويبات ببيانات أمثلة — لا يؤثر على الموقع الأساسي';
        seedBtn.textContent = '🧪';
        seedBtn.style.cssText = 'background:rgba(201,162,39,.20);border-color:rgba(201,162,39,.5);';
        seedBtn.addEventListener('click', window.bzSeedWorkstation);
        actions.insertBefore(seedBtn, actions.firstChild);
    }
    // 2) lock the sensitive tabs until unlocked
    if (getCookie('ws_unlocked') === '1') return;
    [WS_PREFIX + '/employees', WS_PREFIX + '/gps_sync', WS_PREFIX + '/cameras', WS_PREFIX + '/tracking'].forEach(p => {
        document.querySelectorAll('a[href="' + p + '"]').forEach(a => {
            if (a.textContent.indexOf('🔒') === -1) {
                a.textContent = '🔒 ' + a.textContent.trim();
                a.title = 'مقفل — يتطلب كلمة مرور';
            }
        });
    });
}

// Wipe every workstation (id=2) store + this browser's ws: cache, then reload empty.
// Workstation-only; the main site never sees this button or endpoint.
window.bzResetWorkstation = async function () {
    if (!inWorkstation()) return;
    if (!(await window.bzConfirm('تفريغ كل بيانات محطة العمل؟\n\nسيُحذف كل ما أُدخل في هذا الرابط (الموظفون، الجدول، الغسيل، السائقون، الزيوت، الورشة، طلب الشراء، السجلات) ويبدأ فارغاً.\n\nالموقع الأساسي لن يتأثر إطلاقاً.'))) return;
    try {
        // '/api/ws_reset' is rewritten to /importantworkstation/api/ws_reset by the fetch wrapper.
        await fetch('/api/ws_reset', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    } catch (e) { /* best-effort */ }
    // Also drop this browser's ws:-prefixed cached copies (bypass the patched instance methods).
    try {
        for (let i = localStorage.length - 1; i >= 0; i--) {
            const k = localStorage.key(i);
            if (k && k.indexOf('ws:') === 0) Storage.prototype.removeItem.call(localStorage, k);
        }
    } catch (e) { /* ignore */ }
    window.location.reload();
};

// Fill every workstation tab with realistic FAKE example data (demo), then reload.
// Workstation-only; the main site never sees this button or endpoint.
window.bzSeedWorkstation = async function () {
    if (!inWorkstation()) return;
    if (!(await window.bzConfirm('تعبئة كل تبويبات محطة العمل ببيانات أمثلة؟'))) return;
    try {
        await fetch('/api/ws_seed', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
    } catch (e) { /* best-effort */ }
    // Drop local ws: caches so the freshly-seeded server data shows on reload.
    try {
        for (let i = localStorage.length - 1; i >= 0; i--) {
            const k = localStorage.key(i);
            if (k && k.indexOf('ws:') === 0) Storage.prototype.removeItem.call(localStorage, k);
        }
    } catch (e) { /* ignore */ }
    window.location.reload();
};

// --- Theme Management ---
function initThemeToggle() {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') {
        document.body.classList.add('dark-mode');
        updateToggleButtons(true);
    } else {
        document.body.classList.remove('dark-mode');
        updateToggleButtons(false);
    }
}

window.toggleDarkMode = function() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    updateToggleButtons(isDark);
};

function updateToggleButtons(isDark) {
    document.querySelectorAll('#darkModeToggle').forEach(btn => {
        btn.innerHTML = isDark ? '☀️' : '🌙';
        btn.style.display = 'flex'; // Ensure it's visible
        
        // Dynamic styling for the button
        if (isDark) {
            btn.style.background = 'rgba(255, 255, 255, 0.1)';
            btn.style.color = '#fff';
            btn.style.border = '1px solid rgba(255, 255, 255, 0.2)';
        } else {
            btn.style.background = 'rgba(15, 23, 42, 0.05)';
            btn.style.color = '#0f172a';
            btn.style.border = '1px solid rgba(15, 23, 42, 0.1)';
        }
    });
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
    const publicPaths = ['/login'];
    if (publicPaths.some(p => path.startsWith(p))) return;

    // Reset timer on any user interaction
    ['mousemove', 'keydown', 'click', 'scroll', 'touchstart', 'touchmove'].forEach(evt => {
        document.addEventListener(evt, window.resetIdleTimer, { passive: true });
    });

    // Kick off the idle timer
    window.resetIdleTimer();
}

// =============================================================================
// BILINGUAL TRANSLATION SYSTEM
// =============================================================================
let translationObserver = null;

function initLanguageTranslation() {
    applyEnglishStyles();
    
    // Auto-inject translation button
    injectLanguageToggle();

    // Fetch and apply saved language
    const currentLang = localStorage.getItem('lang') || 'ar';
    setLanguage(currentLang);
}

window.toggleLanguage = function() {
    const currentLang = localStorage.getItem('lang') || 'ar';
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    localStorage.setItem('lang', newLang);
    setLanguage(newLang);
};

function setLanguage(lang) {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    
    // Update language toggle text
    const langBtn = document.getElementById('languageToggleBtn');
    if (langBtn) {
        langBtn.innerHTML = lang === 'ar' ? '🇬🇧' : '🇸🇦';
        langBtn.title = lang === 'ar' ? 'Switch to English' : 'التحويل للعربية';
    }

    // Perform static translation
    translateDOM(lang);

    // Set up MutationObserver to translate dynamically added elements
    startTranslationObserver(lang);
}

function translateDOM(lang) {
    const dict = translations[lang] || {};
    
    function walk(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const trimmed = node.nodeValue.trim();
            if (trimmed) {
                if (dict[trimmed]) {
                    if (!node.parentElement.hasAttribute('data-orig-text')) {
                        node.parentElement.setAttribute('data-orig-text', trimmed);
                    }
                    node.nodeValue = node.nodeValue.replace(trimmed, dict[trimmed]);
                } else if (lang === 'ar' && node.parentElement.hasAttribute('data-orig-text')) {
                    const orig = node.parentElement.getAttribute('data-orig-text');
                    node.nodeValue = node.nodeValue.replace(trimmed, orig);
                }
            }
        } else if (node.nodeType === Node.ELEMENT_NODE) {
            // Placeholder translation
            if (node.placeholder) {
                const trimmedPlaceholder = node.placeholder.trim();
                if (dict[trimmedPlaceholder]) {
                    if (!node.hasAttribute('data-orig-placeholder')) {
                        node.setAttribute('data-orig-placeholder', trimmedPlaceholder);
                    }
                    node.placeholder = dict[trimmedPlaceholder];
                } else if (lang === 'ar' && node.hasAttribute('data-orig-placeholder')) {
                    node.placeholder = node.getAttribute('data-orig-placeholder');
                }
            }
            
            // Title translation
            if (node.title) {
                const trimmedTitle = node.title.trim();
                if (dict[trimmedTitle]) {
                    if (!node.hasAttribute('data-orig-title')) {
                        node.setAttribute('data-orig-title', trimmedTitle);
                    }
                    node.title = dict[trimmedTitle];
                } else if (lang === 'ar' && node.hasAttribute('data-orig-title')) {
                    node.title = node.getAttribute('data-orig-title');
                }
            }

            // Select elements special handling
            if (node.tagName === 'SELECT') {
                Array.from(node.options).forEach(opt => {
                    const trimmedOpt = opt.textContent.trim();
                    if (dict[trimmedOpt]) {
                        if (!opt.hasAttribute('data-orig-text')) {
                            opt.setAttribute('data-orig-text', trimmedOpt);
                        }
                        opt.textContent = dict[trimmedOpt];
                    } else if (lang === 'ar' && opt.hasAttribute('data-orig-text')) {
                        opt.textContent = opt.getAttribute('data-orig-text');
                    }
                });
            }

            if (!['SCRIPT', 'STYLE', 'VIDEO', 'SOURCE'].includes(node.tagName)) {
                for (let i = 0; i < node.childNodes.length; i++) {
                    walk(node.childNodes[i]);
                }
            }
        }
    }
    
    walk(document.body);
    
    // Page Title
    const docTitle = document.title.trim();
    if (dict[docTitle]) {
        if (!document.documentElement.hasAttribute('data-orig-title')) {
            document.documentElement.setAttribute('data-orig-title', docTitle);
        }
        document.title = dict[docTitle];
    } else if (lang === 'ar' && document.documentElement.hasAttribute('data-orig-title')) {
        document.title = document.documentElement.getAttribute('data-orig-title');
    }
}

function startTranslationObserver(lang) {
    if (translationObserver) translationObserver.disconnect();
    
    translationObserver = new MutationObserver((mutations) => {
        translationObserver.disconnect();
        
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                translateSubtree(node, lang);
            });
            if (mutation.type === 'characterData') {
                translateSubtree(mutation.target, lang);
            }
        });
        
        translationObserver.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });
    });
    
    translationObserver.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true
    });
}

function translateSubtree(node, lang) {
    const dict = translations[lang] || {};
    
    if (node.nodeType === Node.TEXT_NODE) {
        const trimmed = node.nodeValue.trim();
        if (trimmed && dict[trimmed]) {
            if (!node.parentElement.hasAttribute('data-orig-text')) {
                node.parentElement.setAttribute('data-orig-text', trimmed);
            }
            node.nodeValue = node.nodeValue.replace(trimmed, dict[trimmed]);
        }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
        if (node.placeholder && dict[node.placeholder.trim()]) {
            const tr = node.placeholder.trim();
            node.setAttribute('data-orig-placeholder', tr);
            node.placeholder = dict[tr];
        }
        
        if (node.title && dict[node.title.trim()]) {
            const tr = node.title.trim();
            node.setAttribute('data-orig-title', tr);
            node.title = dict[tr];
        }

        if (node.tagName === 'SELECT') {
            Array.from(node.options).forEach(opt => {
                const trimmedOpt = opt.textContent.trim();
                if (dict[trimmedOpt]) {
                    opt.setAttribute('data-orig-text', trimmedOpt);
                    opt.textContent = dict[trimmedOpt];
                }
            });
        }

        if (!['SCRIPT', 'STYLE', 'VIDEO', 'SOURCE'].includes(node.tagName)) {
            node.childNodes.forEach(child => translateSubtree(child, lang));
        }
    }
}

function injectLanguageToggle() {
    if (document.getElementById('languageToggleBtn')) return;

    const darkToggle = document.getElementById('darkModeToggle') || document.getElementById('empDarkModeToggle');
    const langBtn = document.createElement('button');
    langBtn.id = 'languageToggleBtn';
    langBtn.onclick = window.toggleLanguage;
    
    // Unified Styling
    langBtn.style.cursor = 'pointer';
    langBtn.style.border = 'none';
    langBtn.style.borderRadius = '50%';
    langBtn.style.width = '45px';
    langBtn.style.height = '45px';
    langBtn.style.display = 'flex';
    langBtn.style.alignItems = 'center';
    langBtn.style.justifyContent = 'center';
    langBtn.style.fontSize = '1.3rem';
    langBtn.style.transition = 'var(--trans-spring, 0.3s)';
    langBtn.style.boxShadow = 'var(--shadow-sm, 0 4px 15px rgba(0,0,0,0.1))';
    langBtn.style.backdropFilter = 'blur(5px)';
    langBtn.style.zIndex = '1001';

    if (darkToggle) {
        const style = window.getComputedStyle(darkToggle);
        if (style.position === 'absolute' || style.position === 'fixed') {
            langBtn.style.position = style.position;
            langBtn.style.top = style.top;
            
            // Adjust coordinates based on design systems
            const currentRight = parseFloat(style.right);
            const currentLeft = parseFloat(style.left);
            if (!isNaN(currentRight)) {
                langBtn.style.right = (currentRight + 55) + 'px';
            } else if (!isNaN(currentLeft)) {
                langBtn.style.left = (currentLeft + 55) + 'px';
            } else {
                langBtn.style.right = '75px';
            }
        } else {
            // Inline alignment (e.g. employee top bar)
            langBtn.style.margin = '0 10px';
        }
        
        const currentLang = localStorage.getItem('lang') || 'ar';
        langBtn.innerHTML = currentLang === 'ar' ? '🇬🇧' : '🇸🇦';
        darkToggle.parentNode.insertBefore(langBtn, darkToggle.nextSibling);
    } else {
        // Floating fallback
        langBtn.style.position = 'fixed';
        langBtn.style.top = '15px';
        langBtn.style.right = '75px';
        
        const currentLang = localStorage.getItem('lang') || 'ar';
        langBtn.innerHTML = currentLang === 'ar' ? '🇬🇧' : '🇸🇦';
        document.body.appendChild(langBtn);
    }
}

function applyEnglishStyles() {
    let styleEl = document.getElementById('en-layout-styles');
    if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = 'en-layout-styles';
        styleEl.innerHTML = `
            html[lang="en"] body {
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
            }
            html[lang="en"] .card label {
                text-align: left !important;
            }
            html[lang="en"] input, html[lang="en"] select, html[lang="en"] textarea {
                text-align: left !important;
            }
            html[lang="en"] .excel-table input, html[lang="en"] .excel-table td input {
                text-align: center !important; /* Keep center alignment for tables */
            }
            html[lang="en"] .nav-links {
                flex-direction: row;
            }
            html[lang="en"] #languageToggleBtn:hover {
                transform: scale(1.1) rotate(10deg);
            }
            html[lang="en"] .user-badge {
                left: 1.5rem !important;
                right: auto !important;
            }
            html[lang="en"] .btn-delete {
                margin-left: 5px;
            }
        `;
        document.head.appendChild(styleEl);
    }
}

// ===== WhatsApp Floating Bubble Injection =====
window.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('wa-floating-btn')) return;
    var waBtn = document.createElement('a');
    waBtn.id = 'wa-floating-btn';
    waBtn.href = 'https://wa.me/?text=' + encodeURIComponent('مرحباً فريق الدعم');
    waBtn.target = '_blank';
    waBtn.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.888-.788-1.489-1.761-1.662-2.06-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>';
    var span = document.createElement('span');
    span.textContent = window.i18n ? window.i18n("واتساب") || 'واتساب' : 'واتساب';
    span.style.fontFamily = 'Cairo, system-ui, sans-serif';
    span.style.fontWeight = '700';
    span.style.fontSize = '14px';
    span.style.lineHeight = '1';
    waBtn.appendChild(span);
    
    // Styling
    waBtn.style.position = 'fixed';
    waBtn.style.bottom = '25px';
    waBtn.style.right = '25px';
    waBtn.style.zIndex = '99999';
    waBtn.style.backgroundColor = '#25D366';
    waBtn.style.color = '#fff';
    waBtn.style.borderRadius = '50px';
    waBtn.style.padding = '12px 20px';
    waBtn.style.boxShadow = '0 4px 14px rgba(37,211,102,0.4)';
    waBtn.style.textDecoration = 'none';
    waBtn.style.display = 'flex';
    waBtn.style.alignItems = 'center';
    waBtn.style.gap = '8px';
    waBtn.style.transition = 'all 0.3s ease';
    waBtn.style.border = '2px solid transparent'; // Fix for dark mode borders
    
    waBtn.onmouseover = function() { 
        this.style.transform = 'translateY(-4px)'; 
        this.style.boxShadow = '0 6px 20px rgba(37,211,102,0.6)'; 
    };
    waBtn.onmouseout = function() { 
        this.style.transform = 'none'; 
        this.style.boxShadow = '0 4px 14px rgba(37,211,102,0.4)'; 
    };
    
    document.body.appendChild(waBtn);
});
