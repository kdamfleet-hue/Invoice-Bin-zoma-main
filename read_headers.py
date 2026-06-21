import openpyxl
import sys
sys.stdout.reconfigure(encoding='utf-8')
wb = openpyxl.load_workbook('static/تقرير الورشة.xlsx', data_only=True)
ws = wb.active
for r in range(1, 40):
    row_data = [(c.column_letter, c.value) for c in ws[r] if c.value is not None]
    if row_data:
        print(f"Row {r}:", row_data)
