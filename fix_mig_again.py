import re
import os
import glob

files = glob.glob("migrations/versions/b089*.py")
if files:
    with open(files[0], "r", encoding="utf-8") as f:
        content = f.read()

    # Remove the create_table block
    content = re.sub(r"op\.create_table\('erp_custody_items'.*?\)", "", content, flags=re.DOTALL)
    content = re.sub(r"op\.drop_table\('erp_custody_items'\)", "", content)

    with open(files[0], "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Cleaned up migration file.")
