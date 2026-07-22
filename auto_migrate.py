import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

migration_code = """
with app.app_context():
    try:
        from flask_migrate import upgrade
        upgrade()
        print("Auto-migration successful on startup.")
    except Exception as e:
        print("Auto-migration skipped or failed:", e)

if __name__ == '__main__':
"""

content = content.replace("if __name__ == '__main__':", migration_code)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Added auto-migration to app.py")
