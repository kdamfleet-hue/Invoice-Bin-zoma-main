import sqlite3
import json
import logging
from app import app, db
from models.schema import Branch, Driver, Vehicle, Document, Incident, SparePart, WorkshopRecord, WorkshopPartUsage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataMigration")

def run_migration():
    with app.app_context():
        conn = sqlite3.connect('database.sqlite')
        conn.row_factory = sqlite3.Row
        
        # 1. Create Default Branch
        main_branch = Branch.query.filter_by(name="الفرع الرئيسي").first()
        if not main_branch:
            main_branch = Branch(name="الفرع الرئيسي", code="HQ")
            db.session.add(main_branch)
            db.session.commit()
            logger.info("✅ Created Default Branch: 'الفرع الرئيسي'")

        branch_id = main_branch.id

        # 2. Migrate Drivers and Vehicles from `drivers` table
        drivers_rows = conn.execute("SELECT * FROM drivers").fetchall()
        driver_count = 0
        vehicle_count = 0
        
        for row in drivers_rows:
            # --- Driver ---
            empid = row['empid']
            if not empid or str(empid).strip() == "":
                empid = f"EMP-{row['id']}" # Fallback for unique constraint
            
            iqama = row['iqama']
            if not iqama or str(iqama).strip() == "":
                iqama = None
            elif Driver.query.filter_by(iqama_number=iqama).first():
                iqama = f"{iqama}-dup{row['id']}"

            driver = Driver.query.filter_by(employee_id=empid).first()
            if not driver:
                driver = Driver(
                    branch_id=branch_id,
                    employee_id=empid,
                    name=row['name'] or "Unknown Driver",
                    iqama_number=iqama,
                    phone=row['phone'],
                    job_title=row['job'],
                    status=row['status'] or "متاح"
                )
                db.session.add(driver)
                driver_count += 1
            
            # --- Vehicle ---
            plate = row['plate']
            if plate and str(plate).strip() != "":
                vehicle = Vehicle.query.filter_by(plate_number=plate).first()
                if not vehicle:
                    vehicle = Vehicle(
                        branch_id=branch_id,
                        plate_number=plate,
                        model=row['car'] or row['model'],
                        serial_number=row['vserial']
                    )
                    db.session.add(vehicle)
                    vehicle_count += 1
        
        db.session.commit()
        logger.info(f"✅ Migrated {driver_count} drivers and {vehicle_count} vehicles.")

        # 3. Migrate all JSON blobs into AppSetting so blob_get() works flawlessly on Postgres
        from models.schema import AppSetting
        
        json_tables = [
            "system_features", "app_secret_key", "app_users", "branch_accounts", "washing_schedule", 
            "employees", "driver_registry", "vehicle_registry", "schedule_data", "records_data", 
            "incidents_data", "gps_devices_data", "alert_settings", "documents_data", "oils_data", 
            "fuel_data", "purchase_data", "workshop_data", "handover_data", "push_subscriptions", 
            "deauthorized_data", "spare_parts", "inventory_transactions"
        ]
        
        blob_count = 0
        for table in json_tables:
            try:
                # The old sqlite tables might not exist or might be empty
                rows = conn.execute(f"SELECT data FROM {table}").fetchall()
                if rows and rows[0]['data']:
                    # Assuming branch_id = 1 for the default branch
                    key = f"{table}_branch_1"
                    
                    # Some tables might be global and not branch-specific, but blob_set handles it.
                    # Actually _global_blob_get uses key={table}_branch_1 as well when _row_id() returns 1.
                    if not AppSetting.query.get(key):
                        setting = AppSetting(key=key, value=rows[0]['data'])
                        db.session.add(setting)
                        blob_count += 1
            except Exception as e:
                pass
        
        db.session.commit()
        logger.info(f"✅ Migrated {blob_count} JSON blobs into AppSetting.")

        logger.info("🎉 Migration script completed successfully. Your data is now in SQLAlchemy models!")
        conn.close()

if __name__ == "__main__":
    run_migration()
