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
        "الاستحقاقات السنوية": "Annual Entitlements",

        // Navigation (with emoji, as rendered in the top bar)
        "🏠 الرئيسية": "🏠 Home",
        "🛒 طلب شراء": "🛒 Purchase",
        "📋 الجدول الأسبوعي": "📋 Weekly Schedule",
        "🛢️ الزيوت والفلاتر": "🛢️ Oils & Filters",
        "🚿 الغسيل": "🚿 Washing",
        "🔧 الورشة": "🔧 Workshop",
        "👥 الموظفين": "👥 Employees",
        "🔍 بحث": "🔍 Search",
        "📁 التوثيق": "📁 Records",
        "📡 مزامنة GPS": "📡 GPS Sync",
        "🛰️ التتبع": "🛰️ Tracking",
        "📹 الكاميرات": "📹 Cameras",
        "📹 الكاميرات المباشرة — Hik-Connect": "📹 Live Cameras — Hik-Connect",
        "فتح في نافذة جديدة": "Open in new window",
        "خروج": "Logout",

        // Common actions / share
        "تصدير Excel": "Export Excel",
        "تنزيل Excel": "Download Excel",
        "إرسال بالبريد": "Send by Email",
        "إرسال واتساب": "Send via WhatsApp",
        "تنزيل PDF": "Download PDF",
        "مشاركة / تصدير": "Share / Export",
        "طباعة": "Print",
        "إضافة صف": "Add Row",
        "إضافة سائق": "Add Driver",
        "حفظ على الخادم": "Save to Server",
        "بحث": "Search",
        "عرض مختصر": "Compact View",
        "عرض كامل (كل الأعمدة)": "Full View (all columns)",

        // Schedule groups / sections
        "الجدول الرئيسي": "Main Schedule",
        "بيانات الموظف": "Employee Data",
        "بيانات المركبات": "Vehicle Data",
        "بيان المركبات الاسبير والمعطلة": "Spare & Out-of-service Vehicles",
        "السائقون في إجازة (هذا الأسبوع)": "Drivers on Leave (this week)",
        "إرسال للجميع عبر واتساب": "Send to all via WhatsApp",
        "ملخص الأعداد": "Counts Summary",

        // Records (documentation) tab
        "التوثيق والسجلات": "Documentation & Records",
        "ما فائدة هذا التبويب؟": "What is this tab for?",
        "نوع التوثيق": "Record Type",
        "الموضوع": "Subject",
        "التفاصيل": "Details",
        "رقم المرجع": "Reference No.",
        "الحالة": "Status",
        "رابط المستند": "Document Link",

        // Search tab
        "بحث سريع": "Quick Search",
        "ابحث بالاسم أو رقم الإقامة": "Search by name or ID number"
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
    injectAIAssistant();
    injectHelpTour();
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
            { href: '/alerts', text: 'تنبيهات الوثائق', icon: 'bell-ring', emoji: '🔔' },
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
    '☰': 'menu', '✕': 'x', '✖': 'x', '×': 'x',
    // added for the AI assistant + insights/platform pages (all UI emoji → Lucide)
    '🤖': 'bot', '🧹': 'eraser', '🧠': 'brain', '⚡': 'zap', '✏️': 'pencil', '✏': 'pencil',
    '🔌': 'plug', '➤': 'send', '⏳': 'hourglass',
    // full sweep — every remaining UI emoji across all tabs → Lucide
    '❌': 'circle-x', '✓': 'check', '✗': 'x', '📎': 'paperclip', '↗️': 'arrow-up-right', '↗': 'arrow-up-right',
    '🔎': 'search', '🎯': 'target', '🚫': 'ban', '⛔': 'ban', '🧼': 'droplets', '❓': 'circle-help',
    '⬇️': 'arrow-down', '⬇': 'arrow-down', '🛵': 'bike', '🗂️': 'folders', '🗂': 'folders',
    '🗺️': 'map', '🗺': 'map', '📭': 'mailbox', '↔️': 'arrow-left-right', '↔': 'arrow-left-right',
    '🌐': 'globe', '🔙': 'arrow-left', '🪪': 'id-card', '🔗': 'link', '🚐': 'bus',
    '🛡️': 'shield', '🛡': 'shield', '📦': 'package'
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
        if (location.pathname === href) a.className = 'active';   // highlight the current tab
        const after = afterSel ? nav.querySelector(afterSel) : null;
        if (after && after.nextSibling) nav.insertBefore(a, after.nextSibling);
        else nav.appendChild(a);
    }
    addLink('/incidents', '🚨 الحوادث والمخالفات', 'a[href$="/records"]');
    addLink('/documents', '📂 أرشيف الوثائق', 'a[href$="/records"]');
    addLink('/handover', '🚗 تسليم واستلام مركبة', 'a[href$="/"]');
    addLink('/insights', '🧠 التحليلات الذكية', 'a[href$="/cameras"]');
    addLink('/platform', '🚀 المنصة', 'a[href$="/insights"]');
    addLink('/settings', '⚙️ الإعدادات', 'a[href$="/platform"]');
    // (no separate "الفاتورة" link — the homepage "الرئيسية" IS the invoice; /invoice aliases to it)
}

// Floating contact dock (WhatsApp + Send-this-table + Email composer), bottom-left, on EVERY tab.
// Skips if the page already provides its own dock (e.g. the homepage). The 📤 button exports /
// emails the current tab's main table; 📧 opens an in-app email composer (works on any tab).
function injectContactDock() {
    try {
        if (document.querySelector('.bz-dock')) return;
        const dock = document.createElement('div');
        dock.className = 'bz-dock';
        dock.setAttribute('aria-label', 'إجراءات سريعة');
        dock.innerHTML =
            '<a class="bz-dock-btn wa" href="https://wa.me/966570310909?text=مرحباً" target="_blank" rel="noopener" data-label="واتساب" title="تواصل عبر واتساب" aria-label="واتساب">💬</a>' +
            '<a class="bz-dock-btn share" href="javascript:void(0)" data-label="إرسال / تصدير الجدول" title="إرسال أو تصدير جدول هذه الصفحة (Excel · PDF · بريد · واتساب)" aria-label="إرسال أو تصدير">📤</a>' +
            '<a class="bz-dock-btn mail" href="javascript:void(0)" data-label="بريد إلكتروني" title="إنشاء رسالة بريد إلكتروني" aria-label="بريد إلكتروني">📧</a>';
        document.body.appendChild(dock);
        const sh = dock.querySelector('.share'); if (sh) sh.addEventListener('click', function (e) { e.preventDefault(); bzShareCurrentTab(); });
        const ml = dock.querySelector('.mail'); if (ml) ml.addEventListener('click', function (e) { e.preventDefault(); bzComposeEmail(); });
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
        div.innerHTML = '<img src="/static/main_logo_clean.png" alt="شركة بن زومة">';
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
        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape') return;
            var aip = document.getElementById('bzAiPanel');
            if (aip && !aip.hidden) return;        // let the open AI chat panel handle Escape itself
            bzSetDrawer(false);
        });
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
// Theme: DARK (luxury charcoal) is the default. LIGHT mode is opt-in via the `light-mode`
// class on <html>+<body> — so before JS runs the page is already dark (no light flash).
function initThemeToggle() {
    var light = localStorage.getItem('darkMode') === 'false';   // 'false' = user chose light
    document.body.classList.toggle('light-mode', light);
    document.documentElement.classList.toggle('light-mode', light);
    updateToggleButtons(!light);
}

window.toggleDarkMode = function () {
    var isLight = document.body.classList.toggle('light-mode');
    document.documentElement.classList.toggle('light-mode', isLight);
    localStorage.setItem('darkMode', isLight ? 'false' : 'true');
    updateToggleButtons(!isLight);
    if (window.lucide && window.lucide.createIcons) { try { window.lucide.createIcons(); } catch (e) { } }
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
    window.fetch = async function(input, init) {
        // In the workstation namespace, route /api/* calls to the sandboxed /importantworkstation/api/*
        if (inWorkstation() && typeof input === 'string' && input.indexOf('/api/') === 0) {
            input = WS_PREFIX + input;
        }
        startProgress();
        try {
            return await originalFetch(input, init);
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

async function initLanguageTranslation() {
    applyEnglishStyles();

    // Auto-inject translation button
    injectLanguageToggle();

    // Merge the comprehensive site-wide translation map (covers all tabs' UI strings)
    try {
        const r = await fetch('/static/i18n_en.json', { cache: 'no-cache' });
        if (r.ok) {
            const map = await r.json();
            translations.en = Object.assign({}, translations.en, map);
        }
    } catch (e) { /* fall back to the built-in dictionary */ }

    // Fetch and apply saved language (re-applies with the now-complete dictionary)
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
    
    // Update language toggle text (EN / AR)
    const langBtn = document.getElementById('languageToggleBtn');
    if (langBtn) {
        langBtn.innerHTML = lang === 'ar' ? 'EN' : 'AR';
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
            if (trimmed && node.parentElement) {
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
        if (trimmed && dict[trimmed] && node.parentElement) {
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
    langBtn.setAttribute('aria-label', 'Language EN/AR');

    // Unified Styling
    langBtn.style.cursor = 'pointer';
    langBtn.style.border = 'none';
    langBtn.style.borderRadius = '50%';
    langBtn.style.width = '45px';
    langBtn.style.height = '45px';
    langBtn.style.display = 'flex';
    langBtn.style.alignItems = 'center';
    langBtn.style.justifyContent = 'center';
    langBtn.style.fontSize = '0.95rem';
    langBtn.style.fontWeight = '800';
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
        langBtn.innerHTML = currentLang === 'ar' ? 'EN' : 'AR';
        darkToggle.parentNode.insertBefore(langBtn, darkToggle.nextSibling);
    } else {
        // Floating fallback
        langBtn.style.position = 'fixed';
        langBtn.style.top = '15px';
        langBtn.style.right = '75px';
        
        const currentLang = localStorage.getItem('lang') || 'ar';
        langBtn.innerHTML = currentLang === 'ar' ? 'EN' : 'AR';
        document.body.appendChild(langBtn);
    }
}

// =============================================================================
// SHARED SECURITY + AUTOFILL ENGINE (used by every tab)
// =============================================================================

/** Escape a value for safe insertion into HTML (prevents stored XSS). */
window.escapeHtml = function (value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
};

/** Normalize a plate string (strip spaces, Arabic→English digits) for matching. */
window.normalizePlate = function (plate) {
    if (plate == null) return '';
    let p = String(plate);
    const ar = '٠١٢٣٤٥٦٧٨٩', en = '0123456789';
    for (let i = 0; i < ar.length; i++) p = p.split(ar[i]).join(en[i]);
    p = p.replace(/\s+/g, '');
    const digits = (p.match(/\d+/g) || []).join('');
    const letters = (p.match(/[^\d]+/g) || []).join('');
    return digits + letters;
};

/**
 * FleetData — single source of truth for driver/vehicle autofill across all tabs.
 * Loads /static/fleet_data.json once and caches it.
 */
window.FleetData = (function () {
    let _cache = null;
    let _promise = null;

    async function load() {
        if (_cache) return _cache;
        if (_promise) return _promise;
        // Workstation is a blank slate: no preloaded fleet registry → no autofill/suggestions
        // from the real data. The user enters everything manually (saved to the server).
        if (window.BZ_WS) { _cache = []; return _cache; }
        _promise = fetch('/api/fleet_data')
            .then(function (r) { return r.ok ? r.json() : []; })
            .then(function (rows) { _cache = Array.isArray(rows) ? rows : []; return _cache; })
            .catch(function () { _cache = []; return _cache; });
        return _promise;
    }

    function records() { return _cache || []; }

    function byName(name) {
        const n = String(name || '').trim();
        if (!n) return null;
        return records().find(function (d) { return (d.name || '').trim() === n; }) || null;
    }

    function byPlate(plate) {
        const target = window.normalizePlate(plate);
        if (!target) return null;
        return records().find(function (d) { return window.normalizePlate(d.plate) === target; }) || null;
    }

    function byIqama(iqama) {
        const t = String(iqama == null ? '' : iqama).replace(/\D/g, '');
        if (!t) return null;
        return records().find(function (d) { return String(d.iqama || '').replace(/\D/g, '') === t; }) || null;
    }

    /** Populate a <datalist> (or <select>) with all driver names. */
    async function fillDatalist(elOrId) {
        await load();
        const el = typeof elOrId === 'string' ? document.getElementById(elOrId) : elOrId;
        if (!el) return;
        const tag = el.tagName.toLowerCase();
        let opts = (tag === 'select' ? '<option value=""></option>' : '');
        const added = new Set();
        records().forEach(function (d) {
            const n = window.escapeHtml((d.name || '').trim());
            const p = window.escapeHtml((d.plate || '').trim());
            const e = window.escapeHtml((d.empid || '').trim());
            if (n && !added.has(n)) {
                opts += '<option value="' + n + '">' + p + (e ? ' | ' + e : '') + '</option>';
                added.add(n);
            }
            if (p && !added.has(p)) {
                opts += '<option value="' + p + '">' + n + '</option>';
                added.add(p);
            }
            if (e && !added.has(e)) {
                opts += '<option value="' + e + '">' + n + '</option>';
                added.add(e);
            }
        });
        el.innerHTML = opts;
    }

    /**
     * Wire a name input so selecting/typing a known driver auto-fills related fields.
     * opts: { name: '#or id of name input', fields: { iqama:'id', empid:'id', plate:'id', car:'id', phone:'id' } }
     * Field targets may be element ids or elements; setter callbacks also supported via fields.set(record).
     */
    async function attachAutofill(opts) {
        await load();
        const nameEl = typeof opts.name === 'string'
            ? (document.getElementById(opts.name) || document.querySelector(opts.name))
            : opts.name;
        if (!nameEl) return;
        if (nameEl.tagName.toLowerCase() === 'input' && nameEl.getAttribute('list')) {
            await fillDatalist(nameEl.getAttribute('list'));
        }
        const fields = opts.fields || {};
        function apply() {
            const rec = byName(nameEl.value);
            if (!rec) return;
            ['iqama', 'empid', 'plate', 'car', 'phone'].forEach(function (key) {
                if (!fields[key]) return;
                const t = typeof fields[key] === 'string'
                    ? (document.getElementById(fields[key]) || document.querySelector(fields[key]))
                    : fields[key];
                if (t && 'value' in t && (rec[key] || rec[key] === '')) t.value = rec[key] || '';
            });
            if (typeof opts.onFill === 'function') opts.onFill(rec);
        }
        if (nameEl.dataset.bzAutofillBound === '1') return; // avoid duplicate listeners on repeat calls
        nameEl.dataset.bzAutofillBound = '1';
        nameEl.addEventListener('change', apply);
        nameEl.addEventListener('input', apply);
    }

    return {
        load: load, records: records, byName: byName, byPlate: byPlate, byIqama: byIqama, byEmpid: byEmpid,
        fillDatalist: fillDatalist, attachAutofill: attachAutofill,
        // Aliases some templates (schedule.html, washing.html) call directly on FleetData —
        // kept here so those call sites don't need their own null-guards duplicated.
        all: records, normalizePlate: window.normalizePlate,
    };
})();

// =============================================================================
// SHARE / EXPORT HELPERS (used by every tab): Download · Email · WhatsApp · PDF
// =============================================================================

// Current language + translate-a-string helper (for Excel headers, dynamic text, etc.)
window.bzLang = function () { return localStorage.getItem('lang') || 'ar'; };
window.bzTL = function (ar) {
    const d = (typeof translations !== 'undefined' && translations.en) ? translations.en : {};
    const key = String(ar == null ? '' : ar).trim();
    return (window.bzLang() === 'en' && d[key]) ? d[key] : ar;
};

window.bzBlobToBase64 = function (blob) {
    return new Promise((resolve, reject) => {
        const r = new FileReader();
        r.onloadend = () => resolve(String(r.result).split(',')[1]);
        r.onerror = reject;
        r.readAsDataURL(blob);
    });
};

window.bzDownload = function (blob, filename) {
    if (window.saveAs) { window.saveAs(blob, filename); return; }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
};

window.bzEmailFile = async function (blob, filename, subject) {
    const email = (window.prompt('أدخل البريد الإلكتروني للمستلم:', '') || '').trim();
    if (!email) return;
    try {
        const b64 = await bzBlobToBase64(blob);
        const r = await fetch('/api/send_email', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, filename: filename, file_b64: b64, subject: subject || filename })
        });
        const d = await r.json().catch(() => ({}));
        if (r.ok && d.success) showToast('تم إرسال الملف إلى ' + email, 'success');
        else showToast('تعذّر الإرسال: ' + (d.error || ''), 'error');
    } catch (e) { showToast('تعذّر الإرسال بالبريد', 'error'); }
};

// WhatsApp web links can't carry file attachments — download the file then open a chat
// with a note so the user attaches it. (Honest limitation of wa.me.)
window.bzWhatsAppFile = function (blob, filename, message) {
    bzDownload(blob, filename);
    const phone = (window.prompt('رقم واتساب المستلم (اختياري، بصيغة 9665…) — اتركه فارغاً لاختيار المحادثة:', '') || '').replace(/\D/g, '');
    const msg = (message || ('الملف المرفق: ' + filename)) + '\n(تم تنزيل الملف على جهازك — يرجى إرفاقه في المحادثة)';
    const base = phone ? ('https://wa.me/' + phone) : 'https://wa.me/';
    window.open(base + '?text=' + encodeURIComponent(msg), '_blank');
    showToast('تم تنزيل الملف — أرفقه في واتساب', 'info');
};

let _html2pdfLoading = null;
function bzEnsureHtml2pdf() {
    if (window.html2pdf) return Promise.resolve();
    if (_html2pdfLoading) return _html2pdfLoading;
    _html2pdfLoading = new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
        s.onload = resolve; s.onerror = reject;
        document.head.appendChild(s);
    });
    return _html2pdfLoading;
}

/** Render a DOM element to a PDF Blob (Arabic-safe; rasterizes the element). */
window.bzElementToPdfBlob = async function (element, orientation) {
    if (!element) throw new Error('bzElementToPdfBlob: no element provided');
    await bzEnsureHtml2pdf();
    const opt = {
        margin: 6, image: { type: 'jpeg', quality: 0.95 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
        jsPDF: { unit: 'mm', format: 'a4', orientation: orientation || 'landscape' }
    };
    return window.html2pdf().set(opt).from(element).toPdf().output('blob');
};

/**
 * Unified share menu. Pass an async builder that returns a Blob, or pass {blob}.
 * opts: { filename, subject, pdfElement (DOM el or id for PDF), waMessage }
 */
window.bzShare = function (getExcelBlob, opts) {
    opts = opts || {};
    const overlay = document.createElement('div');
    overlay.className = 'modal-backdrop show';
    overlay.style.zIndex = 3000;
    overlay.innerHTML =
        '<div class="modal-content-custom" style="max-width:420px;">' +
        '<div class="modal-header-custom"><h2>📤 مشاركة / تصدير</h2>' +
        '<button class="close-btn" data-x>✕</button></div>' +
        '<div class="modal-body-custom"><div class="bz-share-menu" style="flex-direction:column;">' +
        '<button class="btn-primary" data-act="dl-xlsx">📥 تنزيل Excel</button>' +
        '<button class="btn-outline" data-act="email-xlsx">📧 إرسال Excel بالبريد</button>' +
        '<button class="btn-outline" data-act="wa-xlsx">💬 إرسال Excel واتساب</button>' +
        (opts.pdfElement ? '<hr style="border:none;border-top:1px solid var(--border);margin:6px 0;">' +
            '<button class="btn-primary" data-act="dl-pdf">📄 تنزيل PDF</button>' +
            '<button class="btn-outline" data-act="email-pdf">📧 إرسال PDF بالبريد</button>' +
            '<button class="btn-outline" data-act="wa-pdf">💬 إرسال PDF واتساب</button>' : '') +
        '</div></div></div>';
    document.body.appendChild(overlay);
    const close = () => { overlay.remove(); };
    overlay.addEventListener('click', (e) => { if (e.target === overlay || (e.target.closest && e.target.closest('[data-x]'))) close(); });

    const fnameBase = (opts.filename || 'ملف').replace(/\.(xlsx|pdf)$/i, '');
    const getPdfEl = () => typeof opts.pdfElement === 'string' ? document.getElementById(opts.pdfElement) : opts.pdfElement;

    overlay.querySelectorAll('button[data-act]').forEach(btn => btn.addEventListener('click', async () => {
        const act = btn.dataset.act;
        btn.disabled = true;
        try {
            if (act.endsWith('xlsx')) {
                const blob = typeof getExcelBlob === 'function' ? await getExcelBlob() : getExcelBlob;
                if (!blob) { showToast('تعذّر تجهيز ملف Excel', 'error'); return; }
                const fn = fnameBase + '.xlsx';
                if (act === 'dl-xlsx') bzDownload(blob, fn);
                else if (act === 'email-xlsx') await bzEmailFile(blob, fn, opts.subject);
                else bzWhatsAppFile(blob, fn, opts.waMessage);
            } else {
                const el = getPdfEl();
                if (!el) { showToast('لا يوجد محتوى للـ PDF', 'error'); return; }
                const blob = await bzElementToPdfBlob(el, opts.pdfOrientation);
                const fn = fnameBase + '.pdf';
                if (act === 'dl-pdf') bzDownload(blob, fn);
                else if (act === 'email-pdf') await bzEmailFile(blob, fn, opts.subject);
                else bzWhatsAppFile(blob, fn, opts.waMessage);
            }
            close();
        } catch (e) { showToast('حدث خطأ: ' + e.message, 'error'); }
        finally { btn.disabled = false; }
    }));
};

// ── Universal "send this table" (every table-bearing tab) ────────────────────────────
// Loads SheetJS on demand to turn ANY DOM table (incl. input-grids) into a real .xlsx;
// falls back to a UTF-8 CSV if the CDN is unavailable so Arabic still opens cleanly in Excel.
let _xlsxLoading = null;
function bzEnsureXlsx() {
    if (window.XLSX) return Promise.resolve();
    if (_xlsxLoading) return _xlsxLoading;
    _xlsxLoading = new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
        s.onload = resolve; s.onerror = reject;
        document.head.appendChild(s);
    });
    return _xlsxLoading;
}

// Read a DOM table into an array-of-arrays, taking <input>/<select>/<textarea> VALUES
// (so editable grids export their real content, not blanks). Skips pure action columns.
function bzExtractTable(table) {
    const aoa = [];
    table.querySelectorAll('tr').forEach(tr => {
        const cells = tr.querySelectorAll('th,td');
        if (!cells.length) return;
        const row = [];
        cells.forEach(td => {
            if (td.hasAttribute('data-noexport') || td.classList.contains('no-print')) return;
            const f = td.querySelector('input,select,textarea');
            let v;
            if (f) { v = (f.type === 'checkbox') ? (f.checked ? '✓' : '') : (f.value || ''); }
            else { v = (td.innerText || td.textContent || ''); }
            row.push(String(v == null ? '' : v).replace(/\s+/g, ' ').trim());
        });
        if (row.some(c => c !== '')) aoa.push(row);
    });
    return aoa;
}

window.bzTableToXlsxBlob = async function (table, sheetName) {
    const aoa = bzExtractTable(table);
    if (!aoa.length) throw new Error('الجدول فارغ');
    try {
        await bzEnsureXlsx();
        const ws = XLSX.utils.aoa_to_sheet(aoa);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, String(sheetName || 'بيانات').replace(/[\\/?*\[\]:]/g, ' ').slice(0, 28) || 'بيانات');
        const buf = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
        return new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    } catch (e) {
        const csv = aoa.map(r => r.map(c => '"' + c.replace(/"/g, '""') + '"').join(',')).join('\r\n');
        return new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' });
    }
};

// Find the page's significant data tables (visible, non-trivial), largest first.
function bzFindDataTables() {
    const scope = document.querySelector('.bz-shell') || document.querySelector('.dashboard-shell') || document.body;
    return Array.from(scope.querySelectorAll('table')).filter(t => {
        const rows = t.querySelectorAll('tr').length;
        const cells = t.querySelectorAll('td,th').length;
        return rows >= 2 && cells >= 4 && t.offsetParent !== null;
    }).sort((a, b) => b.querySelectorAll('td,th').length - a.querySelectorAll('td,th').length);
}

function bzPageTitle() {
    const el = document.querySelector('.bz-section-title, h1, h2');
    return ((el && el.textContent) || document.title || 'تقرير').replace(/\s+/g, ' ').trim().slice(0, 60);
}

// 📤 dock action: share/export THIS tab's main table; no table → open the email composer.
window.bzShareCurrentTab = function () {
    const tables = bzFindDataTables();
    const title = bzPageTitle();
    if (!tables.length) {
        if (typeof showToast === 'function') showToast('لا يوجد جدول في هذه الصفحة — فُتح إنشاء بريد', 'info');
        bzComposeEmail({ subject: title });
        return;
    }
    bzShare(() => bzTableToXlsxBlob(tables[0], title), {
        filename: title, subject: title, pdfElement: tables[0],
        pdfOrientation: 'landscape', waMessage: 'تقرير: ' + title
    });
};

// 📧 In-app email composer (to / cc / subject / body + optional "attach this page as PDF").
// Posts to /api/compose_email. Works on EVERY tab — even ones without a table.
window.bzComposeEmail = function (opts) {
    opts = opts || {};
    const ea = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
    const overlay = document.createElement('div');
    overlay.className = 'modal-backdrop show'; overlay.style.zIndex = 3000;
    overlay.innerHTML =
        '<div class="modal-content-custom" style="max-width:520px;">' +
        '<div class="modal-header-custom"><h2>📧 إرسال بريد إلكتروني</h2><button class="close-btn" data-x aria-label="إغلاق">✕</button></div>' +
        '<div class="modal-body-custom">' +
        '<label class="bz-fld"><span>إلى</span><input id="bzceTo" type="email" inputmode="email" dir="ltr" placeholder="recipient@example.com" value="' + ea(opts.to || '') + '"></label>' +
        '<label class="bz-fld"><span>نسخة (CC) — اختياري</span><input id="bzceCc" type="text" dir="ltr" placeholder="عناوين مفصولة بفواصل"></label>' +
        '<label class="bz-fld"><span>الموضوع</span><input id="bzceSub" type="text" value="' + ea(opts.subject || 'BIN ZOMAH INTL.') + '"></label>' +
        '<label class="bz-fld"><span>الرسالة</span><textarea id="bzceBody" rows="5" placeholder="اكتب رسالتك هنا…">' + ea(opts.body || '') + '</textarea></label>' +
        '<label class="bz-chk"><input id="bzceAttach" type="checkbox"> إرفاق هذه الصفحة كملف PDF</label>' +
        '<div class="bz-msg2" id="bzceMsg"></div>' +
        '<div class="bz-fld-actions"><button class="btn-outline" data-x type="button">إلغاء</button><button class="btn-primary" id="bzceSend" type="button">📨 إرسال</button></div>' +
        '</div></div>';
    document.body.appendChild(overlay);
    const close = () => overlay.remove();
    overlay.addEventListener('click', e => { if (e.target === overlay || (e.target.closest && e.target.closest('[data-x]'))) close(); });
    const q = id => overlay.querySelector(id);
    q('#bzceTo').focus();
    q('#bzceSend').addEventListener('click', async () => {
        const to = q('#bzceTo').value.trim();
        const msg = q('#bzceMsg');
        if (!to || to.indexOf('@') < 1 || to.indexOf('.') < 0) { msg.style.color = '#ef4444'; msg.textContent = 'أدخل بريداً إلكترونياً صحيحاً'; return; }
        const fd = new FormData();
        fd.append('email', to);
        fd.append('subject', q('#bzceSub').value || 'BIN ZOMAH INTL.');
        fd.append('body', q('#bzceBody').value || '');
        q('#bzceCc').value.split(/[,;\s]+/).filter(Boolean).forEach(c => fd.append('cc', c));
        const send = q('#bzceSend'); send.disabled = true; msg.style.color = 'var(--text-secondary)'; msg.textContent = 'جارٍ الإرسال…';
        try {
            if (q('#bzceAttach').checked) {
                const el = document.querySelector('.bz-shell') || document.body;
                const blob = await bzElementToPdfBlob(el, 'portrait');
                fd.append('attachment', new File([blob], (q('#bzceSub').value || 'page').replace(/[\\/?*\[\]:]/g, ' ').slice(0, 40) + '.pdf', { type: 'application/pdf' }));
            }
            const r = await fetch('/api/compose_email', { method: 'POST', body: fd });
            const d = await r.json().catch(() => ({}));
            if (r.ok && d.success) { if (typeof showToast === 'function') showToast('تم إرسال البريد إلى ' + to, 'success'); close(); }
            else { msg.style.color = '#ef4444'; msg.textContent = 'تعذّر الإرسال: ' + (d.error || 'تحقّق من إعداد البريد على الخادم'); }
        } catch (e) { msg.style.color = '#ef4444'; msg.textContent = 'تعذّر الاتصال بالخادم'; }
        finally { send.disabled = false; }
    });
};

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

// =============================================================================
// AI ASSISTANT (مساعد بن زومة الذكي) — chat + reviewable table edits, every tab.
// Sends the CURRENT tab's table to the server-side Gemini proxy (/api/ai/chat); the
// key never reaches the browser. Proposed edits are shown as a diff and applied to the
// live input-grid ONLY on confirm — the page's own save then persists (frozen-data safe).
// Skipped on the open workstation sandbox (no token spend there).
// =============================================================================

// Read a table into {headers, rows, trs} keeping LIVE row order (no trimming) so model
// row indices map 1:1 onto the on-page rows when applying edits.
function bzAIGrid(table) {
    function vis(tr) {
        var o = [];
        tr.querySelectorAll('th,td').forEach(function (c) {
            if (c.hasAttribute('data-noexport') || c.classList.contains('no-print')) return;
            o.push(c);
        });
        return o;
    }
    function rd(cell) {
        var f = cell && cell.querySelector('input,select,textarea');
        if (f) return f.type === 'checkbox' ? (f.checked ? '✓' : '') : (f.value || '');
        return cell ? (cell.innerText || cell.textContent || '').replace(/\s+/g, ' ').trim() : '';
    }
    var thead = table.querySelector('thead');
    var headRows = thead ? Array.prototype.slice.call(thead.querySelectorAll('tr')) : [];
    var body = table.querySelector('tbody') || table;
    // data rows: skip header rows + placeholder/empty-state rows (single colspan cell, e.g. «لا يوجد»)
    var trs = Array.prototype.filter.call(body.querySelectorAll('tr'), function (tr) {
        return headRows.indexOf(tr) === -1 && tr.querySelector('td') && vis(tr).length > 1;
    });
    var dataCols = trs.length ? vis(trs[0]).length : 0;
    // Header row = the thead row whose visible-cell count matches the data rows. Grouped grids
    // (employees/schedule/oils/purchase) put a colspan group/title row FIRST and the real column
    // labels in the LAST row, so blindly taking the first thead row would mis-map every column.
    var headRow = null;
    if (headRows.length) {
        headRow = headRows[headRows.length - 1];
        if (dataCols) {
            var bestDiff = 1e9;
            headRows.forEach(function (hr) { var diff = Math.abs(vis(hr).length - dataCols); if (diff < bestDiff) { bestDiff = diff; headRow = hr; } });
        }
    } else {
        headRow = table.querySelector('tr');
    }
    var headers = headRow ? vis(headRow).map(function (c) { return (c.innerText || c.textContent || '').replace(/\s+/g, ' ').trim(); }) : [];
    var rows = trs.map(function (tr) { return vis(tr).map(rd); });
    return { headers: headers, rows: rows, trs: trs, vis: vis, table: table };
}

function bzAIColResolver(headers) {
    function norm(s) { return String(s == null ? '' : s).replace(/[ً-ْٰ]/g, '').replace(/^#\s*/, '').replace(/\s+/g, ' ').trim().toLowerCase(); }
    var map = Object.create(null);
    headers.forEach(function (h, i) { var k = norm(h); if (k && !(k in map)) map[k] = i; });
    return function (col) {
        if (typeof col === 'number') return (col >= 0 && col < headers.length) ? col : -1;
        var k = norm(col); if (k === '') return -1;
        if (k in map) return map[k];
        var hit = Object.keys(map).filter(function (h) { return h && (h.indexOf(k) === 0 || k.indexOf(h) === 0); });
        return hit.length === 1 ? map[hit[0]] : -1;
    };
}

function bzAIWrite(cell, val) {
    var f = cell && cell.querySelector('input,select,textarea');
    if (f) {
        if (f.type === 'checkbox') f.checked = !!val && val !== '✗' && val !== '' && val !== '0';
        else f.value = String(val == null ? '' : val);
        f.classList.add('bz-ai-changed');
        f.dispatchEvent(new Event('input', { bubbles: true }));   // drive the page's own model-sync + autosave
        f.dispatchEvent(new Event('change', { bubbles: true }));
    } else if (cell) { cell.textContent = String(val == null ? '' : val); }
}

function bzAIAddRow(grid, values) {
    var tbody = grid.table.querySelector('tbody') || grid.table;
    var last = grid.trs[grid.trs.length - 1];
    if (!last) return;
    var clone = last.cloneNode(true);
    clone.querySelectorAll('input,select,textarea').forEach(function (f) { if (f.type === 'checkbox') f.checked = false; else f.value = ''; });
    tbody.appendChild(clone);
    var cells = grid.vis(clone);
    (values || []).forEach(function (v, i) { if (cells[i]) bzAIWrite(cells[i], v); });
    grid.table.dispatchEvent(new Event('input', { bubbles: true }));
}

// Validate ALL actions first, build a human diff + apply steps. Nothing mutates until run.
// Capture a labelled form control's best label (for/ancestor/preceding/placeholder/aria/name).
function bzAIFieldLabel(el) {
    try {
        if (el.id) { var l = document.querySelector('label[for="' + ((window.CSS && CSS.escape) ? CSS.escape(el.id) : el.id) + '"]'); if (l && l.textContent.trim()) return l.textContent; }
    } catch (e) { }
    var lab = el.closest('label'); if (lab && lab.textContent.trim()) return lab.textContent.replace(el.value || '', '');
    var prev = el.previousElementSibling;
    while (prev) { if (/^(label|span|div|p|h[1-6]|strong|b)$/i.test(prev.tagName) && prev.textContent.trim()) return prev.textContent; prev = prev.previousElementSibling; }
    var p = el.parentElement;
    if (p) { var pl = p.querySelector('label, .label, .field-label'); if (pl && pl.textContent.trim()) return pl.textContent; }
    return el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.name || '';
}
// Page form fields (NOT inside a data table, not the chrome/AI panel) the assistant can read/fill.
function bzAIFormFields() {
    var scope = document.querySelector('.bz-shell') || document.body, out = [], seen = Object.create(null);
    scope.querySelectorAll('input, select, textarea').forEach(function (el) {
        if (el.closest('table')) return;                                   // table cells handled by the grid
        if (el.closest('#bzAiPanel, .bz-ai-panel, .bz-topbar, .bz-sidebar, .bz-dock')) return;
        var t = (el.type || '').toLowerCase();
        if (['hidden', 'submit', 'button', 'file', 'search', 'image', 'reset'].indexOf(t) >= 0) return;
        if (el.disabled || el.readOnly || el.offsetParent === null) return; // skip disabled/hidden
        var label = (bzAIFieldLabel(el) || '').replace(/\s+/g, ' ').trim().slice(0, 80);
        if (!label || seen[label]) return;
        seen[label] = 1;
        if (out.length >= 40) return;                 // cap BEFORE push (forEach can't break)
        var val = (t === 'checkbox' || t === 'radio') ? (el.checked ? '✓' : '') : (el.value || '');
        out.push({ label: label, value: val, el: el, type: t });
    });
    return out;
}
function bzAIWriteField(el, val) {
    if (!el) return;
    var v = String(val == null ? '' : val);
    if (el.type === 'checkbox' || el.type === 'radio') { el.checked = !!v && v !== '✗' && v !== '0' && v.toLowerCase() !== 'false'; }
    else if (el.tagName === 'SELECT') {
        var matched = false;
        Array.prototype.forEach.call(el.options, function (o) { if (!matched && (o.value === v || (o.textContent || '').trim() === v)) { el.value = o.value; matched = true; } });
        if (!matched && v) Array.prototype.forEach.call(el.options, function (o) { if (!matched && (o.textContent || '').trim().indexOf(v) >= 0) { el.value = o.value; matched = true; } });
        if (!matched) el.value = v;
    } else { el.value = v; }
    el.classList.add('bz-ai-changed');
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
}

function bzAIPlan(grid, fields, actions) {
    var resolve = grid ? bzAIColResolver(grid.headers) : null;
    var steps = [], delSteps = [], diff = [], errors = [], deletes = 0, MAXPER = 50;
    function readCellVal(cell) { var f = cell && cell.querySelector('input,select,textarea'); return f ? (f.value || '') : (cell ? (cell.innerText || cell.textContent || '').trim() : ''); }
    function nrm(s) { return String(s == null ? '' : s).replace(/[ً-ْٰ]/g, '').replace(/^#\s*/, '').replace(/\s+/g, ' ').trim().toLowerCase(); }
    var fmap = Object.create(null); (fields || []).forEach(function (f) { if (f && f.label) { var k = nrm(f.label); if (!(k in fmap)) fmap[k] = f; } });
    function resolveField(name) {
        var k = nrm(name); if (!k) return null;
        if (k in fmap) return fmap[k];
        var hit = Object.keys(fmap).filter(function (h) { return h && (h.indexOf(k) === 0 || k.indexOf(h) === 0); });
        return hit.length === 1 ? fmap[hit[0]] : null;
    }
    function needGrid() { if (!grid) throw 'لا يوجد جدول في هذه الصفحة (افتح التبويب المطلوب أولاً)'; }
    (actions || []).forEach(function (a) {
        try {
            if (!a || typeof a !== 'object') throw 'إجراء غير صالح';
            if (a.op === 'set_field') {
                var f = resolveField(a.field || a.col || a.label); if (!f) throw 'حقل غير معروف: «' + (a.field || a.col || '') + '»';
                var bf = f.el ? ((f.el.type === 'checkbox' || f.el.type === 'radio') ? (f.el.checked ? '✓' : '') : (f.el.value || '')) : '';
                diff.push('حقل «' + f.label + '»: «' + bf + '» → «' + (a.value == null ? '' : a.value) + '»');
                (function (el) { steps.push(function () { bzAIWriteField(el, a.value); }); })(f.el);
            } else if (a.op === 'set_cell') {
                needGrid();
                var ci = resolve(a.col); if (ci < 0) throw 'عمود غير معروف: «' + (a.col || '') + '»';
                var r = a.row; if (typeof r !== 'number' || r < 0 || r >= grid.trs.length) throw 'صف خارج النطاق';
                (function (rr, cc) {
                    var before = readCellVal(grid.vis(grid.trs[rr])[cc]);
                    diff.push('صف ' + (rr + 1) + ' · ' + grid.headers[cc] + ': «' + before + '» → «' + (a.value == null ? '' : a.value) + '»');
                    steps.push(function () { bzAIWrite(grid.vis(grid.trs[rr])[cc], a.value); });
                })(r, ci);
            } else if (a.op === 'fill_column') {
                needGrid();
                var ci2 = resolve(a.col); if (ci2 < 0) throw 'عمود غير معروف: «' + (a.col || '') + '»';
                var n = 0;
                grid.trs.forEach(function (tr) {
                    var cur = readCellVal(grid.vis(tr)[ci2]);
                    if (a.only_empty !== false && String(cur).trim() !== '') return;
                    if (String(cur) === String(a.value)) return;
                    n++; steps.push(function () { bzAIWrite(grid.vis(tr)[ci2], a.value); });
                });
                if (n > MAXPER) throw 'التعبئة تتجاوز الحد (' + n + ')';
                if (n) diff.push('تعبئة «' + grid.headers[ci2] + '» بـ «' + (a.value == null ? '' : a.value) + '» (' + n + ' خانة)');
            } else if (a.op === 'add_row') {
                needGrid();
                diff.push('+ صف جديد: ' + ((a.values || []).join(' · ') || '(فارغ)'));
                steps.push(function () { bzAIAddRow(grid, a.values || []); });
            } else if (a.op === 'delete_row') {
                needGrid();
                var dr = a.row; if (typeof dr !== 'number' || dr < 0 || dr >= grid.trs.length) throw 'صف خارج النطاق';
                deletes++; diff.push('− حذف صف ' + (dr + 1));
                (function (rr) { delSteps.push(function () { var tr = grid.trs[rr]; if (tr && tr.isConnected) { tr.remove(); grid.table.dispatchEvent(new Event('input', { bubbles: true })); } }); })(dr);
            } else { throw 'عملية غير مدعومة'; }
        } catch (e) { errors.push(String(e)); }
    });
    if (deletes > 0 && grid && grid.trs.length - deletes < 1) return { steps: [], diff: [], errors: errors.concat(['لا يمكن حذف كل الصفوف']) };
    return { steps: steps.concat(delSteps), diff: diff, errors: errors };   // edits first, deletions last
}

function injectAIAssistant() {
    try {
        if (typeof inWorkstation === 'function' && inWorkstation()) return;       // no AI on the open sandbox
        if (/\/(login|lock)/.test(location.pathname)) return;
        if (!document.querySelector('.bz-topbar') && !document.querySelector('.bz-shell')) return;
        if (document.getElementById('bzAiFab')) return;
        var esc = window.escapeHtml || function (s) { return String(s == null ? '' : s); };
        var titleOf = function () { return (typeof bzPageTitle === 'function') ? bzPageTitle() : document.title; };
        var CKEY = 'bz_ai_convos_v1';

        // ── conversation store (localStorage) ───────────────────────────────────
        function loadConvos() { try { return JSON.parse(localStorage.getItem(CKEY) || '[]') || []; } catch (e) { return []; } }
        function saveConvos() { try { localStorage.setItem(CKEY, JSON.stringify(convos.filter(function (c) { return c.messages && c.messages.length; }).slice(0, 60))); } catch (e) { } }
        function nowStr() { var d = new Date(); function p(n) { return (n < 10 ? '0' : '') + n; } return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes()); }
        function classify(conv) {
            var hasEdit = (conv.messages || []).some(function (m) { return m.edits; });
            if (hasEdit) return 'تعديل بيانات';
            var txt = (conv.messages || []).map(function (m) { return m.text; }).join(' ');
            if (/\bكم\b|عدد|إجمالي|احسب|كمية/.test(txt)) return 'استفسار أعداد';
            if (/موظف|سائق|إقامة|جوال/.test(txt)) return 'الموظفون والسائقون';
            if (/مركبة|لوحة|سيارة|دينا|لوري/.test(txt)) return 'المركبات';
            if (/جدول/.test(txt)) return 'الجدول الأسبوعي';
            if (/زيت|صيانة|ورشة|فلتر/.test(txt)) return 'الصيانة';
            if (/حادث|مخالف/.test(txt)) return 'الحوادث';
            return 'عام';
        }
        function titleFor(conv) {
            var u = (conv.messages || []).filter(function (m) { return m.role === 'user'; })[0];
            return (u && u.text ? u.text : 'محادثة جديدة').replace(/\s+/g, ' ').trim().slice(0, 44);
        }

        var convos = loadConvos();
        var cur = null, busy = false, typingEl = null, usage = null;

        var fab = document.createElement('button');
        fab.id = 'bzAiFab'; fab.type = 'button'; fab.className = 'bz-ai-fab';
        fab.title = 'المساعد الذكي'; fab.setAttribute('aria-label', 'المساعد الذكي');
        fab.innerHTML = '<span class="bz-ai-fab-ic">🤖</span>';
        document.body.appendChild(fab);

        var panel = document.createElement('section');
        panel.id = 'bzAiPanel'; panel.className = 'bz-ai-panel'; panel.setAttribute('dir', 'rtl');
        panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'المساعد الذكي'); panel.hidden = true;
        panel.innerHTML =
            '<header class="bz-ai-hd"><span class="bz-ai-av">🤖</span>' +
            '<div class="bz-ai-meta"><b>مساعد بن زومة الذكي</b><span class="bz-ai-ctx"></span></div>' +
            '<button class="bz-ai-x" data-hist type="button" title="المحادثات السابقة" aria-label="المحادثات">🕓</button>' +
            '<button class="bz-ai-x" data-new type="button" title="محادثة جديدة" aria-label="محادثة جديدة">➕</button>' +
            '<button class="bz-ai-x" data-close type="button" title="إغلاق" aria-label="إغلاق">✕</button></header>' +
            '<div class="bz-ai-usage" title="استخدام اليوم — حدّ التطبيق الواقي لخدمة Gemini"></div>' +
            '<div class="bz-ai-msgs"></div>' +
            '<div class="bz-ai-chips"></div>' +
            '<div class="bz-ai-history" hidden><div class="bz-ai-history-hd"><b>المحادثات السابقة</b>' +
            '<button class="bz-ai-x" data-histclose type="button" aria-label="رجوع">✕</button></div>' +
            '<div class="bz-ai-history-list"></div></div>' +
            '<form class="bz-ai-bar"><textarea class="bz-ai-in" rows="1" placeholder="اسأل عن أي تبويب أو اطلب تعديلاً…" aria-label="رسالتك"></textarea>' +
            '<button class="bz-ai-send" type="submit" title="إرسال" aria-label="إرسال">➤</button></form>';
        document.body.appendChild(panel);

        var msgs = panel.querySelector('.bz-ai-msgs'), chips = panel.querySelector('.bz-ai-chips'),
            input = panel.querySelector('.bz-ai-in'), ctxEl = panel.querySelector('.bz-ai-ctx'),
            form = panel.querySelector('.bz-ai-bar'), usageEl = panel.querySelector('.bz-ai-usage'),
            histEl = panel.querySelector('.bz-ai-history'), histList = panel.querySelector('.bz-ai-history-list');

        function lucidify() { try { if (typeof bzReplaceEmojis === 'function') bzReplaceEmojis(panel); } catch (e) { } }

        // ── usage / limit counter ───────────────────────────────────────────────
        function renderUsage() {
            if (!usage) { usageEl.innerHTML = ''; return; }
            var d = usage.day || 0, cap = usage.day_cap || 150, m = usage.minute || 0, mc = usage.minute_cap || 8, tok = usage.tokens || 0;
            var gr = usage.global_cap ? (usage.global || 0) / usage.global_cap : 0;
            var ratio = Math.max(cap ? d / cap : 0, gr), cls = ratio >= 0.9 ? 'red' : ratio >= 0.6 ? 'amber' : 'ok';
            usageEl.className = 'bz-ai-usage ' + cls;
            usageEl.innerHTML = '<span class="bz-ai-usage-bar"><i style="width:' + Math.min(100, Math.round(ratio * 100)) + '%"></i></span>' +
                '<span class="bz-ai-usage-t">طلبات اليوم <b>' + d + '/' + cap + '</b> · الدقيقة ' + m + '/' + mc + ' · الرموز ' + Number(tok).toLocaleString('en-US') + '</span>';
        }
        function fetchUsage() { fetch('/api/ai/status', { headers: { 'Accept': 'application/json' } }).then(function (r) { return r.json(); }).then(function (j) { if (j && j.usage) { usage = j.usage; renderUsage(); } }).catch(function () { }); }

        // ── conversation lifecycle ──────────────────────────────────────────────
        function newConvo() { cur = { id: 'c' + Date.now(), title: 'محادثة جديدة', type: 'عام', branch: (window.BZ_BRANCH || ''), ts: nowStr(), messages: [] }; convos.unshift(cur); msgs.innerHTML = ''; renderChips(); hideHistory(); }
        function addMsg(role, text, extra) { var m = { role: role, text: text, ts: nowStr() }; if (extra) for (var k in extra) m[k] = extra[k]; if (cur) cur.messages.push(m); return m; }
        function persist() { if (!cur) return; cur.title = titleFor(cur); cur.type = classify(cur); cur.ts = nowStr(); cur.branch = (window.BZ_BRANCH || ''); convos = [cur].concat(convos.filter(function (c) { return c !== cur; })); saveConvos(); }
        function renderConvo() { msgs.innerHTML = ''; (cur && cur.messages || []).forEach(function (m) { bubble(m.role === 'user' ? 'user' : 'bot', fmt(m.text)); }); renderChips(); lucidify(); msgs.scrollTop = msgs.scrollHeight; }

        function openP() { if (!cur) newConvo(); panel.hidden = false; fab.classList.add('on'); refreshCtx(); fetchUsage(); renderUsage(); hideHistory(); lucidify(); setTimeout(function () { input.focus(); }, 60); }
        function closeP() { panel.hidden = true; fab.classList.remove('on'); }
        fab.addEventListener('click', function () { panel.hidden ? openP() : closeP(); });
        panel.querySelector('[data-close]').addEventListener('click', closeP);
        panel.querySelector('[data-new]').addEventListener('click', function () { if (busy) return; persist(); newConvo(); input.focus(); });
        panel.querySelector('[data-hist]').addEventListener('click', function () { persist(); showHistory(); });
        panel.querySelector('[data-histclose]').addEventListener('click', hideHistory);
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { e.stopPropagation(); if (!histEl.hidden) hideHistory(); else closeP(); } });

        // ── history view (grouped + sorted by type) ─────────────────────────────
        function showHistory() {
            input.style.height = 'auto';               // so the overlay's bottom inset still clears the bar
            var groups = {}, saved = convos.filter(function (c) { return c.messages && c.messages.length; });
            saved.forEach(function (c) { (groups[c.type] = groups[c.type] || []).push(c); });
            var keys = Object.keys(groups).sort();
            histList.innerHTML = keys.length ? keys.map(function (t) {
                return '<div class="bz-ai-hgrp">' + esc(t) + ' <span>(' + groups[t].length + ')</span></div>' + groups[t].map(function (c) {
                    return '<div class="bz-ai-hitem" data-id="' + esc(c.id) + '"><div class="bz-ai-hitem-x"><div class="bz-ai-hitem-t">' + esc(c.title) + '</div>' +
                        '<div class="bz-ai-hitem-m">' + esc(c.ts) + ' · ' + (c.messages ? c.messages.length : 0) + ' رسالة</div></div>' +
                        '<button class="bz-ai-hdel" data-del="' + esc(c.id) + '" title="حذف" aria-label="حذف">🗑</button></div>';
                }).join('');
            }).join('') : '<div class="bz-ai-hempty">لا محادثات محفوظة بعد</div>';
            histList.querySelectorAll('.bz-ai-hitem').forEach(function (it) {
                it.addEventListener('click', function (e) { if (e.target.closest('[data-del]')) return; if (busy) return; var c = convos.filter(function (x) { return x.id === it.getAttribute('data-id'); })[0]; if (c) { cur = c; renderConvo(); hideHistory(); } });
            });
            histList.querySelectorAll('[data-del]').forEach(function (b) {
                b.addEventListener('click', function (e) { e.stopPropagation(); if (busy) return; var id = b.getAttribute('data-del'); convos = convos.filter(function (x) { return x.id !== id; }); if (cur && cur.id === id) cur = null; saveConvos(); showHistory(); });
            });
            histEl.hidden = false; lucidify();
        }
        function hideHistory() { histEl.hidden = true; }

        function refreshCtx() { ctxEl.textContent = titleOf() + ' · فرع ' + (window.BZ_BRANCH || 'الدمام'); }
        function suggestions() {
            var p = location.pathname;
            if (/employees/.test(p)) return ['كم عدد الموظفين؟', 'من اقتربت إقامته من الانتهاء؟', 'أكمل خانات الجوال الفارغة بـ«غير متوفر»'];
            if (/oils/.test(p)) return ['ما إجمالي اللترات؟', 'أي مركبة تحتاج تغيير زيت؟'];
            if (/schedule/.test(p)) return ['كم سائقاً في الجدول؟', 'من نوع مركبته «دينا»؟'];
            if (/workshop/.test(p)) return ['لخّص أعمال الورشة', 'ما المركبات تحت الصيانة؟'];
            if (/incidents/.test(p)) return ['كم واقعة مفتوحة؟', 'أي مركبة تكرّرت حوادثها؟'];
            if (/washing/.test(p)) return ['من لم تُغسل مركبته بعد؟'];
            return ['كم عدد الموظفين في الجدول الأسبوعي؟', 'كم عدد المركبات؟', 'لخّص حالة الفرع'];
        }
        function renderChips() {
            chips.innerHTML = '';
            if (cur && cur.messages && cur.messages.length) return;
            suggestions().forEach(function (t) {
                var b = document.createElement('button'); b.type = 'button'; b.className = 'bz-ai-chip'; b.textContent = t;
                b.addEventListener('click', function () { input.value = t; submit(); });
                chips.appendChild(b);
            });
        }
        function fmt(t) { return esc(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>'); }
        function bubble(role, htmlStr) { var b = document.createElement('div'); b.className = 'bz-ai-msg ' + role; b.innerHTML = htmlStr; msgs.appendChild(b); msgs.scrollTop = msgs.scrollHeight; return b; }
        function typing(on) { if (on) typingEl = bubble('bot typing', '<span class="bz-ai-dots"><i></i><i></i><i></i></span>'); else if (typingEl) { typingEl.remove(); typingEl = null; } }

        form.addEventListener('submit', function (e) { e.preventDefault(); submit(); });
        input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); } });
        input.addEventListener('input', function () { input.style.height = 'auto'; input.style.height = Math.min(120, input.scrollHeight) + 'px'; });

        function currentGrid() { var ts = (typeof bzFindDataTables === 'function') ? bzFindDataTables() : []; return ts && ts[0] ? bzAIGrid(ts[0]) : null; }

        function submit() {
            if (busy) return;
            var text = (input.value || '').trim(); if (!text) return;
            if (!cur) newConvo();
            input.value = ''; input.style.height = 'auto'; busy = true; hideHistory();
            bubble('user', fmt(text)); addMsg('user', text); renderChips(); persist();
            typing(true);
            var grid = currentGrid();
            var fields = (typeof bzAIFormFields === 'function') ? bzAIFormFields() : [];
            var aoa = grid ? [grid.headers].concat(grid.rows) : [];
            var hist = (cur.messages || []).slice(0, -1).slice(-5).map(function (m) { return { role: m.role === 'user' ? 'user' : 'model', text: m.text }; });
            fetch('/api/ai/chat', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, tab: (window.BZ_SNAP_TAB || ''), title: titleOf(), table: aoa, fields: fields.map(function (f) { return { label: f.label, value: f.value }; }), history: hist })
            }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }, function () { return { ok: r.ok, d: {} }; }); })
                .then(function (res) {
                    typing(false);
                    var d = res.d || {};
                    if (d.usage) { usage = d.usage; renderUsage(); }
                    if (!res.ok) { var em = d.error || 'تعذّر تنفيذ الطلب'; bubble('bot', fmt('⚠ ' + em)); addMsg('model', '⚠ ' + em); persist(); return; }
                    var reply = d.reply || '';
                    bubble('bot', fmt(reply || '(لا يوجد رد)')); lucidify();
                    var acts = d.table_actions || [];
                    addMsg('model', reply, acts.length ? { edits: true } : null); persist();
                    if (acts.length) proposeEdits(grid, fields, acts, d.frozen);
                })
                .catch(function () { typing(false); bubble('bot', 'تعذّر الاتصال بالمساعد.'); addMsg('model', 'تعذّر الاتصال بالمساعد.'); persist(); })
                .then(function () { busy = false; input.focus(); });
        }

        function proposeEdits(grid, fields, actions, frozen) {
            var plan = bzAIPlan(grid, fields, actions);
            if (!plan.steps.length) { bubble('bot', plan.errors.length ? ('تعذّر تطبيق المقترح: ' + esc(plan.errors[0])) : 'لا تعديلات قابلة للتطبيق.'); return; }
            var card = document.createElement('div'); card.className = 'bz-ai-apply';
            card.innerHTML = '<div class="bz-ai-apply-hd">✏️ تعديلات مقترحة (' + plan.steps.length + ')</div>' +
                '<ul class="bz-ai-diff">' + plan.diff.slice(0, 14).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + (plan.diff.length > 14 ? '<li>…</li>' : '') + '</ul>' +
                (plan.errors.length ? '<div class="bz-ai-warn">⚠ تجاهُل ' + plan.errors.length + ' إجراء غير صالح</div>' : '') +
                '<div class="bz-ai-apply-acts"><button class="bz-ai-btn ghost" data-x type="button">تجاهل</button><button class="bz-ai-btn go" data-go type="button">تطبيق</button></div>';
            msgs.appendChild(card); msgs.scrollTop = msgs.scrollHeight; lucidify();
            card.querySelector('[data-x]').addEventListener('click', function () { card.querySelector('.bz-ai-apply-acts').innerHTML = '<span class="bz-ai-mut">تم التجاهل</span>'; });
            card.querySelector('[data-go]').addEventListener('click', function () {
                var run = function () {
                    var n = 0; plan.steps.forEach(function (s) { try { s(); n++; } catch (e) { } });
                    card.querySelector('.bz-ai-apply-acts').innerHTML = '<span class="bz-ai-ok">✓ طُبّقت — راجع الصفحة ثم احفظها</span>';
                    if (window.showToast) showToast('طُبّقت ' + n + ' تعديلاً ✓ — لا تنسَ حفظ الصفحة', 'success');
                };
                if (frozen && window.bzConfirm) { window.bzConfirm('هذا فرع الدمام (بيانات مرجعية مجمّدة).\nتطبيق ' + plan.steps.length + ' تعديلاً؟').then(function (ok) { if (ok) run(); }); }
                else run();
            });
        }
    } catch (e) { /* non-critical */ }
}

// =============================================================================
// GUIDED TOUR (جولة تعريفية) — a one-time spotlight walkthrough for new users,
// re-launchable any time from the ❓ button. Non-blocking, RTL, mobile-friendly.
// =============================================================================
window.bzTour = function (rawSteps) {
    var steps = (rawSteps || []).map(function (s) {
        return { el: (typeof s.el === 'string') ? document.querySelector(s.el) : s.el, title: s.title, body: s.body };
    }).filter(function (s) { return s.el && s.el.offsetParent !== null; });
    if (!steps.length) return;
    if (document.querySelector('.bz-tour')) return;
    var i = 0;
    var ov = document.createElement('div'); ov.className = 'bz-tour'; ov.setAttribute('dir', 'rtl');
    ov.innerHTML =
        '<div class="bz-tour-spot"></div>' +
        '<div class="bz-tour-pop" role="dialog" aria-live="polite"><div class="bz-tour-ttl"></div><div class="bz-tour-body"></div>' +
        '<div class="bz-tour-foot"><span class="bz-tour-dots"></span><div class="bz-tour-btns">' +
        '<button class="bz-tour-skip" type="button">تخطّي</button><button class="bz-tour-prev" type="button">السابق</button>' +
        '<button class="bz-tour-next" type="button">التالي</button></div></div></div>';
    document.body.appendChild(ov);
    var spot = ov.querySelector('.bz-tour-spot'), pop = ov.querySelector('.bz-tour-pop'),
        ttl = ov.querySelector('.bz-tour-ttl'), body = ov.querySelector('.bz-tour-body'),
        dots = ov.querySelector('.bz-tour-dots'), prevB = ov.querySelector('.bz-tour-prev'), nextB = ov.querySelector('.bz-tour-next');
    function done() { try { localStorage.setItem('bz_tour_done', '1'); } catch (e) { } ov.remove(); document.removeEventListener('keydown', onKey); window.removeEventListener('resize', render); window.removeEventListener('scroll', render, true); }
    function onKey(e) { if (e.key === 'Escape') { e.stopPropagation(); done(); } else if (e.key === 'Enter' || e.key === 'ArrowLeft') go(1); else if (e.key === 'ArrowRight') go(-1); }
    function go(d) { i += d; if (i < 0) i = 0; if (i >= steps.length) { done(); return; } render(); }
    function place() {
        var s = steps[i], r = s.el.getBoundingClientRect(), pad = 8;
        spot.style.cssText = 'top:' + (r.top - pad) + 'px;left:' + (r.left - pad) + 'px;width:' + (r.width + pad * 2) + 'px;height:' + (r.height + pad * 2) + 'px;';
        var ph = pop.offsetHeight || 150, below = r.bottom + 12;
        var top = (below + ph < window.innerHeight - 8) ? below : Math.max(8, r.top - 12 - ph);
        var left = Math.min(Math.max(12, r.left + r.width / 2 - pop.offsetWidth / 2), window.innerWidth - pop.offsetWidth - 12);
        pop.style.top = top + 'px'; pop.style.left = left + 'px';
    }
    function render() {
        var s = steps[i];
        ttl.textContent = s.title; body.textContent = s.body;
        dots.innerHTML = steps.map(function (_, k) { return '<i class="' + (k === i ? 'on' : '') + '"></i>'; }).join('');
        prevB.style.visibility = i === 0 ? 'hidden' : 'visible';
        nextB.textContent = i === steps.length - 1 ? 'إنهاء' : 'التالي';
        try { s.el.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) { }
        setTimeout(place, 240);
    }
    ov.querySelector('.bz-tour-skip').addEventListener('click', done);
    prevB.addEventListener('click', function () { go(-1); });
    nextB.addEventListener('click', function () { go(1); });
    spot.addEventListener('click', function () { go(1); });
    document.addEventListener('keydown', onKey);
    window.addEventListener('resize', render);
    window.addEventListener('scroll', render, true);
    render();
};

function injectHelpTour() {
    try {
        var topbar = document.querySelector('.bz-topbar');
        if (!topbar || /\/(login|lock)/.test(location.pathname)) return;
        var actions = topbar.querySelector('.bz-actions');
        if (actions && !document.getElementById('bzHelpBtn')) {
            var b = document.createElement('button');
            b.id = 'bzHelpBtn'; b.type = 'button'; b.className = 'bz-icon-btn';
            b.title = 'جولة تعريفية'; b.setAttribute('aria-label', 'جولة تعريفية'); b.textContent = '❓';
            b.addEventListener('click', startTour);
            actions.insertBefore(b, actions.firstChild);
        }
        var seen = false; try { seen = !!localStorage.getItem('bz_tour_done'); } catch (e) { }
        if (!seen) setTimeout(startTour, 1500);   // auto-run once for new users
    } catch (e) { /* non-critical */ }
    function startTour() {
        window.bzTour([
            { el: '.bz-sidebar nav, .bz-topbar .bz-nav', title: 'القائمة الرئيسية', body: 'كل تبويبات النظام هنا: الجدول الأسبوعي، الموظفون، الورشة، الحوادث، التحليلات والمزيد.' },
            { el: '#bzBranchWrap, .bz-branch-wrap, .bz-branch-badge', title: 'الفرع النشط', body: 'بدّل بين الفروع لعرض وتحرير بيانات كل فرع على حدة بمعزل عن غيره.' },
            { el: '#bzTopSearch', title: 'بحث سريع', body: 'ابحث فوراً داخل بيانات الصفحة الحالية.' },
            { el: '#bzAiFab', title: 'المساعد الذكي', body: 'اسأله عن أعداد بياناتك أو اطلب منه تعبئة/تعديل الجداول — يقترح، تراجع، ثم تحفظ بنفسك.' },
            { el: '.bz-dock', title: 'المشاركة والبريد', body: 'أرسل أي جدول أو تقرير بالبريد أو واتساب، أو صدّره Excel / PDF.' },
            { el: '#darkModeToggle', title: 'الوضع الليلي/النهاري', body: 'بدّل مظهر الموقع بين الفاخر الداكن والفاتح بضغطة.' },
            { el: '#bzHelpBtn', title: 'أعد الجولة أي وقت', body: 'تقدر تعيد هذه الجولة التعريفية من هنا متى احتجت. بالتوفيق!' }
        ]);
    }
}

// --- Global Table Auto-fill from FleetData ---
document.addEventListener('change', async function(e) {
    if (e.target.tagName !== 'INPUT') return;
    if (!e.target.closest('table')) return;
    
    if (!window.FleetData) return;
    try { await window.FleetData.load(); } catch(err){}

    const val = e.target.value.trim();
    if (!val || val.length < 3) return;

    let rec = window.FleetData.byPlate(val) || window.FleetData.byName(val);
    if (!rec && val.length >= 4) {
        rec = window.FleetData.all().find(d => (d.plate && d.plate.includes(val)) || (d.name && d.name.includes(val)));
    }

    if (!rec) return;

    const tr = e.target.closest('tr');
    if (!tr) return;

    const table = tr.closest('table');
    let ths = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
    if (ths.length === 0) {
        const prev = tr.previousElementSibling;
        if (prev) ths = Array.from(prev.querySelectorAll('td')).map(td => td.textContent.trim());
    }

    const tds = Array.from(tr.querySelectorAll('td'));

    tds.forEach((td, i) => {
        const input = td.querySelector('input');
        if (!input || input === e.target) return;
        
        const header = (ths[i] || '').toLowerCase();
        
        if ((header.includes('لوحة') || header.includes('لوحه')) && !input.value) {
            input.value = rec.plate || '';
        } else if ((header.includes('اسم') || header.includes('سائق') || header.includes('مستخدم')) && !input.value) {
            input.value = rec.name || '';
        } else if ((header.includes('مركبة') || header.includes('نوع') || header.includes('سيارة')) && !input.value) {
            input.value = rec.car || '';
        } else if ((header.includes('إقامة') || header.includes('اقامة')) && !input.value) {
            input.value = rec.iqama || '';
        } else if ((header.includes('وظيفي') || header.includes('رقم')) && !input.value && header.includes('وظيفي')) {
            input.value = rec.empid || '';
        } else if (header.includes('وظيفة') && !input.value) {
            input.value = rec.job || '';
        } else if (header.includes('بطاقة السائق') && !input.value) {
            input.value = rec.drivercard || '';
        } else if (header.includes('جوال') && !input.value) {
            input.value = rec.phone || '';
        } else if (header.includes('موديل') && !input.value) {
            input.value = rec.model || '';
        } else if (header.includes('طبالي') && !input.value) {
            input.value = rec.pallets || '';
        } else if (header.includes('حمولة') && !input.value) {
            input.value = rec.load || '';
        } else if (header.includes('تسلسلي') && !input.value) {
            input.value = rec.vserial || '';
        } else if (header.includes('فحص') && !input.value) {
            input.value = rec.inspect || '';
        } else if (header.includes('رخصة السير') && !input.value) {
            input.value = rec.license || '';
        } else if (header.includes('تشغيل') && !input.value) {
            input.value = rec.opcard || '';
        } else if (header.includes('ملاحظات') && !input.value) {
            // Can be empNotes or notes depending on if it's in the employee section or vehicle section
            // We just use notes as default if there's no way to distinguish
            input.value = rec.notes || rec.empNotes || '';
        }
    });
});


/* ============================================================
   BIN ZOMAH ERP - ADVANCED FEATURES (Timeline, Alerts, Spotlight)
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Setup Spotlight Search
    const searchInput = document.getElementById('bzTopSearch');
    if (searchInput) {
        // Create Dropdown Container
        const dropdown = document.createElement('div');
        dropdown.id = 'bzSpotlightDropdown';
        dropdown.style.cssText = `
            position: absolute; top: 50px; left: 0; right: 0;
            background: var(--d-card); border: 1px solid var(--gold); border-radius: 8px;
            box-shadow: var(--shadow); z-index: 10000; display: none; max-height: 400px; overflow-y: auto;
        `;
        searchInput.parentElement.style.position = 'relative';
        searchInput.parentElement.appendChild(dropdown);

        searchInput.addEventListener('input', async (e) => {
            const q = e.target.value.trim().toLowerCase();
            if (!q) { dropdown.style.display = 'none'; return; }
            
            const fleet = await window.FleetData.load();
            const results = fleet.filter(d => 
                (d.name && d.name.toLowerCase().includes(q)) || 
                (d.plate && d.plate.toLowerCase().includes(q)) || 
                (d.iqama && d.iqama.includes(q))
            ).slice(0, 10);
            
            if (results.length === 0) {
                dropdown.innerHTML = '<div style="padding:10px;text-align:center;color:var(--d-muted);">لا توجد نتائج تطابق بحثك</div>';
            } else {
                dropdown.innerHTML = results.map(d => `
                    <div class="spotlight-item" style="padding:10px; border-bottom:1px solid var(--d-border); cursor:pointer; display:flex; justify-content:space-between; align-items:center;"
                         onclick="openTimeline(${d.id || `'${d.plate}'`})">
                        <div>
                            <div style="color:var(--gold); font-weight:bold;">${d.name || '---'}</div>
                            <div style="font-size:0.8rem; color:var(--d-muted);">${d.car || ''} - ${d.iqama || ''}</div>
                        </div>
                        <div style="direction:ltr; background:var(--d-bg); padding:2px 6px; border-radius:4px; font-size:0.9rem;">
                            ${d.plate || '---'}
                        </div>
                    </div>
                `).join('');
            }
            dropdown.style.display = 'block';
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.parentElement.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    // 2. Setup Smart Alerts Modal
    const bell = document.getElementById('bzBell');
    if (bell) {
        bell.href = 'javascript:void(0)';
        bell.addEventListener('click', openAlertsModal);
    }
});

function calculateDaysLeft(dateStr) {
    if (!dateStr) return null;
    const exp = new Date(dateStr);
    if (isNaN(exp)) return null;
    const now = new Date();
    const diffTime = exp - now;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

async function openAlertsModal() {
    if(window.showToast) window.showToast('جاري فحص التواريخ...', 'info');
    const fleet = await window.FleetData.load();
    let html = '';
    let alertsCount = 0;
    
    fleet.forEach(d => {
        const fields = [
            { key: 'inspect', label: 'الفحص الدوري' },
            { key: 'license', label: 'رخصة السير' },
            { key: 'opcard', label: 'بطاقة التشغيل' },
            { key: 'iqama', label: 'الإقامة' },
            { key: 'drivercard', label: 'بطاقة السائق' }
        ];
        
        let localAlerts = [];
        fields.forEach(f => {
            const days = calculateDaysLeft(d[f.key]);
            if (days !== null && days <= 30) {
                const color = days < 0 ? 'var(--red)' : (days <= 7 ? 'var(--amber)' : 'var(--yellow)');
                const txt = days < 0 ? `منتهي منذ ${Math.abs(days)} يوم` : `ينتهي خلال ${days} يوم`;
                localAlerts.push(`<div style="color:${color}; font-size:0.9rem;">⚠️ <b>${f.label}:</b> ${d[f.key]} (${txt})</div>`);
                alertsCount++;
            }
        });
        
        if (localAlerts.length > 0) {
            html += `
            <div style="background:var(--d-bg); padding:10px; border-radius:6px; margin-bottom:10px; border-right:4px solid var(--red);">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <strong style="color:var(--gold)">${d.name}</strong>
                    <span style="direction:ltr;">${d.plate}</span>
                </div>
                ${localAlerts.join('')}
            </div>`;
        }
    });

    if (alertsCount === 0) {
        html = '<div style="text-align:center; padding:30px; color:var(--green); font-size:1.2rem;">✅ جميع الرخص والوثائق سارية المفعول (لا توجد انتهاءات قريبة).</div>';
    }

    const modalHtml = `
    <div id="alertsModal" class="modal active">
        <div class="modal-content" style="max-width:600px; max-height:80vh; display:flex; flex-direction:column;">
            <div class="modal-header">
                <h3>🔔 رادار التنبيهات الذكي</h3>
            </div>
            <div style="flex:1; overflow-y:auto; padding:15px;">
                <p style="color:var(--d-muted); margin-bottom:15px; font-size:0.9rem;">يعرض هذا الرادار تلقائياً أي وثيقة انتهت أو ستنتهي خلال 30 يوماً لجميع الأسطول.</p>
                ${html}
            </div>
            <div class="modal-footer">
                <button class="btn-outline" onclick="document.getElementById('alertsModal').remove()">إغلاق</button>
            </div>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

async function openTimeline(identifier) {
    // Hide spotlight
    const dp = document.getElementById('bzSpotlightDropdown');
    if (dp) dp.style.display = 'none';
    
    if(window.showToast) window.showToast('جاري استدعاء سجل المركبة...', 'info');
    const fleet = await window.FleetData.load();
    const d = fleet.find(x => x.id == identifier || x.plate == identifier);
    if (!d) return;

    // Build timeline events based on integration logic
    let events = [];
    events.push({ date: 'الآن', title: 'السجل الشامل', desc: 'مسجل في السجل الأساسي' });
    
    const html = `
    <div id="timelineModal" class="modal active">
        <div class="modal-content" style="max-width:500px;">
            <div class="modal-header">
                <h3>السجل الزمني للمركبة</h3>
            </div>
            <div style="padding:15px; text-align:center; border-bottom:1px solid var(--d-border);">
                <h2 style="color:var(--gold); margin:0;">${d.name}</h2>
                <div style="direction:ltr; font-size:1.2rem; margin:5px 0;">${d.plate}</div>
                <div style="color:var(--d-muted);">${d.car || '---'}</div>
            </div>
            <div style="padding:15px;">
                <div style="display:flex; flex-direction:column; gap:15px; position:relative; padding-right:20px; border-right:2px solid var(--gold);">
                    <div style="position:relative;">
                        <div style="position:absolute; right:-27px; top:2px; background:var(--d-bg); border:2px solid var(--gold); border-radius:50%; width:12px; height:12px;"></div>
                        <div style="color:var(--d-muted); font-size:0.8rem;">تاريخ الفحص الدوري</div>
                        <div style="font-weight:bold; color:var(--text);">${d.inspect || 'غير مسجل'}</div>
                    </div>
                    <div style="position:relative;">
                        <div style="position:absolute; right:-27px; top:2px; background:var(--d-bg); border:2px solid var(--blue); border-radius:50%; width:12px; height:12px;"></div>
                        <div style="color:var(--d-muted); font-size:0.8rem;">تاريخ رخصة السير</div>
                        <div style="font-weight:bold; color:var(--text);">${d.license || 'غير مسجل'}</div>
                    </div>
                    <div style="position:relative;">
                        <div style="position:absolute; right:-27px; top:2px; background:var(--d-bg); border:2px solid var(--green); border-radius:50%; width:12px; height:12px;"></div>
                        <div style="color:var(--d-muted); font-size:0.8rem;">تاريخ بطاقة التشغيل</div>
                        <div style="font-weight:bold; color:var(--text);">${d.opcard || 'غير مسجل'}</div>
                    </div>
                    <div style="position:relative;">
                        <div style="position:absolute; right:-27px; top:2px; background:var(--d-bg); border:2px solid var(--purple); border-radius:50%; width:12px; height:12px;"></div>
                        <div style="color:var(--d-muted); font-size:0.8rem;">انتهاء الإقامة</div>
                        <div style="font-weight:bold; color:var(--text);">${d.iqama || 'غير مسجل'}</div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-outline" onclick="document.getElementById('timelineModal').remove()">إغلاق</button>
            </div>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', html);
}
