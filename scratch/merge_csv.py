import pandas as pd
import glob
import os

excel_file = "تحديث الاسبوعي - فرع الدمام (محدث).xlsx"
csv_files = glob.glob("*.csv")

# Create a backup just in case
import shutil
shutil.copy(excel_file, excel_file + ".bak")

with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    for csv_file in csv_files:
        sheet_name = csv_file.replace("-الجدول ١.csv", "").replace(".csv", "")
        print(f"Reading {csv_file} -> {sheet_name}")
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
            except:
                df = pd.read_csv(csv_file, encoding='cp1256')
        
        # Write to sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False)
print("Finished merging CSVs into Excel.")
