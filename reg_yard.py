import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from routes.yard import yard_bp" not in content:
    content = content.replace("from routes.custody import custody_bp\n", "from routes.custody import custody_bp\nfrom routes.yard import yard_bp\n")
    content = content.replace("app.register_blueprint(custody_bp)\n", "app.register_blueprint(custody_bp)\napp.register_blueprint(yard_bp)\n")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Registered yard_bp in app.py")
