from app import app, db
from models.schema import User, Branch
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        # Ensure default branch exists
        branch1 = Branch.query.get(1)
        if not branch1:
            branch1 = Branch(id=1, name="الفرع الرئيسي", code="HQ")
            db.session.add(branch1)
            db.session.commit()
            print("Created default branch (ID=1)")
        
        # Create admin user if not exists, otherwise reset password
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=generate_password_hash("123456"),
                role="admin",
                is_active=True
            )
            db.session.add(admin)
            print("Created admin user (admin / 123456)")
        else:
            admin.password_hash = generate_password_hash("123456")
            admin.role = "admin"
            admin.is_active = True
            print("Reset existing admin user password to 123456 and set as active admin.")
            
        # Create branch manager if not exists
        branch1 = User.query.filter_by(username="branch1").first()
        if not branch1:
            branch1 = User(
                username="branch1",
                password_hash=generate_password_hash("123456"),
                role="branch_manager",
                branch_id=1,
                is_active=True
            )
            db.session.add(branch1)
            print("Created branch1 user (branch1 / 123456)")
        else:
            branch1.password_hash = generate_password_hash("123456")
            branch1.is_active = True
        # Create dedicated user aaa (Purchase Only)
        user_aaa = User.query.filter_by(username="aaa").first()
        if not user_aaa:
            user_aaa = User(
                username="aaa",
                password_hash=generate_password_hash("123aaa"),
                role="viewer",
                is_active=True
            )
            db.session.add(user_aaa)
            print("Created user aaa (aaa / 123aaa)")
        else:
            user_aaa.password_hash = generate_password_hash("123aaa")
            user_aaa.is_active = True
            print("Reset existing user aaa password to 123aaa.")

        db.session.commit()

        # Set dedicated workstation mode /purchase for user aaa
        from helpers import _global_blob_get, _global_blob_set
        all_perms = _global_blob_get("user_account_permissions") or {}
        all_perms["aaa"] = {
            "dedicated_mode": "/purchase",
            "allowed_tabs": ["/purchase"]
        }
        _global_blob_set("user_account_permissions", all_perms)
        print("Configured user aaa for Purchase Only (/purchase)")
        print("Database users successfully updated.")

if __name__ == "__main__":
    seed()
