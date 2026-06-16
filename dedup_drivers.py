import json

# Load current data
data = json.loads(open("drivers_clean.json", "r", encoding="utf-8").read())

# Build iqama -> entries map
iqama_groups = {}
no_iqama = []
for d in data:
    iq = d.get("iqama", "").strip()
    if iq:
        iqama_groups.setdefault(iq, []).append(d)
    else:
        no_iqama.append(d)

# Merge duplicates by iqama: keep the one with longest name + merge all fields
merged = []
for iq, entries in iqama_groups.items():
    # Pick the entry with the longest name
    best = max(entries, key=lambda x: len(x.get("name", "")))
    # Fill from other entries
    for e in entries:
        for field in ["empid", "iqama", "plate", "car", "phone"]:
            if not best.get(field, "") and e.get(field, ""):
                best[field] = e[field]
    merged.append(best)

# Add no-iqama entries, but deduplicate by plate
seen_plates = set()
for m in merged:
    pl = m.get("plate", "").replace(" ", "")
    if pl:
        seen_plates.add(pl)

for d in no_iqama:
    pl = d.get("plate", "").replace(" ", "")
    name = d.get("name", "")
    # Skip junk
    if not name or len(name) < 3:
        continue
    if name.isdigit():
        continue
    # Skip "Employee Name" header row
    if "Employee" in name or "اسم" in name:
        continue
    # Check if plate already exists
    if pl and pl in seen_plates:
        # Find and merge
        for m in merged:
            if m.get("plate", "").replace(" ", "") == pl:
                if not m.get("car", "") and d.get("car", ""):
                    m["car"] = d["car"]
                break
    else:
        merged.append(d)
        if pl:
            seen_plates.add(pl)

# Sort by name
merged.sort(key=lambda x: x["name"])

# Fix known iqama errors from employees_data.md:
# "اجيت راجا" has two iqamas listed: 2441077944 and 2461544377
# 2441077944 is actually "محمد عبدالرحمن المندوه"'s iqama
# So اجيت راجا should be 2461544377 only
for d in merged:
    if d["name"] == "اجيت راجا" and d.get("iqama") == "2441077944":
        d["iqama"] = "2461544377"

# Save
total = len(merged)
js_out = "const driversData = " + json.dumps(merged, ensure_ascii=False, indent=2) + ";\n"
with open("drivers_data.js", "w", encoding="utf-8") as f:
    f.write(js_out)

with open("drivers_clean.json", "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

w_iq = sum(1 for d in merged if d["iqama"])
w_pl = sum(1 for d in merged if d["plate"])
w_car = sum(1 for d in merged if d["car"])
w_ph = sum(1 for d in merged if d["phone"])
print("FINAL DEDUPED: %d drivers | iqama: %d | plate: %d | car: %d | phone: %d" % (total, w_iq, w_pl, w_car, w_ph))

# Verify خالد
found = [d for d in merged if "خالد" in d["name"]]
for d in found:
    print("KHALED: %s | iq=%s | pl=%s | car=%s" % (d["name"], d["iqama"], d["plate"], d["car"]))
