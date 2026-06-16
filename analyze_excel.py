import openpyxl
import sys
sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook('static/تقرير الورشة.xlsx', data_only=True)
ws = wb.active

print("--- Merged Cells ---")
for merged in ws.merged_cells.ranges:
    print(merged)

print("\n--- Row Heights ---")
for r in range(1, 16):
    if ws.row_dimensions[r].height:
        print(f"Row {r}: {ws.row_dimensions[r].height}")

print("\n--- Column Widths ---")
for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
    if ws.column_dimensions[col].width:
        print(f"Col {col}: {ws.column_dimensions[col].width}")

print("\n--- Cells Content ---")
for row in ws.iter_rows(min_row=1, max_row=15, min_col=1, max_col=10):
    for cell in row:
        if cell.value:
            print(f"{cell.coordinate}: {cell.value} (Align: {cell.alignment.horizontal}, Font: {cell.font.name} {cell.font.size} {cell.font.bold})")
