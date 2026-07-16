import os
import json
import sqlite3
from flask import Flask
from models.schema import db, Branch, User, Driver, Vehicle, VehicleCustody, Incident, SparePart, WorkshopRecord, WorkshopPartUsage, Document, AuditLog
from datetime import datetime

# Initialize a dummy Flask app to provide application context for Flask-SQLAlchemy
app = Flask(__name__)
DB_PATH = os.environ.get('SQLITE_PATH', os.path.join(os.path.dirname(__file__), 'database.sqlite'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def parse_date(date_str):
    if not date_str or str(date_str).strip() == '':
        return None
    try:
        # Assuming YYYY-MM-DD
        return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
    except Exception:
        return None

def run_migration():
    with app.app_context():
        print("1. Creating new ERP tables (with erp_ prefix)...")
        db.create_all()
        print("ERP tables created successfully.")

        print("2. Connecting to legacy JSON blob tables...")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Migrate Branches
        # Assuming branch ID 1 is الدمام and ID 2 is Workstation
        try:
            if not Branch.query.filter_by(id=1).first():
                dammam = Branch(id=1, name="الدمام", code="DMM")
                db.session.add(dammam)
            if not Branch.query.filter_by(id=2).first():
                ws = Branch(id=2, name="Workstation Sandbox", code="WS")
                db.session.add(ws)
            db.session.commit()
            print("Branches seeded.")
        except Exception as e:
            print(f"Error seeding branches: {e}")
            db.session.rollback()

        # Migrate Users
        try:
            c.execute("SELECT id, data FROM app_users")
            users_blob = c.fetchone()
            if users_blob and users_blob[1]:
                users_list = json.loads(users_blob[1])
                for u in users_list:
                    if not User.query.filter_by(username=u.get("username")).first():
                        new_user = User(
                            branch_id=1, # Default to Dammam for HQ users
                            username=u.get("username"),
                            password_hash=u.get("pw_hash") or "123456",
                            role="admin" if u.get("is_admin") else "branch"
                        )
                        db.session.add(new_user)
                db.session.commit()
                print("Users migrated.")
        except Exception as e:
            print(f"Error migrating users: {e}")
            db.session.rollback()

        # Migrate Schedule Data into Drivers and Vehicles
        # Because driver_registry and vehicle_registry are empty, we will extract from schedule_data
        try:
            c.execute("SELECT id, data FROM schedule_data WHERE id=1")
            sched_blob = c.fetchone()
            if sched_blob and sched_blob[1]:
                sched_data = json.loads(sched_blob[1])
                main_list = sched_data.get("main", [])
                
                for row in main_list:
                    empid = row.get("empid")
                    if empid:
                        # Ensure Driver exists
                        driver = Driver.query.filter_by(employee_id=str(empid)).first()
                        if not driver:
                            driver = Driver(
                                branch_id=1,
                                employee_id=str(empid),
                                name=row.get("name", "Unknown"),
                                iqama_number=str(row.get("iqama", "")),
                                job_title=row.get("job", ""),
                                status="متاح"
                            )
                            db.session.add(driver)
                            db.session.commit()

                        # Ensure Vehicle exists
                        plate = row.get("plate")
                        if plate:
                            vehicle = Vehicle.query.filter_by(plate_number=str(plate)).first()
                            if not vehicle:
                                vehicle = Vehicle(
                                    branch_id=1,
                                    plate_number=str(plate),
                                    model=str(row.get("model", "")),
                                    v_type=str(row.get("vtype", ""))
                                )
                                db.session.add(vehicle)
                                db.session.commit()
                                
                            # Create a VehicleCustody record
                            if not VehicleCustody.query.filter_by(driver_id=driver.id, vehicle_id=vehicle.id).first():
                                custody = VehicleCustody(
                                    driver_id=driver.id,
                                    vehicle_id=vehicle.id,
                                    received_date=datetime.utcnow().date(),
                                    status="active"
                                )
                                db.session.add(custody)
                                db.session.commit()
                
                print("Drivers, Vehicles, and Custodies extracted from schedule_data.")
        except Exception as e:
            print(f"Error migrating schedule_data: {e}")
            db.session.rollback()

        conn.close()
        print("Migration completed successfully! The ERP tables are now populated.")

if __name__ == '__main__':
    run_migration()
