import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from routes.custody import custody_bp" not in content:
    content = content.replace("from routes.documents import documents_bp\n", "from routes.documents import documents_bp\nfrom routes.custody import custody_bp\n")
    content = content.replace("app.register_blueprint(documents_bp)\n", "app.register_blueprint(documents_bp)\napp.register_blueprint(custody_bp)\n")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Registered custody_bp in app.py")
