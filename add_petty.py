import re

with open("models/schema.py", "r", encoding="utf-8") as f:
    content = f.read()

models = """
class PettyCash(db.Model):
    __tablename__ = 'erp_petty_cash'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('erp_branches.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('erp_drivers.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    expense_type = db.Column(db.String(100), nullable=False) # رسوم طرق، صيانة، طوارئ، رسوم ميناء
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default="معلق") # معلق، معتمد، مرفوض
    receipt_image = db.Column(db.String(255), nullable=True) # مسار الصورة
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

"""

if "class PettyCash" not in content:
    content = content.replace("class AppSetting(db.Model):", models + "class AppSetting(db.Model):")
    with open("models/schema.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added PettyCash model.")
else:
    print("Model already exists.")
