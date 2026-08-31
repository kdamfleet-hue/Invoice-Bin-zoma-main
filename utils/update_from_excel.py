import pandas as pd
import os
import sys

# Ensure project root is in PYTHONPATH for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from models.schema import db, Driver, Vehicle, VehicleCustody

# Path to the merged drivers/vehicles Excel file (copied locally to avoid permission issues)
def _resolve_excel_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(root, "excel_data.xlsx"),
        os.path.join(root, "جدول_بيانات_السائقين_والمركبات_المدمج_كامل.xlsx"),
        os.path.join("/app", "جدول_بيانات_السائقين_والمركبات_المدمج_كامل.xlsx"),
        os.path.join("/persist", "جدول_بيانات_السائقين_والمركبات_المدمج_كامل.xlsx"),
        os.path.join(root, "DB-WORK", "جدول_بيانات_السائقين_والمركبات_المدمج_كامل.xlsx"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return candidates[0]

EXCEL_PATH = _resolve_excel_path()

def _hijri_to_gregorian(hy, hm, hd):
    """Convert Hijri (Islamic) date to Gregorian using the Kuwaiti algorithm."""
    hy, hm, hd = int(hy), int(hm), int(hd)
    jd = int((11 * hy + 3) / 30) + 354 * hy + 30 * hm - int((hm - 1) / 2) + hd + 1948440 - 385
    # Julian day to Gregorian
    l = jd + 68569
    n = int((4 * l) / 146097)
    l = l - int((146097 * n + 3) / 4)
    i = int((4000 * (l + 1)) / 1461001)
    l = l - int((1461 * i) / 4) + 31
    j = int((80 * l) / 2447)
    day = l - int((2447 * j) / 80)
    l = int(j / 11)
    month = j + 2 - 12 * l
    year = 100 * (n - 49) + i + l
    from datetime import date
    return date(int(year), int(month), int(day))


def safe_date(val):
    """Parse Gregorian or Hijri (yyyy-mm-dd / yyyy/mm/dd) into a date.
    Rejects empty values; converts Hijri years (approx 1300-1600) to Gregorian.
    """
    try:
        if val is None:
            return None
        if isinstance(val, float) and pd.isna(val):
            return None
        # Already a date/datetime
        if hasattr(val, 'year') and hasattr(val, 'month') and hasattr(val, 'day') and not isinstance(val, str):
            d = val if hasattr(val, 'hour') is False or not hasattr(val, 'date') else (val.date() if hasattr(val, 'date') else val)
            try:
                if hasattr(d, 'date'):
                    d = d.date()
            except Exception:
                pass
            if getattr(d, 'year', 0) >= 1900 and getattr(d, 'year', 0) <= 2100:
                return d
            if 1300 <= getattr(d, 'year', 0) <= 1600:
                return _hijri_to_gregorian(d.year, d.month, d.day)
            return None

        s = str(val).strip()
        if not s or s.lower() in ('nan', 'nat', 'none', '-'):
            return None
        s = s.replace('/', '-').replace('.', '-')
        parts = [p for p in s.split('-') if p]
        if len(parts) >= 3:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            if 1300 <= y <= 1600:
                return _hijri_to_gregorian(y, m, d)
            if 1900 <= y <= 2100:
                from datetime import date
                return date(y, m, d)

        result = pd.to_datetime(val, errors='coerce')
        if result is pd.NaT or pd.isnull(result):
            return None
        d = result.date()
        if 1300 <= d.year <= 1600:
            return _hijri_to_gregorian(d.year, d.month, d.day)
        if d.year < 1900 or d.year > 2100:
            return None
        return d
    except Exception:
        return None

        # Handle pandas NaT or NaN floats
        if isinstance(val, float) and pd.isna(val):
            return None
        result = pd.to_datetime(val, errors='coerce')
        if result is pd.NaT or pd.isnull(result):
            return None
        d = result.date()
        # Reject clearly out-of-range years (hijri years like 1448 or future garbage)
        if d.year < 1900 or d.year > 2100:
            return None
        return d
    except Exception:
        return None

def upsert_driver_vehicle(row, branch_id=None):
    """Insert or update a driver and its vehicle based on a DataFrame row.
    The function maps Arabic column names (as provided by the user) to the model fields.
    """
    # ----- Driver fields -----
    empid = str(row.get('الرقم الوظيفي') or row.get('employee_id') or '').strip()
    if not empid:
        return
    name = str(row.get('اسم السائق') or row.get('name') or '').strip()
    iqama = str(row.get('رقم الإقامة') or row.get('iqama') or '').strip()
    phone = str(row.get('رقم الجوال') or row.get('phone') or '').strip()
    job = str(row.get('الوظيفة') or row.get('job') or '').strip()
    birth_date = row.get('تاريخ الميلاد') or row.get('birth_date')

    # ----- Vehicle fields -----
    plate = str(row.get('رقم اللوحة') or row.get('plate') or '').strip()
    model = str(row.get('الموديل') or row.get('model') or '').strip()
    v_type = str(row.get('نوع المركبة') or row.get('car') or '').strip()
    load_capacity = str(row.get('الحمولة') or row.get('load_capacity') or '').strip()
    serial_number = str(row.get('الرقم التسلسلي') or row.get('serial_number') or '').strip()
    inspection_expiry = row.get('تاريخ انتهاء الفحص الدوري') or row.get('inspection_expiry')
    license_expiry = row.get('تاريخ انتهاء رخصة السير') or row.get('license_expiry')
    notes = str(row.get('الملاحظات') or row.get('notes') or '').strip()

    # ----- Upsert Driver -----
    driver = Driver.query.filter_by(employee_id=empid).first()
    if not driver:
        driver = Driver(employee_id=empid, branch_id=branch_id or 1)
        db.session.add(driver)
    driver.name = name
    driver.phone = phone
    driver.job_title = job
    # Only set iqama if it's unique
    if iqama:
        existing_iqama = Driver.query.filter(Driver.iqama_number == iqama, Driver.id != driver.id).first()
        if not existing_iqama:
            driver.iqama_number = iqama
    driver.birth_date = safe_date(birth_date)
    driver.status = "متاح"

    # ----- Upsert Vehicle (if a plate is provided) -----
    if plate and not pd.isna(plate):
        vehicle = Vehicle.query.filter_by(plate_number=plate).first()
        if not vehicle:
            vehicle = Vehicle(plate_number=plate, branch_id=branch_id or 1)
            db.session.add(vehicle)
        vehicle.model = model
        vehicle.v_type = v_type
        vehicle.load_capacity = load_capacity
        vehicle.serial_number = serial_number
        insp = safe_date(inspection_expiry)
        lic = safe_date(license_expiry)
        # Fill missing document dates only (do not wipe existing values)
        if insp and not vehicle.inspection_expiry:
            vehicle.inspection_expiry = insp
        if lic and not vehicle.istimara_expiry:
            vehicle.istimara_expiry = lic
        vehicle.notes = notes

        # ----- Link driver and vehicle via custody -----
        custody = VehicleCustody.query.filter_by(driver_id=driver.id, vehicle_id=vehicle.id).first()
        if not custody:
            custody = VehicleCustody(
                driver_id=driver.id,
                vehicle_id=vehicle.id,
                received_date=db.func.current_date()
            )
            db.session.add(custody)

def main():
    if not os.path.isfile(EXCEL_PATH):
        print(f"Excel file not found: {EXCEL_PATH}")
        return
    df = pd.read_excel(EXCEL_PATH)
    app = flask_app
    with app.app_context():
        for _, row in df.iterrows():
            upsert_driver_vehicle(row)
        db.session.commit()
        print("✅ تم تحديث قاعدة البيانات من ملف Excel بنجاح.")

if __name__ == "__main__":
    main()


def fill_missing_vehicle_docs(excel_path=None):
    """Fill only missing istimara/inspection dates on vehicles from merged Excel.
    Does not delete or overwrite existing document dates.
    Returns dict stats.
    """
    path = excel_path or EXCEL_PATH
    stats = {"success": False, "path": path, "rows": 0, "vehicles_touched": 0, "dates_filled": 0, "error": None}
    if not os.path.isfile(path):
        stats["error"] = f"Excel file not found: {path}"
        return stats
    try:
        df = pd.read_excel(path)
        stats["rows"] = len(df)
        with flask_app.app_context():
            for _, row in df.iterrows():
                plate = str(row.get('رقم اللوحة') or row.get('plate') or '').strip()
                if not plate or plate.lower() in ('nan', 'none', '-'):
                    continue
                vehicle = Vehicle.query.filter_by(plate_number=plate).first()
                if not vehicle:
                    plate_norm = " ".join(plate.split())
                    vehicle = Vehicle.query.filter(Vehicle.plate_number.ilike(f"%{plate_norm}%")).first()
                if not vehicle:
                    continue
                stats["vehicles_touched"] += 1
                insp = safe_date(row.get('تاريخ انتهاء الفحص الدوري') or row.get('inspection_expiry'))
                lic = safe_date(row.get('تاريخ انتهاء رخصة السير') or row.get('license_expiry'))
                if insp and not vehicle.inspection_expiry:
                    vehicle.inspection_expiry = insp
                    stats["dates_filled"] += 1
                if lic and not vehicle.istimara_expiry:
                    vehicle.istimara_expiry = lic
                    stats["dates_filled"] += 1
                serial = str(row.get('الرقم التسلسلي') or row.get('serial_number') or '').strip()
                if serial and serial.lower() != 'nan' and not vehicle.serial_number:
                    vehicle.serial_number = serial
            db.session.commit()
        stats["success"] = True
    except Exception as e:
        stats["error"] = str(e)
        try:
            db.session.rollback()
        except Exception:
            pass
    return stats

