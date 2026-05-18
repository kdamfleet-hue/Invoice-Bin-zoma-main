# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pdfplumber

script_dir = os.path.dirname(os.path.abspath(__file__))

pdf_file = None
for f in os.listdir(script_dir):
    if f.endswith('.pdf'):
        pdf_file = os.path.join(script_dir, f)
        print(f"Found PDF: {f}")
        break

pdf = pdfplumber.open(pdf_file)
print(f"PDF metadata: {pdf.metadata}")
print(f"Number of pages reported by pdfplumber: {len(pdf.pages)}")

# Try accessing pages differently
import pypdfium2 as pdfium

pdf2 = pdfium.PdfDocument(pdf_file)
print(f"Number of pages (pdfium): {len(pdf2)}")

for i in range(len(pdf2)):
    page = pdf2[i]
    width, height = page.get_size()
    print(f"Page {i+1}: {width}x{height}")
    
    # Render page to image
    bitmap = page.render(scale=2)
    pil_image = bitmap.to_pil()
    img_path = os.path.join(script_dir, f'page_{i+1}.png')
    pil_image.save(img_path)
    print(f"Saved page image: {img_path}")

    # Try to extract text
    textpage = page.get_textpage()
    text = textpage.get_text_range()
    if text.strip():
        print(f"Text on page {i+1}: {text[:1000]}")
    else:
        print(f"No text found on page {i+1}")

pdf2.close()
pdf.close()


