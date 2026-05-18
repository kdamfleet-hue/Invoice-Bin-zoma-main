import os
import re

html_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\oils.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Email Modal and Buttons
modal_html = """
    <!-- Email Modal -->
    <div id="emailModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:2000; align-items:center; justify-content:center;">
        <div class="modal-content" style="background:white; padding:2rem; border-radius:16px; width:90%; max-width:400px; text-align:center;">
            <h3 style="color:#1A3A5C; margin-bottom:1rem;">إرسال بيان الزيوت عبر الإيميل</h3>
            <p style="margin-bottom:1rem; color:#555;">أدخل البريد الإلكتروني الذي ترغب بإرسال البيان إليه:</p>
            <input type="email" id="targetEmail" placeholder="example@gmail.com" style="width:100%; padding:10px; margin-bottom:1rem; border:1px solid #ccc; border-radius:8px;">
            <div style="display:flex; gap:10px; justify-content:center;">
                <button id="btnSendEmail" class="btn-primary" onclick="sendExcelEmail()" style="padding:0.5rem 1rem;">إرسال البيان 🚀</button>
                <button class="btn-remove" onclick="document.getElementById('emailModal').style.display='none'" style="padding:0.5rem 1rem;">إلغاء</button>
            </div>
        </div>
    </div>
"""
if "emailModal" not in content:
    content = content.replace('</body>', modal_html + '\n</body>')

# Update export button to also show email button
old_buttons = '<button class="btn-primary" onclick="generateExcel()">📥 استخراج البيان (Excel)</button>'
new_buttons = """
<button class="btn-primary" onclick="generateExcel()">📥 استخراج البيان (Excel)</button>
<button class="btn-primary" style="background: #e67e22;" onclick="document.getElementById('emailModal').style.display='flex'">📧 إرسال عبر الإيميل</button>
"""
if "📧 إرسال عبر الإيميل" not in content:
    content = content.replace(old_buttons, new_buttons)

# 2. Update HTML Table
old_thead = """
            <thead>
                <tr>
                    <th style="width: 50px;">م</th>
                    <th>التاريخ</th>
                    <th>اسم السائق</th>
                    <th>نوع السيارة</th>
                    <th>رقم اللوحة</th>
                    <th>الكيلومتر</th>
                    <th>نوع الزيت</th>
                    <th>الكمية</th>
                    <th>نوع الفلتر</th>
                    <th>الملاحظات</th>
                    <th style="width: 60px;">حذف</th>
                </tr>
            </thead>
"""
new_thead = """
            <thead>
                <tr>
                    <th style="width: 50px;">م</th>
                    <th>رقم لوحة السيارة</th>
                    <th>المستخدم</th>
                    <th>تاريخ تغيير الزيت</th>
                    <th>رقم العداد</th>
                    <th>عدد اللترات</th>
                    <th>عدد فلاتر الزيت والديزل والهواء</th>
                    <th style="width: 60px;">حذف</th>
                </tr>
            </thead>
"""
content = content.replace(old_thead, new_thead)

# Update addRow javascript
old_row_js = """
                <td>${rowCount}</td>
                <td><input type="date" class="t-date" value="${new Date().toISOString().split('T')[0]}"></td>
                <td><input type="text" class="t-driver" list="driversList" placeholder="اسم السائق" onchange="autofillRow(this)"></td>
                <td><input type="text" class="t-car" placeholder="السيارة"></td>
                <td><input type="text" class="t-plate" placeholder="اللوحة"></td>
                <td><input type="number" class="t-km" placeholder="كم"></td>
                <td><input type="text" class="t-oil" placeholder="نوع الزيت"></td>
                <td><input type="number" class="t-qty" placeholder="الكمية"></td>
                <td><input type="text" class="t-filter" placeholder="الفلتر"></td>
                <td><input type="text" class="t-notes" placeholder="..."></td>
                <td><button class="btn-remove" onclick="this.parentElement.parentElement.remove(); updateIds();">X</button></td>
"""
new_row_js = """
                <td>${rowCount}</td>
                <td><input type="text" class="t-plate" placeholder="رقم اللوحة"></td>
                <td><input type="text" class="t-driver" list="driversList" placeholder="اسم السائق" onchange="autofillRow(this)"></td>
                <td><input type="date" class="t-date" value="${new Date().toISOString().split('T')[0]}"></td>
                <td><input type="number" class="t-km" placeholder="رقم العداد"></td>
                <td><input type="number" class="t-qty" placeholder="عدد اللترات"></td>
                <td><input type="text" class="t-filter" placeholder="عدد الفلاتر"></td>
                <td><button class="btn-remove" onclick="this.parentElement.parentElement.remove(); updateIds();">X</button></td>
"""
content = content.replace(old_row_js, new_row_js)

# 3. Update Excel Generation & Add Email sending JS
js_excel_target = "async function generateExcel() {"
js_excel_replacement = """
        async function createExcelBuffer() {
            const wb = new ExcelJS.Workbook();
            const ws = wb.addWorksheet('بيان الزيوت والفلاتر', { views: [{ rightToLeft: true }] });

            const P = 'FF4A86E8'; // Blue like the image
            const W = 'FFFFFFFF';
            const thinBorder = { style: 'thin', color: { argb: 'FF000000' } };

            ws.columns = [
                { width: 5 }, { width: 18 }, { width: 25 }, { width: 20 }, 
                { width: 15 }, { width: 15 }, { width: 35 }
            ];

            const new_logo = "{{ b64_en }}";
            ws.getRow(1).height = 10; ws.getRow(2).height = 40; ws.getRow(3).height = 40; ws.getRow(4).height = 20;
            if(new_logo) { 
                const id = wb.addImage({ base64: 'data:image/png;base64,'+new_logo, extension: 'png' }); 
                ws.addImage(id, { tl: { col: 1.5, row: 1 }, ext: { width: 350, height: 73 } }); 
            }

            ws.mergeCells('A6:G6');
            const title = ws.getCell('A6');
            
            // Calculate date range from table
            const dateInputs = document.querySelectorAll('.t-date');
            let dates = Array.from(dateInputs).map(i => i.value).filter(v => v);
            let minDate = '', maxDate = '';
            if(dates.length > 0) {
                dates.sort();
                minDate = dates[0].split('-').join('/');
                maxDate = dates[dates.length-1].split('-').join('/');
            }
            
            title.value = `بيان استهلاك الزيوت والفلاتر للسيارات الديزل (فرع الدمام) من تاريخ ${minDate} الى تاريخ ${maxDate}`;
            title.font = { name: 'Arial', size: 14, bold: true, color: { argb: 'FF2986CC' } };
            title.alignment = { horizontal: 'center', vertical: 'middle' };
            ws.getRow(6).height = 30;

            ws.getRow(8).height = 25;
            const headers = ['م', 'رقم لوحة السيارة', 'المستخدم', 'تاريخ تغيير الزيت', 'رقم العداد', 'عدد اللترات', 'عدد فلاتر الزيت والديزل والهواء'];
            const hCols = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
            for(let i=0; i<headers.length; i++) {
                const c = ws.getCell(hCols[i] + '8');
                c.value = headers[i]; c.font = { name: 'Arial', size: 12, bold: true, color: { argb: W } }; 
                c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4A86E8' } }; 
                c.alignment = { horizontal: 'center', vertical: 'middle' }; 
                c.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
            }

            let startRow = 9;
            let totalLiters = 0;
            const rows = document.querySelectorAll('#oilTable tbody tr');
            rows.forEach((tr, index) => {
                ws.getRow(startRow).height = 20;
                let liters = parseFloat(tr.querySelector('.t-qty').value) || 0;
                totalLiters += liters;
                
                const data = [
                    index + 1,
                    tr.querySelector('.t-plate').value,
                    tr.querySelector('.t-driver').value,
                    tr.querySelector('.t-date').value.split('-').join('/'),
                    tr.querySelector('.t-km').value,
                    liters,
                    tr.querySelector('.t-filter').value
                ];
                for(let i=0; i<data.length; i++) {
                    const c = ws.getCell(hCols[i] + startRow);
                    c.value = data[i]; c.font = { name: 'Arial', size: 11, bold: true, color: { argb: 'FF000000' } }; 
                    c.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true }; 
                    c.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
                }
                startRow++;
            });

            // Total Row
            ws.getRow(startRow).height = 25;
            ws.mergeCells(`A${startRow}:E${startRow}`);
            const tLbl = ws.getCell(`A${startRow}`);
            tLbl.value = "إجمالي اللترات المستخدمة";
            tLbl.font = { name: 'Arial', size: 14, bold: true, color: { argb: W } };
            tLbl.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4A86E8' } };
            tLbl.alignment = { horizontal: 'left', vertical: 'middle' };
            tLbl.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
            
            const tVal = ws.getCell(`F${startRow}`);
            tVal.value = totalLiters;
            tVal.font = { name: 'Arial', size: 14, bold: true, color: { argb: 'FFCC0000' } }; // Red for total
            tVal.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFFF00' } }; // Yellow background for emphasis
            tVal.alignment = { horizontal: 'center', vertical: 'middle' };
            tVal.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
            
            const tEmpty = ws.getCell(`G${startRow}`);
            tEmpty.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4A86E8' } };
            tEmpty.border = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

            ws.addRow([]);
            const footerRow = ws.addRow(['تم الإعداد بواسطة قسم الحركة (خالد الغامدي)']);
            ws.mergeCells(`A${footerRow.number}:G${footerRow.number}`);
            footerRow.getCell(1).alignment = { horizontal: 'center', vertical: 'middle' };
            footerRow.getCell(1).font = { name: 'Arial', size: 12, bold: true, color: { argb: 'FF5A6A7A' } };
            footerRow.getCell(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFEDF2F7' } };
            footerRow.height = 30;

            const buffer = await wb.xlsx.writeBuffer();
            return { buffer, filename: `بيان_زيوت_وفلاتر_الدمام.xlsx` };
        }

        async function sendExcelEmail() {
            const email = document.getElementById('targetEmail').value;
            if(!email) return alert('يرجى إدخال الإيميل');
            const btn = document.getElementById('btnSendEmail');
            btn.innerText = 'جاري الإرسال... ⏳';
            try {
                const { buffer, filename } = await createExcelBuffer();
                let binary = '';
                const bytes = new Uint8Array(buffer);
                const len = bytes.byteLength;
                for (let i = 0; i < len; i++) { binary += String.fromCharCode(bytes[i]); }
                const file_b64 = window.btoa(binary);

                const res = await fetch('/api/send_email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, filename, file_b64 })
                });
                const data = await res.json();
                if(data.success) {
                    alert('تم إرسال البيان بنجاح عبر الإيميل!');
                    document.getElementById('emailModal').style.display='none';
                } else {
                    alert('حدث خطأ أثناء الإرسال: ' + data.error);
                }
            } catch(err) {
                alert('خطأ في الاتصال: ' + err);
            }
            btn.innerText = 'إرسال البيان 🚀';
        }

        async function generateExcel() {
            const { buffer, filename } = await createExcelBuffer();
"""

# I need to replace the entire old generateExcel with the new split logic
content = re.sub(r'async function generateExcel\(\) \{.*?(?=// Dark Mode)', js_excel_replacement, content, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated oils.html layout and added email sending.")


