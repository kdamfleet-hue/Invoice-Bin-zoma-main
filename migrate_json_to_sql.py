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

        # 3. Migrate Documents (JSON table: documents_data)
        try:
            doc_rows = conn.execute("SELECT data FROM documents_data").fetchall()
            doc_count = 0
            for r in doc_rows:
                # The JSON blob
                data = json.loads(r['data'])
                # Some JSON tables store an array of objects
                if isinstance(data, dict) and "docs" in data:
                    data_list = data["docs"]
                elif isinstance(data, list):
                    data_list = data
                else:
                    data_list = [data]
                
                for item in data_list:
                    # Depends on JSON structure, let's just attempt generic mapping
                    doc = Document(
                        branch_id=branch_id,
                        doc_type=item.get("type", "Unknown"),
                        entity_type=item.get("entity_type", "General"),
                        entity_ref=item.get("entity_ref", ""),
                        file_path=item.get("path", "none"),
                        notes=item.get("notes", "")
                    )
                    db.session.add(doc)
                    doc_count += 1
            db.session.commit()
            logger.info(f"✅ Migrated {doc_count} documents.")
        except Exception as e:
            logger.warning(f"⚠️ Could not migrate documents_data: {e}")

        logger.info("🎉 Migration script completed successfully. Your data is now in SQLAlchemy models!")
        conn.close()

if __name__ == "__main__":
    run_migration()
