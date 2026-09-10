import pandas as pd
import os
import sys
import math
from datetime import date

# Ensure project root is in PYTHONPATH for imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app as flask_app
from models.schema import db, Driver, Vehicle, VehicleCustody, Branch, AppSetting
from utils.update_from_excel import safe_date

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weekly_update.xlsx')

def clean_val(v):
    if pd.isna(v) or v is None:
        return ''
    if isinstance(v, float) and math.isnan(v):
        return ''
    s = str(v).strip()
    if s.lower() in ('nan', 'none', '-', '', 'لا يوجد', 'لايوجد'):
        return ''
    return s

def process_active_sheet(df, branch_id, job_default='سائق'):
    updated_veh = 0
    updated_drv = 0
    
    for _, row in df.iterrows():
        plate = clean_val(row.get('رقم اللوحة'))
        if not plate:
            continue
            
        # Vehicle Data
        model = clean_val(row.get('الموديل'))
        v_type = clean_val(row.get('نوع المركبة'))
        capacity = clean_val(row.get('الحمولة'))
        serial = clean_val(row.get('الرقم التسلسلي'))
        pallets = clean_val(row.get('عدد الطبالي'))
        notes = clean_val(row.get('الملاحظات'))
        
        insp_exp = safe_date(row.get('تاريخ انتهاء الفحص الدوري'))
        lic_exp = safe_date(row.get('تاريخ انتهاء رخصة السير'))
        opcard_exp = safe_date(row.get('تاريخ انتهاء بطاقة التشغيل'))
        
        vehicle = Vehicle.query.filter_by(plate_number=plate).first()
        if not vehicle:
            vehicle = Vehicle(plate_number=plate, branch_id=branch_id)
            db.session.add(vehicle)
            
        if model: vehicle.model = model
        if v_type: vehicle.v_type = v_type
        if capacity: vehicle.load_capacity = capacity
        if serial: vehicle.serial_number = serial
        if pallets: vehicle.pallets = pallets
        if notes: vehicle.notes = notes
        vehicle.yard_status = '' # Active in schedule
        
        if insp_exp: vehicle.inspection_expiry = insp_exp
        if lic_exp: vehicle.istimara_expiry = lic_exp
        if opcard_exp: vehicle.insurance_expiry = opcard_exp
        
        updated_veh += 1

        # Driver Data
        empid = clean_val(row.get('الرقم الوظيفي'))
        name = clean_val(row.get('اسم السائق'))
        iqama = clean_val(row.get('رقم الإقامة'))
        phone = clean_val(row.get('رقم الجوال'))
        job = clean_val(row.get('الوظيفة')) or job_default
        
        drivercard_exp = safe_date(row.get('تاريخ انتهاء بطاقة السائق'))
        
        if not empid and not name:
            continue
            
        driver = None
        if empid:
            driver = Driver.query.filter_by(employee_id=empid).first()
        if not driver and iqama:
            driver = Driver.query.filter_by(iqama_number=iqama).first()
            if driver and empid and not driver.employee_id:
                driver.employee_id = empid
            
        if not driver:
            emp_id = empid if empid else (iqama if iqama else f"EXT-{plate}")
            driver = Driver(employee_id=emp_id, branch_id=branch_id)
            db.session.add(driver)
            
        if name: driver.name = name
        if phone: driver.phone = phone
        if job: driver.job_title = job
        if iqama: driver.iqama_number = iqama
        if drivercard_exp: driver.drivercard = str(drivercard_exp)
        driver.status = 'نشط'
        
        updated_drv += 1
        db.session.flush()

        # Link Vehicle to Driver
        VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status='active').update({'status': 'returned'})
        custody = VehicleCustody(driver_id=driver.id, vehicle_id=vehicle.id, received_date=date.today())
        db.session.add(custody)
        
    return updated_veh, updated_drv

def process_spare_sheet(df, branch_id):
    updated_veh = 0
    for _, row in df.iterrows():
        plate = clean_val(row.get('رقم اللوحة'))
        if not plate:
            continue
            
        status = clean_val(row.get('الحالة'))
        model = clean_val(row.get('الموديل'))
        v_type = clean_val(row.get('نوع المركبة'))
        capacity = clean_val(row.get('الحمولة'))
        serial = clean_val(row.get('الرقم التسلسلي'))
        pallets = clean_val(row.get('عدد الطبالي'))
        notes = clean_val(row.get('الملاحظات'))
        
        insp_exp = safe_date(row.get('تاريخ انتهاء الفحص الدوري'))
        lic_exp = safe_date(row.get('تاريخ انتهاء رخصة السير'))
        opcard_exp = safe_date(row.get('تاريخ انتهاء بطاقة التشغيل'))
        
        vehicle = Vehicle.query.filter_by(plate_number=plate).first()
        if not vehicle:
            vehicle = Vehicle(plate_number=plate, branch_id=branch_id)
            db.session.add(vehicle)
            
        if model: vehicle.model = model
        if v_type: vehicle.v_type = v_type
        if capacity: vehicle.load_capacity = capacity
        if serial: vehicle.serial_number = serial
        if pallets: vehicle.pallets = pallets
        if notes: vehicle.notes = notes
        vehicle.yard_status = status if status else 'اسبير'
        
        if insp_exp: vehicle.inspection_expiry = insp_exp
        if lic_exp: vehicle.istimara_expiry = lic_exp
        if opcard_exp: vehicle.insurance_expiry = opcard_exp
        
        # Unlink any driver
        VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status='active').update({'status': 'returned'})
        
        updated_veh += 1
        
    return updated_veh

def main():
    if not os.path.isfile(EXCEL_PATH):
        print(f"Excel file not found: {EXCEL_PATH}")
        return
        
    print("Loading Excel file...")
    try:
        df_public = pd.read_excel(EXCEL_PATH, sheet_name='سجل النقل', header=3)
        df_private = pd.read_excel(EXCEL_PATH, sheet_name='سجل الخاص', header=3)
        df_spare = pd.read_excel(EXCEL_PATH, sheet_name='الأسبير والمعطلة', header=2)
    except Exception as e:
        print(f"Error loading sheets: {e}")
        return

    with flask_app.app_context():
        branch = Branch.query.filter(Branch.name.like('%الدمام%')).first()
        branch_id = branch.id if branch else 1
        
        print("Processing Public Transport...")
        v1, d1 = process_active_sheet(df_public, branch_id, job_default='سائق نقل عام')
        print(f"  -> Vehicles: {v1}, Drivers: {d1}")
        
        print("Processing Private Transport...")
        v2, d2 = process_active_sheet(df_private, branch_id, job_default='سائق نقل خاص')
        print(f"  -> Vehicles: {v2}, Drivers: {d2}")
        
        print("Processing Spares/Broken...")
        v3 = process_spare_sheet(df_spare, branch_id)
        print(f"  -> Vehicles: {v3}")
        
        db.session.commit()
        
        print("Re-populating schedule dashboard JSON...")
        import populate_schedule
        print("✅ Data Import & Schedule Update Successful!")

if __name__ == "__main__":
    main()
