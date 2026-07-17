import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """def api_fleet_data():
    from models.schema import Driver, VehicleCustody
    drivers = Driver.query.all()
    fleet = []
    for d in drivers:
        custody = VehicleCustody.query.filter_by(driver_id=d.id, status='active').first()
        v = custody.vehicle if custody and custody.vehicle else None
        
        fleet.append({
            "id": d.id,
            "name": d.name or "",
            "empid": d.employee_id or "",
            "iqama": d.iqama_number or "",
            "plate": v.plate_number if v else "",
            "car": v.v_type if v else "",
            "phone": d.phone or "",
            "drivercard": "",
            "job": d.job_title or "",
            "empNotes": d.notes or "",
            "model": v.model if v else "",
            "pallets": "",
            "load": "",
            "vserial": "",
            "inspect": "",
            "license": "",
            "opcard": "",
            "notes": ""
        })
    response = jsonify(fleet)"""

# replace the function body
content = re.sub(
    r'def api_fleet_data\(\):.*?response = jsonify\(fleet\)',
    replacement,
    content,
    flags=re.DOTALL
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.py api_fleet_data")
