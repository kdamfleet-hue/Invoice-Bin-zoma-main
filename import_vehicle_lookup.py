"""Import driver data from vehicle_lookup_v2.xlsx into the SQLite database."""
import os, sqlite3, re
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite")
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "New", "vehicle_lookup_v2.xlsx")


def normalize_plate(plate):
    if not plate or str(plate).strip() == "":
        return ""
    plate = str(plate).strip()
    plate = re.sub(r"\s+", " ", plate)
    return plate


def main():
    df = pd.read_excel(EXCEL_PATH)
    print(f"Read {len(df)} records from vehicle_lookup_v2.xlsx")
    print(f"Columns: {list(df.columns)}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Ensure columns exist (old init_db.py may not have them)
    for col in ["empid", "iqama", "phone"]:
        try:
            cur.execute(f"ALTER TABLE drivers ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass  # column already exists

    # Read existing drivers
    cur.execute("SELECT id, name, plate, car, iqama, phone FROM drivers")
    existing = {row[1]: dict(zip(["id", "name", "plate", "car", "iqama", "phone"], row)) for row in cur.fetchall()}
    print(f"Existing drivers in DB: {len(existing)}")

    added = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():
        plate = normalize_plate(row.get("رقم اللوحة", ""))
        name = str(row.get("اسم المستخدم الفعلي", "")).strip()
        iqama = str(row.get("رقم هوية المستخدم الفعلي", "")).strip()
        brand = str(row.get("الماركة", "")).strip()
        model = str(row.get("الطراز", "")).strip()
        year = str(row.get("سنة الصنع", "")).strip()

        # Build car description
        car_parts = []
        if brand and brand != "nan":
            car_parts.append(brand)
        if model and model != "nan":
            car_parts.append(model)
        if year and year != "nan":
            car_parts.append(year)
        car = " ".join(car_parts)

        if not name or name == "nan" or not name.strip():
            skipped += 1
            continue

        if iqama == "nan":
            iqama = ""

        # Check if driver already exists (by name or iqama)
        found = None
        if name in existing:
            found = existing[name]
        else:
            # Try to find by iqama
            for k, v in existing.items():
                if iqama and v.get("iqama") == iqama:
                    found = v
                    break

        if found:
            # Update missing fields
            changes = []
            fid = found["id"]
            if plate and (not found.get("plate") or found["plate"] in ("None", "", "لا يوجد")):
                changes.append(("plate", plate))
            if car and (not found.get("car") or found["car"] in ("None", "", "لا يوجد")):
                changes.append(("car", car))
            if iqama and (not found.get("iqama") or found["iqama"] in ("None", "", "لا يوجد")):
                changes.append(("iqama", iqama))

            if changes:
                for col, val in changes:
                    cur.execute(f"UPDATE drivers SET {col} = ? WHERE id = ?", (val, fid))
                updated += 1
        else:
            # Insert new driver
            cur.execute(
                "INSERT INTO drivers (name, plate, car, iqama, phone) VALUES (?, ?, ?, ?, ?)",
                (name, plate, car, iqama, ""),
            )
            existing[name] = {"id": cur.lastrowid, "name": name, "plate": plate, "car": car, "iqama": iqama, "phone": ""}
            added += 1

    conn.commit()
    conn.close()

    print(f"\n=== Results ===")
    print(f"Added: {added}")
    print(f"Updated: {updated}")
    print(f"Skipped (no name): {skipped}")
    print(f"Total in DB now: {len(existing)}")


if __name__ == "__main__":
    main()


