import json, re

sources = {}
full_data = {}

def merge_into(name, data, source):
    name = name.strip()
    if not name: return
    sources.setdefault(name, []).append(source)
    if name not in full_data:
        full_data[name] = {"name": name, "empid": "", "iqama": "", "plate": "", "car": "", "phone": ""}
    for field in ["empid", "iqama", "plate", "car", "phone"]:
        val = str(data.get(field, "")).strip()
        if val and val != "None" and not full_data[name].get(field, ""):
            full_data[name][field] = val

# 1. drivers_data.js
with open("drivers_data.js", "r", encoding="utf-8") as f:
    c = f.read().replace("const driversData = ", "").strip().rstrip(";")
    for d in json.loads(c):
        merge_into(d["name"], d, "drivers_data.js")

# 2. all_drivers_merged.json
with open("all_drivers_merged.json", "r", encoding="utf-8") as f:
    for name, info in json.load(f).items():
        merge_into(name, info, "all_drivers_merged.json")

# 3. drivers_final_merged.json
with open("drivers_final_merged.json", "r", encoding="utf-8") as f:
    for d in json.load(f):
        merge_into(d.get("name", ""), d, "drivers_final_merged.json")

# 4. employees_data.md
with open("employees_data.md", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("|") and "---" not in line and "#" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2 and not parts[0].isdigit() and len(parts[0]) > 3 and "الاسم" not in parts[0]:
                merge_into(parts[0], {"iqama": parts[1] if len(parts) > 1 else ""}, "employees_data.md")

# 5. washing_data.js
with open("static/washing_data.js", "r", encoding="utf-8") as f:
    content = f.read()
    pattern = r'plate:"([^"]*)",type:"([^"]*)",driver:"([^"]*)"'
    for m in re.finditer(pattern, content):
        plate, car_type, driver = m.groups()
        if driver:
            merge_into(driver, {"plate": plate, "car": car_type}, "washing_data.js")

# Filter junk
def is_junk(name):
    if not name: return True
    if name.isdigit(): return True
    if len(name) < 3: return True
    junk = ["إجمالي", "تم إعداد", "الاستخدام", "بيان استهلاك", "💡"]
    return any(j in name for j in junk)

clean = {k: v for k, v in full_data.items() if not is_junk(k)}

# Check missing
in_js = set()
with open("drivers_data.js", "r", encoding="utf-8") as f:
    c = f.read().replace("const driversData = ", "").strip().rstrip(";")
    for d in json.loads(c):
        in_js.add(d["name"])

missing = {k: v for k, v in clean.items() if k not in in_js}
print("Total unique: %d | In JS: %d | MISSING: %d" % (len(clean), len(in_js), len(missing)))
with open("missing_names.txt", "w", encoding="utf-8") as mf:
    for name in sorted(missing.keys()):
        d = missing[name]
        src = ", ".join(sources[name])
        mf.write("MISSING: %s | iq=%s | pl=%s | car=%s | ph=%s | from: %s\n" % (name, d["iqama"], d["plate"], d["car"], d["phone"], src))
print("Missing names saved to missing_names.txt")

# Save ULTIMATE
final = sorted(clean.values(), key=lambda x: x["name"])
js_out = "const driversData = " + json.dumps(final, ensure_ascii=False, indent=2) + ";\n"
with open("drivers_data.js", "w", encoding="utf-8") as f:
    f.write(js_out)

with open("drivers_clean.json", "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

total = len(final)
w_iq = sum(1 for d in final if d["iqama"])
w_pl = sum(1 for d in final if d["plate"])
w_car = sum(1 for d in final if d["car"])
w_ph = sum(1 for d in final if d["phone"])
print("\nFINAL: %d drivers | iqama: %d | plate: %d | car: %d | phone: %d" % (total, w_iq, w_pl, w_car, w_ph))
