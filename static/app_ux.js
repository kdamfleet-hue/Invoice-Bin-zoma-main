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
};\n\n
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
                         onclick="openTimeline('${d.plate || d.id}')">
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
                localAlerts.push(`<div style="color:${color}; font-size:0.9rem;">⚠️ <b>${f.label}:</b> ${d[f.key] || ''} (${txt})</div>`);
                alertsCount++;
            }
        });
        
        if (localAlerts.length > 0) {
            html += `
            <div style="background:var(--d-bg); padding:10px; border-radius:6px; margin-bottom:10px; border-right:4px solid var(--red);">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <strong style="color:var(--gold)">${d.name || ''}</strong>
                    <span style="direction:ltr;">${d.plate || ''}</span>
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
    
    const html = `
    <div id="timelineModal" class="modal active">
        <div class="modal-content" style="max-width:500px;">
            <div class="modal-header">
                <h3>السجل الزمني للمركبة</h3>
            </div>
            <div style="padding:15px; text-align:center; border-bottom:1px solid var(--d-border);">
                <h2 style="color:var(--gold); margin:0;">${d.name || '---'}</h2>
                <div style="direction:ltr; font-size:1.2rem; margin:5px 0;">${d.plate || '---'}</div>
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
