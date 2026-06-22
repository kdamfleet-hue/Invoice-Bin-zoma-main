import os
import re

file_path = 'templates/purchase.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject the excel-table styles into the head
excel_style = """
    <style>
        .excel-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 25px;
            font-family: 'Cairo', sans-serif;
            border: 2px solid #000;
            background: #fff;
        }
        .excel-table th, .excel-table td {
            border: 1px solid #000;
            padding: 0;
            margin: 0;
        }
        .excel-header {
            background-color: #BDD7EE !important;
            color: #000 !important;
            text-align: center;
            font-weight: bold;
            padding: 8px !important;
            font-size: 1.1rem;
            border: 1px solid #000;
        }
        .excel-label {
            background-color: #BDD7EE !important;
            color: #000 !important;
            text-align: center;
            font-weight: bold;
            padding: 6px !important;
            font-size: 0.95rem;
            width: 12%;
            white-space: nowrap;
        }
        .excel-table th {
            background-color: #BDD7EE;
            color: #000;
            text-align: center;
            font-weight: bold;
            padding: 6px !important;
            font-size: 0.95rem;
        }
        .excel-input {
            width: 21%;
        }
        .excel-input input, .excel-table td input {
            width: 100%;
            height: 100%;
            box-sizing: border-box;
            border: none !important;
            padding: 8px;
            background: transparent;
            font-family: 'Cairo', sans-serif;
            font-weight: bold;
            color: #000;
            text-align: center;
            outline: none;
            min-height: 35px;
        }
        .excel-input input:focus, .excel-table td input:focus {
            background: #f0f8ff;
        }
        .btn-add-row {
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 10px;
            cursor: pointer;
            font-family: 'Cairo', sans-serif;
            font-weight: bold;
            font-size: 0.9rem;
            margin-right: 15px;
        }
        .btn-add-row:hover {
            background: #219653;
        }
    </style>
</head>"""

html = html.replace('</head>', excel_style)

# 2. Extract everything from <div class="info-grid"> down to </table> for Summary
# and replace it with the new Excel format HTML!

# We'll use a regex to replace from <div class="info-grid"> to the end of the summary table.
start_str = r'<div class="info-grid">'
end_str = r'<div class="section-title">.*?ملاحظات هامة</div>'

new_html_block = """
        <table class="excel-table">
            <thead>
                <tr><th colspan="6" class="excel-header">بيانات السيارة والسائق</th></tr>
            </thead>
            <tbody>
                <tr>
                    <th class="excel-label">اسم السائق:</th><td class="excel-input"><input type="text" id="poDriver" list="driversList" onchange="poAutofill()"></td>
                    <th class="excel-label">الوظيفة:</th><td class="excel-input"><input type="text" id="poJob" value="سائق"></td>
                    <th class="excel-label">الفرع:</th><td class="excel-input"><input type="text" id="poBranch" value="الدمام"></td>
                </tr>
                <tr>
                    <th class="excel-label">نوع السيارة:</th><td class="excel-input"><input type="text" id="poCar"></td>
                    <th class="excel-label">الموديل:</th><td class="excel-input"><input type="text" id="poModel"></td>
                    <th class="excel-label">رقم اللوحة:</th><td class="excel-input"><input type="text" id="poPlate"></td>
                </tr>
                <tr>
                    <th class="excel-label">عداد السيارة:</th><td class="excel-input" colspan="5"><input type="number" id="odometer" required placeholder="مثال: 150000"></td>
                </tr>
                <tr>
                    <th class="excel-label">رقم الإقامة:</th><td class="excel-input"><input type="text" id="poIqama"></td>
                    <th class="excel-label">رقم الجوال:</th><td class="excel-input"><input type="text" id="poPhone"></td>
                    <th class="excel-label">التاريخ:</th><td class="excel-input"><input type="date" id="poDate"></td>
                </tr>
                <tr>
                    <th class="excel-label">الرقم التسلسلي:</th><td class="excel-input" colspan="5"><input type="text" id="poSerial" readonly style="background: rgba(0,0,0,0.05); color: #d35400;"></td>
                </tr>
            </tbody>
        </table>

        <!-- Parts -->
        <table id="partsTable" class="excel-table">
            <thead>
                <tr><th colspan="7" class="excel-header">قطع الغيار <button class="btn-add-row" onclick="addPartRow()">+ إضافة</button></th></tr>
                <tr>
                    <th style="width: 5%;">م</th>
                    <th style="width: 35%;">البيان</th>
                    <th style="width: 10%;">الكمية</th>
                    <th style="width: 15%;">السعر</th>
                    <th style="width: 15%;">القيمة</th>
                    <th style="width: 15%;">ملاحظات</th>
                    <th style="width: 5%;">حذف</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <!-- Repairs -->
        <table id="repairsTable" class="excel-table">
            <thead>
                <tr><th colspan="5" class="excel-header">الإصلاح <button class="btn-add-row" onclick="addRepairRow()">+ إضافة</button></th></tr>
                <tr>
                    <th style="width: 5%;">م</th>
                    <th style="width: 45%;">الوصف</th>
                    <th style="width: 20%;">القيمة</th>
                    <th style="width: 25%;">ملاحظات</th>
                    <th style="width: 5%;">حذف</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <!-- Tires -->
        <table id="tiresTable" class="excel-table">
            <thead>
                <tr><th colspan="9" class="excel-header">الكفرات <button class="btn-add-row" onclick="addTireRow()">+ إضافة</button></th></tr>
                <tr>
                    <th style="width: 5%;">م</th>
                    <th style="width: 15%;">تاريخ التغيير</th>
                    <th style="width: 10%;">العدد</th>
                    <th style="width: 10%;">أمامية</th>
                    <th style="width: 10%;">خلفية</th>
                    <th style="width: 15%;">قراءة سابقة</th>
                    <th style="width: 15%;">قراءة حالية</th>
                    <th style="width: 15%;">المسافة</th>
                    <th style="width: 5%;">حذف</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <!-- Batteries -->
        <table id="batteriesTable" class="excel-table">
            <thead>
                <tr><th colspan="8" class="excel-header">البطاريات <button class="btn-add-row" onclick="addBatteryRow()">+ إضافة</button></th></tr>
                <tr>
                    <th style="width: 5%;">م</th>
                    <th style="width: 30%;">الوصف</th>
                    <th style="width: 10%;">العدد</th>
                    <th style="width: 15%;">المقاس</th>
                    <th style="width: 10%;">أمبير</th>
                    <th style="width: 15%;">السعر للوحدة</th>
                    <th style="width: 10%;">التاريخ</th>
                    <th style="width: 5%;">حذف</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>

        <!-- Summary Totals -->
        <table id="summaryTable" class="excel-table">
            <thead>
                <tr><th colspan="7" class="excel-header">ملخص الإجماليات</th></tr>
                <tr>
                    <th style="width: 14%;">قطع الغيار</th>
                    <th style="width: 14%;">الإصلاح</th>
                    <th style="width: 14%;">الكفرات</th>
                    <th style="width: 14%;">البطاريات</th>
                    <th style="width: 15%;">الإجمالي (قبل الضريبة)</th>
                    <th style="width: 14%;">ضريبة 15%</th>
                    <th style="width: 15%;">الإجمالي شامل الضريبة</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><input type="number" id="sumParts" style="font-weight:bold;text-align:center;" placeholder="الإجمالي"></td>
                    <td><input type="number" id="sumRepairs" style="font-weight:bold;text-align:center;" placeholder="الإجمالي"></td>
                    <td><input type="number" id="sumTires" style="font-weight:bold;text-align:center;" placeholder="الإجمالي"></td>
                    <td><input type="number" id="sumBatteries" style="font-weight:bold;text-align:center;" placeholder="الإجمالي"></td>
                    <td><input type="number" id="sumSubtotal" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;color:var(--accent);"></td>
                    <td><input type="number" id="sumVat" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;color:#e67e22;"></td>
                    <td><input type="number" id="sumGrandTotal" readonly style="background:rgba(0,0,0,0.05);font-weight:bold;text-align:center;color:#27ae60;font-size:1.1rem;"></td>
                </tr>
            </tbody>
        </table>

        <div class="section-title">ملاحظات هامة</div>
"""

# Replace the block
match = re.search(r'<div class="info-grid">.*?<div class="section-title">.*?U.U,O O-O,O O O1O U.Oc</div>', html, flags=re.DOTALL)
if match:
    # the regex matched mojibake. But the mojibake is unpredictable.
    pass

# We will just do a simpler search
start_idx = html.find('<div class="info-grid">')
# Find the start of General Notes
end_idx = html.find('<textarea id="poNotes"')

if start_idx != -1 and end_idx != -1:
    # Find the nearest section-title before textarea
    title_start = html.rfind('<div class="section-title">', 0, end_idx)
    html = html[:start_idx] + new_html_block + html[end_idx:]
else:
    print("Failed to find start/end indices")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated purchase.html successfully")
