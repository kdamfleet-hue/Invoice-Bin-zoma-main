import base64, os
folder = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp'

def b64(name):
    path = os.path.join(folder, name)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ""

out = f"ar='{b64('source_img_1.png')}'\nen='{b64('source_img_0.png')}'\ncent='{b64('output-onlinepngtools.png')}'"
with open(os.path.join(folder, 'b64.txt'), 'w') as f:
    f.write(out)

