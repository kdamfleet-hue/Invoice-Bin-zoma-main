import os, re

template_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\index.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Buttons
old_btn = """    <button class="btn-submit" onclick="generateExcel()">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
        إنشاء وتصدير الفاتورة
    </button>"""

new_btn = """    <div style="display: flex; gap: 1rem; justify-content: center; max-width: 800px; margin: 0 auto;">
        <button class="btn-submit" style="flex:1;" onclick="generateExcel()">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
            تصدير PDF / Excel
        </button>
        <button class="btn-submit" style="flex:1; background: #e67e22;" onclick="document.getElementById('emailModal').style.display='flex'">
            📧 إرسال الفاتورة للإيميل
        </button>
    </div>"""

if old_btn in content:
    content = content.replace(old_btn, new_btn)

# 2. Add Email Modal
email_modal = """
    <!-- Modal Email -->
    <div class="modal" id="emailModal">
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h2>إرسال عبر الإيميل</h2>
                <button class="close-btn" onclick="document.getElementById('emailModal').style.display='none'">✖</button>
            </div>
            <div class="add-form" style="grid-template-columns: 1fr;">
                <input type="email" id="targetEmail" placeholder="البريد الإلكتروني للمستلم" required>
                <button class="btn-add" onclick="sendExcelEmail()" id="btnSendEmail">إرسال الفاتورة 🚀</button>
            </div>
        </div>
    </div>
"""

if 'id="emailModal"' not in content:
    content = content.replace('<!-- Modal Drivers Database -->', email_modal + '\n    <!-- Modal Drivers Database -->')

# 3. Refactor generateExcel
if "async function createInvoiceBuffer()" not in content:
    content = content.replace('async function generateExcel() {', 'async function createInvoiceBuffer() {')
    content = content.replace('const buffer = await wb.xlsx.writeBuffer();\n            const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });\n            saveAs(blob, `فاتورة_${driver}_${plate}.xlsx`);\n        }', """const buffer = await wb.xlsx.writeBuffer();
            return { buffer, filename: `فاتورة_${driver}_${plate}.xlsx` };
        }

        async function generateExcel() {
            const { buffer, filename } = await createInvoiceBuffer();
            const blob = new Blob([buffer], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
            saveAs(blob, filename);
        }

        async function sendExcelEmail() {
            const email = document.getElementById('targetEmail').value;
            if(!email) return alert('يرجى إدخال الإيميل');
            const btn = document.getElementById('btnSendEmail');
            btn.innerText = 'جاري الإرسال... ⏳';
            try {
                const { buffer, filename } = await createInvoiceBuffer();
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
                    alert('تم إرسال الفاتورة بنجاح عبر الإيميل!');
                    document.getElementById('emailModal').style.display='none';
                } else {
                    alert('حدث خطأ أثناء الإرسال: ' + data.error);
                }
            } catch(err) {
                alert('خطأ في الاتصال: ' + err);
            }
            btn.innerText = 'إرسال الفاتورة 🚀';
        }""")

# 4. Add User header (logout)
logout_html = """
    {% if user %}
    <div style="position: absolute; top: 1rem; left: 1rem; display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.9); padding: 5px 15px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <img src="{{ user.picture }}" alt="User" style="width: 30px; height: 30px; border-radius: 50%;">
        <span style="font-weight: bold; color: #1A3A5C; font-size: 0.9rem;">{{ user.name }}</span>
        <a href="/logout" style="color: #e74c3c; text-decoration: none; font-size: 0.9rem; font-weight: bold; margin-right: 10px;">خروج</a>
    </div>
    {% endif %}
"""
if "user.picture" not in content:
    content = content.replace('<h1 class="header-title">نظام الفواتير الذكي</h1>', logout_html + '\n    <h1 class="header-title">نظام الفواتير الذكي</h1>')


with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("HTML template patched successfully for Email and OAuth User profile.")
# تعريف رابط الصورة لتوقيع البريد (اختياري)
signature_image_url = "https://yourdomain.com/assets/signature.png"  # استبدل بالرابط الفعلي لديك أو اتركه فارغاً إذا كنت تفضل نص توقيع فقط

# بناء توقيع البريد
signature_html = """
  <hr style="border:0; border-top:1px solid #eee; margin: 20px 0;">
  <div style="font-family:Arial, sans-serif; font-size:12px; color:#555; line-height:1.6;">
"""

if signature_image_url:
    signature_html += f"""
    <div style="display:flex; align-items:center; gap:12px;">
      <img src="{signature_image_url}" alt="توقيع" style="height:40px; width:auto;">
      <div>
        <strong>اسمك بالكامل</strong><br>
        المسمى الوظيفي | الشركة<br>
        الهاتف: 0123456789 • البريد: your.email@example.com
      </div>
    </div>
    """
else:
    signature_html += """
    <div>
      <strong>اسمك بالكامل</strong><br>
      المسمى الوظيفي | الشركة<br>
      الهاتف: 0123456789 • البريد: your.email@example.com
    </div>
    """

signature_html += """
  </div>
"""

# أمثلة دمج التوقيع مع محتوى الإيميل:
email_html_start = """
<!DOCTYPE html>
<html lang="ar">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>فاتورة - BIN ZOMAH</title>
  <style>
    body { font-family: Arial, sans-serif; direction: rtl; }
    .email-container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .logo { text-align: center; margin: 20px 0; }
    .content { font-size: 14px; line-height: 1.6; color: #333; }
  </style>
</head>
<body>
  <div class="email-container">
"""

logo_block = """
  <div class="logo">
    <!-- يمكنك حذف هذا الجزء إذا لم ترغب بالشعار العلوي -->
  </div>
"""

email_html_end = """
  </div>
</body>
</html>
"""

# محتوى الفاتورة
content_block = """
  <div class="content">
    <p>عزيزي العميل،</p>
    <p>يرجى العثور على فاتورتك المرفقة. شكراً لتعاونك.</p>
  </div>
"""

# دمج: الرأس + اللوجو (إن وجد) + المحتوى + التوقيع
full_email_html = email_html_start + logo_block + content_block + signature_html + email_html_end

# استخدم full_email_html كجزء من جسم البريد في سكريبتك
