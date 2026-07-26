from app import app
from models.schema import db, User

# Ensure we have a valid test user
with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password_hash='mock', role='admin')
        db.session.add(admin)
        db.session.commit()

client = app.test_client()

# Login
with client.session_transaction() as sess:
    sess['authenticated'] = True
    sess['role'] = 'admin'
    sess['username'] = 'admin'
    sess['is_admin'] = True

errors = []
success = 0

for rule in app.url_map.iter_rules():
    if 'GET' in rule.methods:
        # Skip rules with arguments for now to keep it simple
        if '<' not in rule.rule:
            try:
                response = client.get(rule.rule)
                if response.status_code >= 500:
                    errors.append(f"500 ERROR at {rule.rule} (Endpoint: {rule.endpoint})")
                else:
                    success += 1
            except Exception as e:
                errors.append(f"EXCEPTION at {rule.rule} (Endpoint: {rule.endpoint}): {e}")

print(f"Tested {success + len(errors)} routes.")
if errors:
    print("Found Errors:")
    for err in errors:
        print(err)
else:
    print("All tested GET routes returned successfully (no 500 errors).")
