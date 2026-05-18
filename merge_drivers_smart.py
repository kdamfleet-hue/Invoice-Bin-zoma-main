# -*- coding: utf-8 -*-
"""Smart merge: deduplicate drivers by iqama number, keep longest name variant."""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(BASE, "all_drivers_merged.json")

with open(input_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

# Remove junk entries
JUNK = ["💡", "col", "الاستخدام"]
clean = {}
for name, data in raw.items():
    if any(j in name for j in JUNK):
        continue
    if len(name.strip()) < 2:
        continue
    clean[name] = data

# Group by iqama (if available)
iqama_groups = {}
no_iqama = {}

for name, data in clean.items():
    iqama = data.get("iqama", "").strip()
    if iqama and len(iqama) >= 8:
        if iqama not in iqama_groups:
            iqama_groups[iqama] = []
        iqama_groups[iqama].append((name, data))
    else:
        # Try to match by phone
        phone = data.get("phone", "").strip()
        if phone and len(phone) >= 8:
            matched = False
            for iq, entries in iqama_groups.items():
                for _, d in entries:
                    if d.get("phone") == phone:
                        iqama_groups[iq].append((name, data))
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                no_iqama[name] = data
        else:
            no_iqama[name] = data

# Merge groups: pick the longest name, merge all data
final_drivers = []

for iqama, entries in iqama_groups.items():
    # Pick longest name (most complete)
    best_name = max([e[0] for e in entries], key=len)
    merged = {}
    for _, data in entries:
        for k, v in data.items():
            if v and (k not in merged or not merged[k] or len(str(v)) > len(str(merged.get(k, "")))):
                merged[k] = v
    merged["name"] = best_name
    merged["iqama"] = iqama
    final_drivers.append(merged)

# Add no-iqama entries (try matching by plate)
for name, data in no_iqama.items():
    plate = data.get("plate", "").strip()
    if plate:
        matched = False
        for fd in final_drivers:
            if fd.get("plate") == plate:
                # Merge into existing
                for k, v in data.items():
                    if v and (k not in fd or not fd[k]):
                        fd[k] = v
                # Keep longer name
                if len(name) > len(fd["name"]):
                    fd["name"] = name
                matched = True
                break
        if not matched:
            data["name"] = name
            final_drivers.append(data)
    else:
        data["name"] = name
        final_drivers.append(data)

# Sort by name
final_drivers.sort(key=lambda x: x.get("name", ""))

# Print final results
print(f"{'='*80}")
print(f"  FINAL MERGED DRIVERS: {len(final_drivers)} unique drivers")
print(f"{'='*80}\n")

FIELD_LABELS = {
    "name": "الاسم",
    "empid": "الرقم الوظيفي",
    "iqama": "🪪 رقم الاقامة",
    "plate": "رقم اللوحة",
    "car": "نوع السيارة",
    "phone": "رقم الجوال",
    "license_expiry": "انتهاء الرخصة",
    "op_card_expiry": "انتهاء بطاقة التشغيل",
    "driver_card_expiry": "انتهاء بطاقة السائق",
    "model": "الموديل",
    "job": "الوظيفة",
}

for i, d in enumerate(final_drivers, 1):
    print(f"┌─ [{i}] {d.get('name', '???')}")
    for key in ["iqama", "empid", "plate", "car", "model", "phone", "license_expiry", "op_card_expiry", "driver_card_expiry", "job"]:
        val = d.get(key, "")
        if val:
            label = FIELD_LABELS.get(key, key)
            print(f"│  {label}: {val}")
    print(f"└{'─'*60}\n")

# Save final merged data
output_path = os.path.join(BASE, "drivers_final_merged.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_drivers, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(final_drivers)} drivers to: {output_path}")



