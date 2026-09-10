import json
from app import app
from models.schema import db, Driver, VehicleCustody, AppSetting

with app.app_context():
    # We'll pull active drivers and build the main schedule list
    active_drivers = Driver.query.filter_by(status='نشط').all()
    
    main_data = []
    
    for d in active_drivers:
        # Get their assigned vehicle
        custody = VehicleCustody.query.filter_by(driver_id=d.id, status='active').first()
        v = custody.vehicle if custody else None
        
        row = {
            "empid": d.employee_id or "",
            "name": d.name or "",
            "iqama": d.iqama_number or "",
            "job": d.job_title or "",
            "phone": d.phone or "",
            "drivercard": d.drivercard or "",
            "empNotes": d.empNotes or "",
            "plate": v.plate_number if v else "",
            "model": v.model if v else "",
            "type": v.v_type if v else "",
            "pallets": v.pallets if v else "",
            "capacity": v.load_capacity if v else "",
            "serial": v.serial_number if v else "",
            "inspect": str(v.inspection_expiry) if v and v.inspection_expiry else "",
            "license": str(v.istimara_expiry) if v and v.istimara_expiry else "",
            "opcard": str(v.insurance_expiry) if v and v.insurance_expiry else "",
            "notes": v.notes if v else ""
        }
        main_data.append(row)
    
    # We could also pull spare vehicles for the 'spare' list
    from models.schema import Vehicle
    spare_vehicles = Vehicle.query.filter(Vehicle.yard_status.in_(['اسبير', 'معطلة', 'صيانة', 'فحص'])).all()
    spare_data = []
    for v in spare_vehicles:
        spare_data.append({
            "name": v.yard_status or "اسبير",
            "plate": v.plate_number or "",
            "typemodel": f"{v.v_type or ''} {v.model or ''}".strip(),
            "pallets": v.pallets or "",
            "capacity": v.load_capacity or "",
            "notes": v.notes or ""
        })

    sd = {
        "main": main_data,
        "spare": spare_data
    }
    
    # Direct DB update
    setting = AppSetting.query.filter_by(key="schedule_data").first()
    if not setting:
        setting = AppSetting()
        setting.key = "schedule_data"
        setting.value = json.dumps(sd)
        db.session.add(setting)
    else:
        setting.value = json.dumps(sd)
    
    db.session.commit()
    print(f"Schedule populated with {len(main_data)} active drivers and {len(spare_data)} spare vehicles.")
