from openpyxl import load_workbook
import sys

wb = load_workbook('static/تقرير الورشة.xlsx')
ws = wb.active

if ws._images:
    img = ws._images[0]
    with open('extracted_logo.png', 'wb') as f:
        f.write(img.image._data())
    print("Extracted logo to extracted_logo.png")
else:
    print("No images found in ws._images")
