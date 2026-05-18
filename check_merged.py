# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl

folder = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy'
orig_file = os.path.join(folder, "تحديث المركبات والسائقين-الدمام2026.xlsx")

wb = openpyxl.load_workbook(orig_file)
ws = wb.active

print("Merged cells:")
for r in ws.merged_cells.ranges:
    print(str(r))

print("\nCol widths:")
for c in range(1, 12):
    letter = openpyxl.utils.get_column_letter(c)
    print(f"Col {letter}: {ws.column_dimensions[letter].width}")


