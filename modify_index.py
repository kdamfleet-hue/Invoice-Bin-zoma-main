import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

new_html = """
    <div class="landing-hero">
        <div class="hero-top">
            <h1 class="hero-title">سجلٌ واحد، يدير أسطولك بأكمله</h1>
            <p class="hero-subtitle">كل حقل يُكتب مرة واحدة، ليتردد صداه فوراً في كل قسم من أقسام الموقع — دون تكرار، ودون انتظار.</p>
            <div class="hero-diamond">◆</div>
        </div>
        
        <div class="hero-stats">
            <div class="stat-item"><div class="stat-num">١٠٤</div><div class="stat-lbl">مجدولون هذا الأسبوع</div></div>
            <div class="stat-item"><div class="stat-num">١٢٨</div><div class="stat-lbl">مركبة نشطة</div></div>
            <div class="stat-item"><div class="stat-num">٪٩١</div><div class="stat-lbl">إنجاز الغسيل الشهري</div></div>
            <div class="stat-item"><div class="stat-num">٦</div><div class="stat-lbl">بانتظار التوزيع</div></div>
        </div>
    </div>

    <div class="landing-section">
        <div class="section-label english-tracked">AUTO-TRACE</div>
        <h2 class="section-title">من اسمٍ واحد... إلى سجلٍ كامل</h2>
        <div class="hex-grid">
            <div class="hex-item"><div class="hex-circle"><i data-lucide="shield-check"></i></div><span>اسم السائق</span><p>محمد العتيبي</p></div>
            <div class="hex-item"><div class="hex-circle"><i data-lucide="rectangle-horizontal"></i></div><span>اللوحة</span><p>أ ب ج ١٢٣٤</p></div>
            <div class="hex-item"><div class="hex-circle"><i data-lucide="truck"></i></div><span>الموديل</span><p>دينا ٢٠٢٤</p></div>
            <div class="hex-item"><div class="hex-circle"><i data-lucide="check-circle"></i></div><span>مكتمل</span><p>١٧ / ١٧</p></div>
            <div class="hex-item"><div class="hex-circle"><i data-lucide="clock"></i></div><span>الفحص</span><p>٢/١١/٢٠٢٦</p></div>
            <div class="hex-item"><div class="hex-circle"><i data-lucide="credit-card"></i></div><span>الإقامة</span><p>٢٤٧٧xxxxxx</p></div>
        </div>
    </div>

    <div class="landing-section">
        <div class="section-label english-tracked">SECTIONS</div>
        <h2 class="section-title">أقسام النظام</h2>
        <div class="sections-list">
            <div class="sl-item"><div class="sl-num">I</div><div class="sl-text"><h3>السجل الشامل</h3><p>لوحة التحكم المركزية بكل بيانات السائق والمركبة، مع مؤشرات الترابط عبر كل الأقسام.</p></div></div>
            <div class="sl-item"><div class="sl-num">II</div><div class="sl-text"><h3>الجدول الأسبوعي</h3><p>الجدول الرئيسي، الاسبير، الإجازات، ورادار غير المجدولين تلقائياً.</p></div></div>
            <div class="sl-item"><div class="sl-num">III</div><div class="sl-text"><h3>جدول الغسيل</h3><p>تتبع دقيق لدورات الغسيل مع تعبئة تلقائية لبيانات اللوحة والسائق.</p></div></div>
            <div class="sl-item"><div class="sl-num">IV</div><div class="sl-text"><h3>الزيوت والفلاتر</h3><p>متابعة اللترات المستهلكة ونوع الفلاتر لكل مركبة عبر استدعاء اللوحة.</p></div></div>
            <div class="sl-item"><div class="sl-num">V</div><div class="sl-text"><h3>طلب شراء وإصلاح</h3><p>نماذج وأوامر رسمية بتنسيق طباعة مخصص لحالة المركبة وأجزائها.</p></div></div>
            <div class="sl-item"><div class="sl-num">VI</div><div class="sl-text"><h3>الحوادث وتسليم العهد</h3><p>توثيق المسؤولية ومحاضر التسليم، مرتبطة مباشرة بالسجل الشامل.</p></div></div>
            <div class="sl-item"><div class="sl-num">VII</div><div class="sl-text"><h3>التتبع وأبشر</h3><p>استيراد ملف أبشر ومزامنة كافة تبويبات الموقع في لحظة واحدة.</p></div></div>
            <div class="sl-item"><div class="sl-num">VIII</div><div class="sl-text"><h3>الإحصائيات</h3><p>رسوم بيانية لأداء الفرع: الغسيل، الزيوت، والمصروفات الشهرية.</p></div></div>
        </div>
    </div>

    <div class="landing-split">
        <div class="split-left">
            <h3 class="split-title">استدعاء مركبة</h3>
            
            <div class="clean-form" id="invoiceArea">
                <div class="cf-row">
                    <label for="driverName">اسم السائق</label>
                    <input type="text" id="driverName" list="driversList" placeholder="اكتب للبحث..." onchange="autofillDriver()">
                    <datalist id="driversList"></datalist>
                </div>
                <div class="cf-row">
                    <label for="plateNum">رقم اللوحة</label>
                    <input type="text" id="plateNum" list="platesList" placeholder="أ ب ج 1234" onchange="autofillByPlate()">
                    <datalist id="platesList"></datalist>
                </div>
                <div class="cf-row">
                    <label for="carType">نوع المركبة</label>
                    <input type="text" id="carType" placeholder="مثال: دينا 2024">
                </div>
                <div class="cf-row">
                    <label for="iqamaNum">رقم الإقامة</label>
                    <input type="text" id="iqamaNum" placeholder="اكتب للبحث...">
                </div>
                
                <!-- Hidden fields required for existing JS logic to not break -->
                <div style="display:none;">
                    <select id="requestType"><option value="أخرى">أخرى</option></select>
                    <input type="date" id="invoiceDate">
                    <div id="invoiceBranch">فرع الدمام</div>
                    <textarea id="desc"></textarea>
                </div>
            </div>
            
            <div class="clean-actions" style="margin-top: 2.5rem; display: flex; gap: 1rem;">
                <button class="btn-clean-gold" onclick="generateExcel()">تصدير الفاتورة</button>
                <button class="btn-clean" onclick="clearInvoiceForm()">إفراغ</button>
                <button class="btn-clean" onclick="openInvoiceShare()">مشاركة</button>
            </div>
        </div>
        
        <div class="split-right">
            <h3 class="split-title">آخر النشاطات</h3>
            <div class="activity-log">
                <div class="al-item"><span class="al-time">١٢ د</span><span class="al-desc">مزامنة ملف أبشر — ٣ مركبات جديدة</span></div>
                <div class="al-item"><span class="al-time">٤٥ د</span><span class="al-desc">تحديث بيانات خالد الشمري</span></div>
                <div class="al-item"><span class="al-time">٩:١٠ ص</span><span class="al-desc">سائق غير مجدول: سعيد الغامدي</span></div>
                <div class="al-item"><span class="al-time">أمس</span><span class="al-desc">طباعة أمر شراء — فرع المحطة</span></div>
            </div>
        </div>
    </div>
    
    <footer class="landing-footer">
        .BIN ZOMAH INTERNATIONAL TRADING & DEVELOPMENT CO. LTD
    </footer>
"""

start_marker = '<div class="header-container">'
end_marker = '<!-- Email modal is at the bottom'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_content = html[:start_idx] + new_html + "\n\n    " + html[end_idx:]
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Replaced successfully.")
else:
    print("Markers not found.")
