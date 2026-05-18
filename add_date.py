import os, re

files_to_patch = [
    r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\index.html',
    r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\index.html'
]

html_input_date = """        <!-- 4. نوع الطلب -->
        <div class="card card-brown">
            <label for="requestType">نوع الطلب</label>
            <select id="requestType">
                <option value="صيانة دورية">صيانة دورية</option>
                <option value="إصلاح عطل">إصلاح عطل</option>
                <option value="إصلاح بنشر">إصلاح بنشر</option>
                <option value="تغيير قطع غيار">تغيير قطع غيار</option>
                <option value="غيار زيت">غيار زيت</option>
                <option value="أخرى">أخرى</option>
            </select>
        </div>

        <!-- 4.5. التاريخ -->
        <div class="card card-olive">
            <label for="invoiceDate">التاريخ</label>
            <input type="date" id="invoiceDate">
        </div>"""

for filepath in files_to_patch:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add HTML input
    if 'id="invoiceDate"' not in content:
        content = re.sub(r'<!-- 4\. نوع الطلب -->.*?</div>', html_input_date, content, flags=re.DOTALL)
    
    # 2. Set default date
    if 'document.getElementById(\'invoiceDate\').valueAsDate = new Date();' not in content:
        content = content.replace('function calcTotal() {', "window.addEventListener('load', () => { document.getElementById('invoiceDate').valueAsDate = new Date(); });\n\n        function calcTotal() {")
    
    # 3. Add invoiceDate to JS
    if "const invoiceDate" not in content:
        content = content.replace("const req = document.getElementById('requestType').value;", "const req = document.getElementById('requestType').value;\n            const invoiceDate = document.getElementById('invoiceDate').value;")
    
    # 4. Modify setInfo section
    old_setinfo = """            setInfo('B8', 'اسم السائق', 'C8', driver);
            setInfo('D8', 'رقم اللوحة', 'E8', plate);
            setInfo('B9', 'نوع السيارة', 'C9', car);
            setInfo('D9', 'نوع الطلب', 'E9', req);
            ws.mergeCells('B8:B8'); ws.mergeCells('C8:C8'); ws.mergeCells('D8:D8'); ws.mergeCells('E8:F8');
            ws.mergeCells('B9:B9'); ws.mergeCells('C9:C9'); ws.mergeCells('D9:D9'); ws.mergeCells('E9:F9');

            ws.getRow(11).height = 30;
            const headers = ['م', 'الوصف / البيان', 'الكمية', 'السعر الإفرادي', 'المبلغ'];
            const hCols = ['B', 'C', 'D', 'E', 'F'];
            for(let i=0; i<headers.length; i++) {
                const c = ws.getCell(hCols[i] + '11');
                c.value = headers[i]; c.font = { name: 'Cairo', size: 11, bold: true, color: { argb: W } }; c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2C4A6E' } }; c.alignment = { horizontal: 'center', vertical: 'middle' }; c.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
            }

            ws.getRow(12).height = 35;
            const data = [1, desc, parseFloat(qty), parseFloat(price), parseFloat(subtotal)];
            for(let i=0; i<data.length; i++) {
                const c = ws.getCell(hCols[i] + '12');
                c.value = data[i]; c.font = { name: 'Cairo', size: 11, color: { argb: 'FF1A1A2E' } }; c.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true }; c.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
                if(i > 1) c.numFmt = '#,##0.00';
            }

            function addTotalRow(r, lbl, val, bold, color, fill) {
                ws.getRow(r).height = 35; ws.mergeCells(`B${r}:E${r}`);
                const lCell = ws.getCell(`B${r}`);
                lCell.value = lbl; lCell.font = { name: 'Cairo', size: 12, bold: true, color: { argb: color } }; lCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: fill } }; lCell.alignment = { horizontal: 'left', vertical: 'middle' }; lCell.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
                const vCell = ws.getCell(`F${r}`);
                vCell.value = parseFloat(val); vCell.font = { name: 'Cairo', size: bold ? 14 : 12, bold: bold, color: { argb: color } }; vCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: fill } }; vCell.alignment = { horizontal: 'center', vertical: 'middle' }; vCell.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }; vCell.numFmt = '#,##0.00';
            }

            addTotalRow(13, "المبلغ الإجمالي (قبل الضريبة)", subtotal, false, P, 'FFF9FAFB');
            addTotalRow(14, "ضريبة القيمة المضافة (15%)", tax, false, 'FFC0392B', 'FFFFF9F9');
            addTotalRow(15, "المجموع الكلي (مع الضريبة)", total, true, W, P);

            ws.getRow(18).height = 25;
            ws.getCell('B18').value = "توقيع السائق"; ws.getCell('F18').value = "اعتماد الإدارة";
            [ws.getCell('B18'), ws.getCell('F18')].forEach(c => { c.font = { name: 'Cairo', size: 11, bold: true, color: { argb: P } }; c.alignment = { horizontal: 'center', vertical: 'middle' }; });
            ws.getRow(19).height = 40;
            const bBottom = { bottom: { style: 'medium', color: { argb: P } } };
            ws.getCell('B19').border = bBottom; ws.getCell('F19').border = bBottom;"""
    
    # We must match exactly. The indentation might have slight differences if it's dynamic. We'll use regex.
    old_setinfo_pattern = r"setInfo\('B8', 'اسم السائق', 'C8', driver\);.*?ws\.getCell\('F19'\)\.border = bBottom;"
    
    new_setinfo = """setInfo('B8', 'اسم السائق', 'C8', driver);
            setInfo('D8', 'التاريخ', 'E8', invoiceDate);
            setInfo('B9', 'نوع السيارة', 'C9', car);
            setInfo('D9', 'رقم اللوحة', 'E9', plate);
            setInfo('B10', 'نوع الطلب', 'C10', req);
            
            ws.getRow(10).height = 25;
            ws.mergeCells('B8:B8'); ws.mergeCells('C8:C8'); ws.mergeCells('D8:D8'); ws.mergeCells('E8:F8');
            ws.mergeCells('B9:B9'); ws.mergeCells('C9:C9'); ws.mergeCells('D9:D9'); ws.mergeCells('E9:F9');
            ws.mergeCells('B10:B10'); ws.mergeCells('C10:F10');

            ws.getRow(12).height = 30;
            const headers = ['م', 'الوصف / البيان', 'الكمية', 'السعر الإفرادي', 'المبلغ'];
            const hCols = ['B', 'C', 'D', 'E', 'F'];
            for(let i=0; i<headers.length; i++) {
                const c = ws.getCell(hCols[i] + '12');
                c.value = headers[i]; c.font = { name: 'Cairo', size: 11, bold: true, color: { argb: W } }; c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF2C4A6E' } }; c.alignment = { horizontal: 'center', vertical: 'middle' }; c.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
            }

            ws.getRow(13).height = 35;
            const data = [1, desc, parseFloat(qty), parseFloat(price), parseFloat(subtotal)];
            for(let i=0; i<data.length; i++) {
                const c = ws.getCell(hCols[i] + '13');
                c.value = data[i]; c.font = { name: 'Cairo', size: 11, color: { argb: 'FF1A1A2E' } }; c.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true }; c.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
                if(i > 1) c.numFmt = '#,##0.00';
            }

            function addTotalRow(r, lbl, val, bold, color, fill) {
                ws.getRow(r).height = 35; ws.mergeCells(`B${r}:E${r}`);
                const lCell = ws.getCell(`B${r}`);
                lCell.value = lbl; lCell.font = { name: 'Cairo', size: 12, bold: true, color: { argb: color } }; lCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: fill } }; lCell.alignment = { horizontal: 'left', vertical: 'middle' }; lCell.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
                const vCell = ws.getCell(`F${r}`);
                vCell.value = parseFloat(val); vCell.font = { name: 'Cairo', size: bold ? 14 : 12, bold: bold, color: { argb: color } }; vCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: fill } }; vCell.alignment = { horizontal: 'center', vertical: 'middle' }; vCell.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }; vCell.numFmt = '#,##0.00';
            }

            addTotalRow(14, "المبلغ الإجمالي (قبل الضريبة)", subtotal, false, P, 'FFF9FAFB');
            addTotalRow(15, "ضريبة القيمة المضافة (15%)", tax, false, 'FFC0392B', 'FFFFF9F9');
            addTotalRow(16, "المجموع الكلي (مع الضريبة)", total, true, W, P);

            ws.getRow(19).height = 25;
            ws.getCell('B19').value = "توقيع السائق"; ws.getCell('F19').value = "اعتماد الإدارة";
            [ws.getCell('B19'), ws.getCell('F19')].forEach(c => { c.font = { name: 'Cairo', size: 11, bold: true, color: { argb: P } }; c.alignment = { horizontal: 'center', vertical: 'middle' }; });
            ws.getRow(20).height = 40;
            const bBottom = { bottom: { style: 'medium', color: { argb: P } } };
            ws.getCell('B20').border = bBottom; ws.getCell('F20').border = bBottom;"""
    
    if "setInfo('D8', 'التاريخ', 'E8', invoiceDate);" not in content:
        content = re.sub(old_setinfo_pattern, new_setinfo, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Dates added successfully!")

