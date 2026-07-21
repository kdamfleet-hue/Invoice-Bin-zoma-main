import re

with open("templates/documents.html", "r", encoding="utf-8") as f:
    content = f.read()

if "تصريح دخول ميناء" not in content:
    content = content.replace('<option value="تأمين">تأمين</option>', '<option value="تأمين">تأمين</option>\n            <option value="تصريح دخول ميناء">تصريح دخول ميناء</option>')
    with open("templates/documents.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added port pass to documents.")
else:
    print("Already added.")
