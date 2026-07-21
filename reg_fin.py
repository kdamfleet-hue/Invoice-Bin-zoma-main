import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

if "finance_bp" not in content:
    content = content.replace("from routes.driver_portal import driver_portal_bp", "from routes.driver_portal import driver_portal_bp\nfrom routes.finance import finance_bp")
    content = content.replace("app.register_blueprint(driver_portal_bp)", "app.register_blueprint(driver_portal_bp)\napp.register_blueprint(finance_bp)")
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Registered finance_bp")
else:
    print("finance_bp already registered")
