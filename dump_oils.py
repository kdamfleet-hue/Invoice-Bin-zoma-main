import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('static/oils_template.xlsx', header=None)

# The first table usually has many rows, let's print from row 40 to the end
for i, row in df.iloc[35:].iterrows():
    row_text = []
    for cell in row:
        if pd.notna(cell):
            row_text.append(str(cell))
    if row_text:
        print(f"Row {i}: {' | '.join(row_text)}")
