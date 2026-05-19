import os

folder = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp'

b64_ar = ""
b64_en = ""
b64_cent = ""

try:
    with open(os.path.join(folder, 'b64.txt'), 'r') as f:
        content = f.read()
        for line in content.split('\n'):
            if line.startswith("ar='"): b64_ar = line[4:-1]
            if line.startswith("en='"): b64_en = line[4:-1]
            if line.startswith("cent='"): b64_cent = line[6:-1]
except:
    pass

html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منشئ الفواتير الاحترافي</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <!-- استيراد بيانات السائقين -->
    <script src="drivers_data.js"></script>
    <style>
        :root {{
            --bg-color: #f3f4f6;
            --text-main: #1a1a2e;
            --card-radius: 16px;
            --trans: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Cairo', sans-serif;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
            background-image: radial-gradient(#d1d5db 1px, transparent 1px);
            background-size: 20px 20px;
        }}

        .header-title {{
            font-size: 2.5rem;
            font-weight: 800;
            color: #1A3A5C;
            margin-bottom: 0.5rem;
            text-align: center;
            text-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}
        
        .header-subtitle {{
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 2rem;
            text-align: center;
        }}

        .grid-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            width: 100%;
            max-width: 1000px;
        }}

        .card {{
            border-radius: var(--card-radius);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            color: white;
            transition: var(--trans);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
            pointer-events: none;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }}

        .card-purple {{ background-color: #423b87; }}
        .card-green {{ background-color: #115340; }}
        .card-blue {{ background-color: #144579; }}
        .card-brown {{ background-color: #6a2c17; }}
        .card-amber {{ background-color: #714406; }}
        .card-olive {{ background-color: #2e5910; }}
        .card-maroon {{ background-color: #6b223b; }}
        .card-gray {{ background-color: #444444; }}

        .card label {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
            display: block;
            opacity: 0.95;
        }}

        .card input, .card select, .card textarea {{
            width: 100%;
            padding: 0.8rem 1rem;
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 1.1rem;
            font-weight: 600;
            outline: none;
            transition: var(--trans);
            backdrop-filter: blur(5px);
        }}
        
        .card input::placeholder, .card textarea::placeholder {{
            color: rgba(255,255,255,0.5);
            font-weight: 400;
        }}

        .card input:focus, .card select:focus, .card textarea:focus {{
            background: rgba(255,255,255,0.2);
            border-color: rgba(255,255,255,0.5);
            box-shadow: 0 0 15px rgba(255,255,255,0.1);
        }}

        .card select option {{
            background-color: var(--text-main);
            color: white;
        }}
        
        .financial-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
        }}
        
        @media (max-width: 600px) {{
            .financial-grid {{ grid-template-columns: 1fr; }}
        }}

        .btn-submit {{
            margin-top: 3rem;
            background: linear-gradient(135deg, #C8A45A 0%, #a88540 100%);
            color: white;
            border: none;
            padding: 1.2rem 3rem;
            font-size: 1.5rem;
            font-weight: 800;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(200, 164, 90, 0.4);
            transition: var(--trans);
            display: inline-flex;
            align-items: center;
            gap: 1rem;
        }}

        .btn-submit:hover {{
            transform: scale(1.05) translateY(-3px);
            box-shadow: 0 15px 35px rgba(200, 164, 90, 0.6);
        }}

        .btn-submit:active {{
            transform: scale(0.98);
        }}

        .span-2 {{ grid-column: span 2; }}
        @media (max-width: 768px) {{
            .span-2 {{ grid-column: span 1; }}
        }}
    </style>
</head>
<body>

    <h1 class="header-title">نظام الفواتير الذكي</h1>
    <p class="header-subtitle">اختر السائق وسيتم تعبئة البيانات تلقائياً</p>

    <div class="grid-container">
        <!-- 1. اسم السائق (البحث الذكي) -->
        <div class="card card-purple span-2">
            <label for="driverName">اسم السائق (اكتب للبحث)</label>
            <input type="text" id="driverName" list="driversList" placeholder="ابحث عن اسم السائق هنا..." onchange="autofillDriver()">
            <datalist id="driversList"></datalist>
        </div>

        <!-- 2. نوع السيارة -->
        <div class="card card-green">
            <label for="carType">نوع السيارة</label>
            <input type="text" id="carType" placeholder="مثال: ايسوزو دينا 2024">
        </div>

        <!-- 3. رقم اللوحة -->
        <div class="card card-blue">
            <label for="plateNum">رقم اللوحة</label>
            <input type="text" id="plateNum" placeholder="مثال: ا ب ج 1234">
        </div>

        <!-- 4. نوع الطلب -->
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
        
        <!-- 5. الكمية والسعر -->
        <div class="card card-maroon span-2">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <label for="quantity">الكمية</label>
                    <input type="number" id="quantity" value="1" min="1" oninput="calcTotal()">
                </div>
                <div>
                    <label for="price">السعر الإفرادي (ريال)</label>
                    <input type="number" id="price" placeholder="0.00" oninput="calcTotal()">
                </div>
            </div>
        </div>

        <!-- 6. الوصف -->
        <div class="card card-amber span-2">
            <label for="desc">الوصف / التفاصيل</label>
            <textarea id="desc" rows="3" placeholder="أدخل تفاصيل الفاتورة أو القطع المستبدلة..."></textarea>
        </div>

        <!-- 7. الاجمالي والضريبة -->
        <div class="card card-gray span-2">
            <label>الحسابات المالية</label>
            <div class="financial-grid">
                <div>
                    <span style="font-size:0.9rem; opacity:0.8;">المبلغ</span>
                    <input type="text" id="subtotal" readonly value="0.00" style="background: rgba(0,0,0,0.3); border-color: transparent; margin-top:5px;">
                </div>
                <div>
                    <span style="font-size:0.9rem; opacity:0.8;">الضريبة (15%)</span>
                    <input type="text" id="tax" readonly value="0.00" style="background: rgba(0,0,0,0.3); border-color: transparent; margin-top:5px;">
                </div>
                <div>
                    <span style="font-size:0.9rem; font-weight:bold; color:#f1c40f;">الإجمالي النهائي</span>
                    <input type="text" id="total" readonly value="0.00" style="background: rgba(0,0,0,0.4); border-color: #f1c40f; color:#f1c40f; margin-top:5px;">
                </div>
            </div>
        </div>
    </div>

    <button class="btn-submit" onclick="generateExcel()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
        إنشاء وتصدير الفاتورة
    </button>

    <script>
        // Populate Datalist
        window.onload = function() {{
            const list = document.getElementById('driversList');
            if (typeof driversData !== 'undefined') {{
                driversData.forEach(d => {{
                    const option = document.createElement('option');
                    option.value = d.name;
                    list.appendChild(option);
                }});
            }}
        }};

        function autofillDriver() {{
            const name = document.getElementById('driverName').value;
            if (typeof driversData !== 'undefined') {{
                const driver = driversData.find(d => d.name === name);
                if (driver) {{
                    document.getElementById('carType').value = driver.car && driver.car !== 'None' ? driver.car : '';
                    document.getElementById('plateNum').value = driver.plate && driver.plate !== 'None' ? driver.plate : '';
                }}
            }}
        }}

        function calcTotal() {{
            const qty = parseFloat(document.getElementById('quantity').value) || 0;
            const price = parseFloat(document.getElementById('price').value) || 0;
            const subtotal = qty * price;
            const tax = subtotal * 0.15;
            const total = subtotal + tax;
            
            document.getElementById('subtotal').value = subtotal.toFixed(2);
            document.getElementById('tax').value = tax.toFixed(2);
            document.getElementById('total').value = total.toFixed(2);
        }}

        async function generateExcel() {{
            const driver = document.getElementById('driverName').value || 'غير محدد';
            const car = document.getElementById('carType').value || 'غير محدد';
            const plate = document.getElementById('plateNum').value || 'غير محدد';
            const req = document.getElementById('requestType').value;
            const qty = document.getElementById('quantity').value;
            const price = document.getElementById('price').value || '0';
            const subtotal = document.getElementById('subtotal').value;
            const tax = document.getElementById('tax').value;
            const total = document.getElementById('total').value;
            const desc = document.getElementById('desc').value || 'لا يوجد وصف';

            const wb = new ExcelJS.Workbook();
            const ws = wb.addWorksheet('الفاتورة', {{ views: [{{ rightToLeft: true }}] }});

            ws.getCell('A1').font = {{ name: 'Cairo', size: 12 }};

            const P = 'FF1A3A5C'; // Primary Navy
            const G = 'FFC8A45A'; // Gold
            const W = 'FFFFFFFF';
            const L = 'FFF0F2F5'; // Light gray
            const thinBorder = {{ style: 'thin', color: {{ argb: 'FFD0D5DD' }} }};

            ws.columns = [
                {{ width: 5 }},
                {{ width: 25 }},
                {{ width: 15 }},
                {{ width: 15 }},
                {{ width: 15 }},
                {{ width: 25 }},
                {{ width: 5 }}
            ];

            // 1. Gold Stripe
            for(let c=1; c<=7; c++) {{
                ws.getCell(1, c).fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: G }} }};
            }}
            ws.getRow(1).height = 5;

            // 2. Add Logos
            const logoArId = wb.addImage({{ base64: 'data:image/png;base64,{b64_ar}', extension: 'png' }});
            const logoEnId = wb.addImage({{ base64: 'data:image/png;base64,{b64_en}', extension: 'png' }});
            const logoCentId = wb.addImage({{ base64: 'data:image/png;base64,{b64_cent}', extension: 'png' }});
            
            ws.getRow(2).height = 30;
            ws.getRow(3).height = 30;
            ws.getRow(4).height = 30;
            
            if("{b64_ar}") ws.addImage(logoArId, 'A2:C4');
            if("{b64_cent}") ws.addImage(logoCentId, 'C2:E4');
            if("{b64_en}") ws.addImage(logoEnId, 'E2:G4');

            // 3. Title
            ws.mergeCells('B6:F6');
            const title = ws.getCell('B6');
            title.value = "فــاتــورة طـلـب صـيـانـة / خـدمـة";
            title.font = {{ name: 'Cairo', size: 16, bold: true, color: {{ argb: P }} }};
            title.alignment = {{ horizontal: 'center', vertical: 'middle' }};
            title.fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: L }} }};
            title.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};
            ws.getRow(6).height = 35;

            // 4. Info Section
            ws.getRow(8).height = 25;
            ws.getRow(9).height = 25;

            function setInfo(cell1, lbl, cell2, val) {{
                const c1 = ws.getCell(cell1);
                c1.value = lbl;
                c1.font = {{ name: 'Cairo', size: 12, bold: true, color: {{ argb: W }} }};
                c1.fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: P }} }};
                c1.alignment = {{ horizontal: 'center', vertical: 'middle' }};
                c1.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};

                const c2 = ws.getCell(cell2);
                c2.value = val;
                c2.font = {{ name: 'Cairo', size: 12, bold: true, color: {{ argb: 'FF333333' }} }};
                c2.fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: 'FFF9FAFB' }} }};
                c2.alignment = {{ horizontal: 'center', vertical: 'middle' }};
                c2.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};
            }}

            setInfo('B8', 'اسم السائق', 'C8', driver);
            setInfo('D8', 'رقم اللوحة', 'E8', plate);
            setInfo('B9', 'نوع السيارة', 'C9', car);
            setInfo('D9', 'نوع الطلب', 'E9', req);

            ws.mergeCells('B8:B8'); ws.mergeCells('C8:C8');
            ws.mergeCells('D8:D8'); ws.mergeCells('E8:F8');
            ws.mergeCells('B9:B9'); ws.mergeCells('C9:C9');
            ws.mergeCells('D9:D9'); ws.mergeCells('E9:F9');

            // 5. Table Headers
            ws.getRow(11).height = 30;
            const headers = ['م', 'الوصف / البيان', 'الكمية', 'السعر الإفرادي', 'المبلغ'];
            const hCols = ['B', 'C', 'D', 'E', 'F'];
            for(let i=0; i<headers.length; i++) {{
                const c = ws.getCell(hCols[i] + '11');
                c.value = headers[i];
                c.font = {{ name: 'Cairo', size: 11, bold: true, color: {{ argb: W }} }};
                c.fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: 'FF2C4A6E' }} }};
                c.alignment = {{ horizontal: 'center', vertical: 'middle' }};
                c.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};
            }}

            // 6. Data Row
            ws.getRow(12).height = 35;
            const dCols = ['B', 'C', 'D', 'E', 'F'];
            const data = [1, desc, parseFloat(qty), parseFloat(price), parseFloat(subtotal)];
            for(let i=0; i<data.length; i++) {{
                const c = ws.getCell(dCols[i] + '12');
                c.value = data[i];
                c.font = {{ name: 'Cairo', size: 11, color: {{ argb: 'FF1A1A2E' }} }};
                c.alignment = {{ horizontal: 'center', vertical: 'middle', wrapText: true }};
                c.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};
                if(i > 1) c.numFmt = '#,##0.00';
            }}

            // 7. Financial Rows
            function addTotalRow(r, lbl, val, bold, color, fill) {{
                ws.getRow(r).height = 35;
                ws.mergeCells(`B${{r}}:E${{r}}`);
                const lCell = ws.getCell(`B${{r}}`);
                lCell.value = lbl;
                lCell.font = {{ name: 'Cairo', size: 12, bold: true, color: {{ argb: color }} }};
                lCell.fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: fill }} }};
                lCell.alignment = {{ horizontal: 'left', vertical: 'middle' }};
                lCell.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};

                const vCell = ws.getCell(`F${{r}}`);
                vCell.value = parseFloat(val);
                vCell.font = {{ name: 'Cairo', size: bold ? 14 : 12, bold: bold, color: {{ argb: color }} }};
                vCell.fill = {{ type: 'pattern', pattern: 'solid', fgColor: {{ argb: fill }} }};
                vCell.alignment = {{ horizontal: 'center', vertical: 'middle' }};
                vCell.border = {{ top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder }};
                vCell.numFmt = '#,##0.00';
            }}

            addTotalRow(13, "المبلغ الإجمالي (قبل الضريبة)", subtotal, false, P, 'FFF9FAFB');
            addTotalRow(14, "ضريبة القيمة المضافة (15%)", tax, false, 'FFC0392B', 'FFFFF9F9');
            addTotalRow(15, "المجموع الكلي (مع الضريبة)", total, true, W, P); // Navy BG for final total

            // 8. Signatures
            ws.getRow(18).height = 25;
            ws.getCell('B18').value = "توقيع السائق";
            ws.getCell('F18').value = "اعتماد الإدارة";
            [ws.getCell('B18'), ws.getCell('F18')].forEach(c => {{
                c.font = {{ name: 'Cairo', size: 11, bold: true, color: {{ argb: P }} }};
                c.alignment = {{ horizontal: 'center', vertical: 'middle' }};
            }});

            ws.getRow(19).height = 40;
            const bBottom = {{ bottom: {{ style: 'medium', color: {{ argb: P }} }} }};
            ws.getCell('B19').border = bBottom;
            ws.getCell('F19').border = bBottom;

            // Generate
            const buffer = await wb.xlsx.writeBuffer();
            const blob = new Blob([buffer], {{ type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }});
            saveAs(blob, `فاتورة_${{plate}}_${{new Date().getTime()}}.xlsx`);
        }}
    </script>
</body>
</html>
"""

with open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated index.html successfully at: {os.path.join(folder, 'index.html')}")

