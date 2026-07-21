import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

if "driver_portal_bp" not in content:
    content = content.replace("from routes.inventory import inventory_bp", "from routes.inventory import inventory_bp\nfrom routes.driver_portal import driver_portal_bp")
    content = content.replace("app.register_blueprint(inventory_bp)", "app.register_blueprint(inventory_bp)\napp.register_blueprint(driver_portal_bp)")
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Registered driver_portal_bp")
else:
    print("driver_portal_bp already registered")
