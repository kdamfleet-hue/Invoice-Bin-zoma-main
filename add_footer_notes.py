import re

file_path = 'templates/purchase.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

new_block = """        <!-- User Notes -->
        <table class="excel-table" style="margin-top: 15px;">
            <tr>
                <th class="excel-label" style="width:15%">ملاحظات:</th>
                <td style="padding:0;"><textarea id="poNotes" rows="2" placeholder="حقل الملاحظات..." style="width:100%; height:100%; padding:8px; border:none; resize:none; font-family:'Cairo'; font-weight:bold; outline:none; font-size:1rem;"></textarea></td>
            </tr>
        </table>

        <!-- Signatures Row -->
        <div style="border-top: 2px solid #b8860b; border-bottom: 2px solid #b8860b; padding: 40px 0 10px 0; display: flex; justify-content: space-between; font-weight: bold; margin-top: 30px; font-size: 0.95rem;">
            <div style="width:14%; text-align:center; color:#000;">السائق</div>
            <div style="width:14%; text-align:center; color:#000;">الميكانيكي</div>
            <div style="width:14%; text-align:center; color:#000;">قسم الحركة</div>
            <div style="width:14%; text-align:center; color:#000;">مسئول الشراء</div>
            <div style="width:14%; text-align:center; color:#000;">الحسابات</div>
            <div style="width:14%; text-align:center; color:#000;">مدير الفرع</div>
            <div style="width:16%; text-align:center; color:#000;">اعتماد الإدارة</div>
        </div>

        <!-- Notes Section -->
        <div style="text-align: center; font-weight: bold; margin-top: 40px; margin-bottom: 5px; color:#000;">
            تم إعداد هذا الجدول بواسطة قسم الحركة
        </div>
        
        <table class="excel-table" style="margin-top: 0; margin-bottom: 30px;">
            <thead>
                <tr><th class="excel-header" style="background-color: #BDD7EE !important; text-align: center; padding:4px !important;">ملاحظات هامة</th></tr>
            </thead>
            <tbody>
                <tr><td style="padding: 4px 10px !important; font-weight: bold; text-align: right; font-size: 0.95rem; border: 1px solid #000; color:#000;">1- يعبأ الطلب من قبل مسئول الورشة بعد توقيعه وتوقيع السائق والميكانيكي</td></tr>
                <tr><td style="padding: 4px 10px !important; font-weight: bold; text-align: right; font-size: 0.95rem; border: 1px solid #000; color:#000;">2- يوقع بعد ذلك من المحاسبة ويتم ارساله للإدارة عن طريق محاسب الفرع ليتم اعتماده من الإدارة</td></tr>
                <tr><td style="padding: 4px 10px !important; font-weight: bold; text-align: right; font-size: 0.95rem; border: 1px solid #000; color:#000;">3- عند وجود ملاحظة لأي من الأطراف يمكن تدوينها في حقل الملاحظات أعلاه</td></tr>
                <tr><td style="padding: 4px 10px !important; font-weight: bold; text-align: right; font-size: 0.95rem; border: 1px solid #000; color:#000;">4- ترفق صورة للإدارة المالية وصورة لقسم الحركة بالإدارة، ويتم حفظ صورة من الطلب لدى الورشة</td></tr>
            </tbody>
        </table>"""

html = re.sub(r'<div class="section-title">ملاحظات هامة</div>\s*<textarea id="poNotes" rows="3" [^>]*></textarea>', new_block, html, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated footer notes")
