# -*- coding: utf-8 -*-
import os
import sys
import json

# Set UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

import pdfplumber

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Find the PDF file
pdf_file = None
for f in os.listdir(script_dir):
    if f.endswith('.pdf'):
        pdf_file = os.path.join(script_dir, f)
        print(f"Found PDF: {f}")
        break

if not pdf_file:
    print("No PDF file found!")
    sys.exit(1)

pdf = pdfplumber.open(pdf_file)
print(f"Number of pages: {len(pdf.pages)}")

all_tables = []

for i, page in enumerate(pdf.pages):
    print(f"\n=== PAGE {i+1} ===")
    print(f"Page size: {page.width} x {page.height}")
    
    # Extract text
    text = page.extract_text()
    if text:
        print(f"Page text preview: {text[:500]}")
    
    # Extract tables
    tables = page.extract_tables()
    print(f"Number of tables: {len(tables)}")
    
    for j, table in enumerate(tables):
        print(f"\nTable {j+1}: {len(table)} rows x {len(table[0]) if table else 0} cols")
        for row_idx, row in enumerate(table):
            print(f"Row {row_idx}: {row}")
        all_tables.append(table)

# Save tables as JSON for later use
output_json = os.path.join(script_dir, 'table_data.json')
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(all_tables, f, ensure_ascii=False, indent=2)
print(f"\nTable data saved to: {output_json}")

pdf.close()


