import os
import logging
from app import app, db
from models.schema import User, Branch
from werkzeug.security import generate_password_hash

logger = logging.getLogger("InvoiceApp")

def seed():
    with app.app_context():
        try:
            # Ensure default branch exists
            branch1 = Branch.query.get(1)
            if not branch1:
                branch1 = Branch(id=1, name="الفرع الرئيسي", code="HQ")
                db.session.add(branch1)
                db.session.commit()

            # Create initial admin ONLY if no admin user exists
            admin = User.query.filter_by(role="admin").first()
            if not admin:
                initial_password = os.environ.get("ADMIN_INITIAL_PASSWORD", "123456")
                admin = User(
                    username="admin",
                    password_hash=generate_password_hash(initial_password),
                    role="admin",
                    is_active=True
                )
                db.session.add(admin)
                logger.info("✅ Initial admin user created securely.")

            # Create initial dedicated user 'aaa' ONLY if it does not exist
            user_aaa = User.query.filter_by(username="aaa").first()
            if not user_aaa:
                initial_aaa_pwd = os.environ.get("AAA_INITIAL_PASSWORD", "123aaa")
                user_aaa = User(
                    username="aaa",
                    password_hash=generate_password_hash(initial_aaa_pwd),
                    role="viewer",
                    is_active=True,
                    is_dedicated=True,
                    allowed_route="/purchase"
                )
                db.session.add(user_aaa)
                logger.info("✅ Initial dedicated user 'aaa' created securely.")

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error seeding initial users: {e}")
