import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

if "inventory_bp" not in content:
    content = content.replace("from routes.yard import yard_bp", "from routes.yard import yard_bp\nfrom routes.inventory import inventory_bp")
    content = content.replace("app.register_blueprint(yard_bp)", "app.register_blueprint(yard_bp)\n    app.register_blueprint(inventory_bp)")
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Registered inventory_bp")
else:
    print("inventory_bp already registered")
