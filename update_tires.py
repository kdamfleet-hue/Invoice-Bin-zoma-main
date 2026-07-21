import re

with open("models/schema.py", "r", encoding="utf-8") as f:
    content = f.read()

models = """
class TireRecord(db.Model):
    __tablename__ = 'erp_tires'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('erp_branches.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('erp_vehicles.id'), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    install_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="جديد") # جديد, مستخدم, تالف, تم التدفئة
    retread_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)

class BatteryRecord(db.Model):
    __tablename__ = 'erp_batteries'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('erp_branches.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('erp_vehicles.id'), nullable=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    capacity = db.Column(db.String(50), nullable=True)
    install_date = db.Column(db.Date, nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="نشط") # نشط, تالف, مستبدل
    notes = db.Column(db.Text, nullable=True)

"""

if "class TireRecord" not in content:
    content = content.replace("class AppSetting(db.Model):", models + "class AppSetting(db.Model):")
    with open("models/schema.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added TireRecord and BatteryRecord to schema.")
else:
    print("Models already exist.")
