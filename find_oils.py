import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Let's just find the text "إجمالي الزيوت" in the excel file
df = pd.read_excel('static/oils_template.xlsx', header=None)

for i, row in df.iterrows():
    for j, cell in enumerate(row):
        if pd.notna(cell) and 'إجمالي الزيوت' in str(cell):
            print(f"Row {i}, Col {j}: {cell}")
