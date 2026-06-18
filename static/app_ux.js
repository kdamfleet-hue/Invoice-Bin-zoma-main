/**
 * GLOBAL UX & UI CONTROLLER
 * Handles Theme Toggling, Topographic Background, Toasts, Progress Bar,
 * Page Transitions, Idle Session Timeout, and Bilingual Translation.
 */

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
    initThemeToggle();
    injectTopographicBackground();
    injectUXContainers();
    initPageTransition();
    wrapFetchForProgress();
    initIdleTimeout();
    initLanguageTranslation();
});

// --- Theme Management ---
function initThemeToggle() {
    const savedTheme = localStorage.getItem('darkMode');
    // Default to dark mode for a professional look
    if (savedTheme === 'false') {
        document.body.classList.remove('dark-mode');
        document.documentElement.classList.remove('dark-mode');
        updateToggleButtons(false);
    } else {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
        updateToggleButtons(true);
    }
}

window.toggleDarkMode = function() {
    document.body.classList.toggle('dark-mode');
    document.documentElement.classList.toggle('dark-mode');
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
        _promise = fetch('/static/fleet_data.json')
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
        el.innerHTML = (tag === 'select' ? '<option value=""></option>' : '') +
            records().map(function (d) {
                const label = window.escapeHtml(d.name);
                return '<option value="' + label + '"></option>';
            }).join('');
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
        nameEl.addEventListener('change', apply);
        nameEl.addEventListener('input', apply);
    }

    return { load: load, records: records, byName: byName, byPlate: byPlate, byIqama: byIqama, fillDatalist: fillDatalist, attachAutofill: attachAutofill };
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
    overlay.addEventListener('click', (e) => { if (e.target === overlay || e.target.hasAttribute('data-x')) close(); });

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
