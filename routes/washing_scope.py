"""Scope washing schedule to the 73 Dammam vehicles only."""
from helpers import normalize_plate, blob_get, blob_set


def washing_dammam_only(stored):
    from routes.dammam import dammam_rows_by_plate
    catalog = dammam_rows_by_plate()
    by_plate = {}
    if isinstance(stored, list):
        for row in stored:
            if not isinstance(row, dict):
                continue
            key = normalize_plate(row.get("plate"))
            if key:
                by_plate[key] = row
    out = []
    for i, (key, meta) in enumerate(catalog.items(), start=1):
        prev = by_plate.get(key) or {}
        months = prev.get("m")
        if not isinstance(months, list) or len(months) != 12:
            months = [0] * 12
        vtype = prev.get("type") or " ".join(x for x in (meta.get("make"), meta.get("model")) if x)
        out.append({
            "id": prev.get("id") or i,
            "plate": meta.get("plate"),
            "type": vtype,
            "driver": prev.get("driver") or "",
            "m": months,
            "price": prev.get("price"),
        })
    return out


def merge_washing_post(incoming):
    from routes.dammam import dammam_plate_set
    stored = blob_get("washing_schedule")
    stored_list = stored if isinstance(stored, list) else []
    allowed = dammam_plate_set()
    keep = [r for r in stored_list if isinstance(r, dict) and normalize_plate(r.get("plate")) not in allowed]
    filtered = []
    for row in incoming if isinstance(incoming, list) else []:
        if isinstance(row, dict) and normalize_plate(row.get("plate")) in allowed:
            filtered.append(row)
    merged = keep + filtered if filtered else stored_list
    if filtered:
        blob_set("washing_schedule", merged)
    return washing_dammam_only(merged)
