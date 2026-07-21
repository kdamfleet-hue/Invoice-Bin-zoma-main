import re

with open("models/schema.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Enhance Vehicle with Yard Management fields
old_veh = "gps_device_id = db.Column(db.String(100), nullable=True)"
new_veh = "gps_device_id = db.Column(db.String(100), nullable=True)\n    yard_status = db.Column(db.String(50), default='خارج الساحة')\n    yard_condition = db.Column(db.String(50), nullable=True)"
if old_veh in content and "yard_status =" not in content:
    content = content.replace(old_veh, new_veh)

# 2. Add CustodyItem model
new_model = """class CustodyItem(db.Model):
    __tablename__ = 'erp_custody_items'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('erp_branches.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('erp_drivers.id'), nullable=False)
    item_type = db.Column(db.String(100), nullable=False)
    item_details = db.Column(db.String(255), nullable=True)
    received_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="في العهدة")
    notes = db.Column(db.Text, nullable=True)

"""
if "class CustodyItem" not in content:
    # append before AppSetting or somewhere
    content = content.replace("class AppSetting(db.Model):", new_model + "class AppSetting(db.Model):")

with open("models/schema.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Schema updated with Yard and Custody fields.")
