import re

with open("models/schema.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add reason to AuditLog
old_audit = "target_id = db.Column(db.String(50), nullable=True)"
new_audit = "target_id = db.Column(db.String(50), nullable=True)\n    reason = db.Column(db.Text, nullable=True) # التوثيق الإلزامي للمخالفة أو المبرر"
if old_audit in content and "reason =" not in content:
    content = content.replace(old_audit, new_audit)
    
with open("models/schema.py", "w", encoding="utf-8") as f:
    f.write(content)

with open("models/database.py", "r", encoding="utf-8") as f:
    db_content = f.read()
    
# In database.py, raw audit_log might not be used because SQLAlchemy manages it?
# Wait! In database.py: db.execute('CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
# That was the old JSON-based table!
# If SQLAlchemy is used for erp_audit_logs, we need an alembic migration or just db.create_all() will handle it?
# Let's check if the new Alembic migration environment is set up.

print("Schema updated.")
