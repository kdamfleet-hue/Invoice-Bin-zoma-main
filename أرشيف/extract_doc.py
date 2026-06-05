import re
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
doc_path = os.path.join(script_dir, 'نموذج طلب شراء رقم 2222.doc')

data = open(doc_path, 'rb').read()

# Try to decode windows-1256 printable characters
text_1256 = ""
for b in data:
    if 32 <= b <= 126 or 193 <= b <= 250: # basic ascii and arabic in 1256
        try:
            text_1256 += bytes([b]).decode('windows-1256')
        except:
            text_1256 += " "
    else:
        text_1256 += " "

words_1256 = [w for w in text_1256.split() if len(w) > 2 and any('\u0600' <= c <= '\u06FF' for c in w)]

# Try UTF-16LE
text_16 = data.decode('utf-16le', errors='ignore')
words_16 = [w for w in text_16.split() if len(w) > 2 and any('\u0600' <= c <= '\u06FF' for c in w)]

with open(os.path.join(script_dir, 'extracted_doc.txt'), 'w', encoding='utf-8') as f:
    f.write("--- 1256 Words ---\n")
    f.write(" ".join(words_1256))
    f.write("\n--- UTF16 Words ---\n")
    f.write(" ".join(words_16))

