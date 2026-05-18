import re

# Read new logo
with open(r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\new_logo_b64.txt', 'r', encoding='utf-8') as f:
    b64 = f.read().strip()

# Update b64.txt for Flask app
with open(r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\b64.txt', 'w', encoding='utf-8') as f:
    f.write(b64)

# Update templates/index.html
templates_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\index.html'
with open(templates_path, 'r', encoding='utf-8') as f:
    t_content = f.read()

# Replace the Excel logic
old_excel = """            const b64_ar = "{{ b64_ar }}";
            const b64_en = "{{ b64_en }}";
            const b64_cent = "{{ b64_cent }}";

            ws.getRow(2).height = 30; ws.getRow(3).height = 30; ws.getRow(4).height = 30;
            
            if(b64_ar) { const id = wb.addImage({ base64: 'data:image/png;base64,'+b64_ar, extension: 'png' }); ws.addImage(id, 'A2:C4'); }
            if(b64_cent) { const id = wb.addImage({ base64: 'data:image/png;base64,'+b64_cent, extension: 'png' }); ws.addImage(id, 'C2:E4'); }
            if(b64_en) { const id = wb.addImage({ base64: 'data:image/png;base64,'+b64_en, extension: 'png' }); ws.addImage(id, 'E2:G4'); }"""

new_excel = """            const new_logo = "{{ b64_en }}";

            ws.getRow(2).height = 30; ws.getRow(3).height = 30; ws.getRow(4).height = 30;
            
            if(new_logo) { 
                const id = wb.addImage({ base64: 'data:image/png;base64,'+new_logo, extension: 'png' }); 
                ws.addImage(id, 'A2:G4'); 
            }"""

if old_excel in t_content:
    t_content = t_content.replace(old_excel, new_excel)
else:
    print("Could not find old excel logic in templates!")

with open(templates_path, 'w', encoding='utf-8') as f:
    f.write(t_content)


# Update static index.html
static_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\index.html'
with open(static_path, 'r', encoding='utf-8') as f:
    s_content = f.read()

# Static Excel logic is huge because of hardcoded b64. Let's use regex to replace it
# It looks like:
# // 2. Add Logos
# const logoArId = wb.addImage({ base64: 'data:image/png;base64,iV...
# ...
# ws.addImage(logoEnId, 'E2:G4');
# 
# ws.mergeCells('B6:F6');

s_content = re.sub(r"// 2\. Add Logos.*?ws\.mergeCells\('B6:F6'\);", 
                   f"// 2. Add Logos\n            const logoId = wb.addImage({{ base64: 'data:image/png;base64,{b64}', extension: 'png' }});\n            ws.addImage(logoId, 'A2:G4');\n\n            ws.mergeCells('B6:F6');", 
                   s_content, flags=re.DOTALL)

with open(static_path, 'w', encoding='utf-8') as f:
    f.write(s_content)

print("Updated templates and static index.html!")
