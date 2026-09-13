"""Deterministic reconciliation helpers for fleet and GPS vehicle records."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any, Iterable

from helpers import normalize_plate


def _text(value: Any) -> str:
    return str(value or "").strip()


def _identity(record: dict[str, Any]) -> tuple[str, str] | None:
    """Prefer durable IDs, then serials, and finally normalized plates."""
    for field in ("vehicle_id", "internal_id", "erp_vehicle_id"):
        value = _text(record.get(field))
        if value:
            return (field, value)
    serial = _text(record.get("serial_number") or record.get("vserial") or record.get("vin"))
    if serial:
        return ("serial_number", serial.upper())
    plate = normalize_plate(record.get("plate") or record.get("plate_number"))
    return ("plate", plate) if plate else None


def _number_key(record: dict[str, Any]) -> str:
    plate = _text(record.get("plate") or record.get("plate_number"))
    return "".join(ch for ch in plate if ch.isdigit())


def _index(records: Iterable[dict[str, Any]]) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], Counter]:
    index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    plates: Counter = Counter()
    for record in records:
        key = _identity(record)
        if key:
            index[key].append(record)
        plate = normalize_plate(record.get("plate") or record.get("plate_number"))
        if plate:
            plates[plate] += 1
    return index, plates


def reconcile_records(fleet_records: Iterable[dict[str, Any]], gps_records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compare two record sets without making automatic data corrections.

    Matching order is durable internal ID, serial/VIN, then normalized plate.
    Same-number/different-letter plates are deliberately returned as manual
    review items rather than being silently merged.
    """
    fleet = list(fleet_records or [])
    gps = list(gps_records or [])
    fleet_index, fleet_plates = _index(fleet)
    gps_index, gps_plates = _index(gps)
    fleet_plate_index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in fleet:
        plate = normalize_plate(record.get("plate") or record.get("plate_number"))
        if plate:
            fleet_plate_index[plate].append(record)
    matched: list[dict[str, Any]] = []
    gps_only: list[dict[str, Any]] = []
    manual_review: list[dict[str, Any]] = []
    matched_fleet_ids: set[int] = set()

    for gps_record in gps:
        gps_key = _identity(gps_record)
        candidates = fleet_index.get(gps_key, []) if gps_key else []
        if not candidates:
            plate = normalize_plate(gps_record.get("plate") or gps_record.get("plate_number"))
            candidates = fleet_plate_index.get(plate, []) if plate else []
        if candidates:
            fleet_record = candidates[0]
            matched.append({"match_type": gps_key[0] if gps_key else "plate", "gps": gps_record, "fleet": fleet_record})
            matched_fleet_ids.add(id(fleet_record))
            continue

        gps_number = _number_key(gps_record)
        number_candidates = [
            record for record in fleet
            if gps_number and _number_key(record) == gps_number
        ]
        if number_candidates:
            manual_review.append({
                "reason": "same_number_different_letters",
                "gps": gps_record,
                "fleet_candidates": number_candidates,
            })
        else:
            gps_only.append(gps_record)

    fleet_only = []
    for fleet_record in fleet:
        key = _identity(fleet_record)
        if id(fleet_record) not in matched_fleet_ids and not any(fleet_record in item.get("fleet_candidates", []) for item in manual_review):
            fleet_only.append(fleet_record)

    duplicate_keys = sorted({key for key, count in (fleet_plates | gps_plates).items() if count > 1})
    return {
        "gps_count": len(gps),
        "fleet_count": len(fleet),
        "matched_count": len(matched),
        "gps_only_count": len(gps_only),
        "fleet_only_count": len(fleet_only),
        "manual_review_count": len(manual_review),
        "duplicate_count": len(duplicate_keys),
        "duplicate_keys": duplicate_keys,
        "matched": matched,
        "gps_only": gps_only,
        "fleet_only": fleet_only,
        "manual_review": manual_review,
    }


def nonmatch_rate(result: dict[str, Any]) -> float:
    """Return the percentage of source records not exactly matched."""
    total = max(int(result.get("gps_count", 0)), int(result.get("fleet_count", 0)))
    unmatched = int(result.get("gps_only_count", 0)) + int(result.get("fleet_only_count", 0))
    return round(unmatched / total * 100, 2) if total else 0.0


def validate_publish_gate(result: dict[str, Any], snapshot_generated_at: Any, *, now: datetime | None = None,
                          max_age_seconds: int = 900, max_nonmatch_rate_pct: float = 5.0) -> dict[str, Any]:
    """Return a deterministic decision for publishing a GPS snapshot."""
    now = now or datetime.utcnow()
    try:
        generated = snapshot_generated_at if isinstance(snapshot_generated_at, datetime) else datetime.fromisoformat(str(snapshot_generated_at).replace("Z", "+00:00"))
        if generated.tzinfo and not now.tzinfo:
            now = now.replace(tzinfo=generated.tzinfo)
        age_seconds = max(0, int((now - generated).total_seconds()))
    except (TypeError, ValueError):
        age_seconds = None
    rate = nonmatch_rate(result)
    reasons = []
    if age_seconds is None:
        reasons.append("invalid_snapshot_timestamp")
    elif age_seconds > max_age_seconds:
        reasons.append("snapshot_too_old")
    if rate > max_nonmatch_rate_pct:
        reasons.append("nonmatch_rate_above_threshold")
    return {
        "publish": not reasons,
        "age_seconds": age_seconds,
        "max_age_seconds": max_age_seconds,
        "nonmatch_rate_pct": rate,
        "max_nonmatch_rate_pct": max_nonmatch_rate_pct,
        "reasons": reasons,
    }


def _expiry_status(value: Any) -> str:
    if not value:
        return "لا يوجد"
    try:
        parsed = value if isinstance(value, date) else datetime.fromisoformat(str(value)[:10]).date()
    except (TypeError, ValueError):
        return "غير صالح"
    return "منتهي" if parsed < date.today() else "ساري المفعول"


def build_dashboard_data(fleet_records: Iterable[dict[str, Any]], gps_records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build the GPS dashboard contract from live records and reconciliation output."""
    fleet = list(fleet_records or [])
    gps = list(gps_records or [])
    reconciliation = reconcile_records(fleet, gps)
    fleet_by_plate = {
        normalize_plate(row.get("plate") or row.get("plate_number")): row
        for row in fleet
        if normalize_plate(row.get("plate") or row.get("plate_number"))
    }
    rows = []
    for gps_row in gps:
        plate = gps_row.get("plate") or gps_row.get("plate_number") or ""
        fleet_row = fleet_by_plate.get(normalize_plate(plate), {})
        inspection = _expiry_status(fleet_row.get("inspection_expiry") or fleet_row.get("inspect"))
        insurance = _expiry_status(fleet_row.get("insurance_expiry") or fleet_row.get("license"))
        driver = gps_row.get("driver") or fleet_row.get("driver") or "غير محدد"
        issues = []
        if not driver or driver == "غير محدد":
            issues.append("Missing driver")
        if inspection == "منتهي":
            issues.append("Expired inspection")
        if insurance == "منتهي":
            issues.append("Expired insurance")
        score = len(issues) * 10 + (1 if not fleet_row else 0)
        priority = "عالية" if score >= 20 else ("متوسطة" if score >= 10 else "منخفضة")
        rows.append({
            "plate": plate,
            "vehicle_type": gps_row.get("asset_type") or gps_row.get("v_type") or fleet_row.get("v_type") or "غير محدد",
            "priority": priority,
            "driver": driver,
            "inspection_status": inspection,
            "insurance_status": insurance,
            "issues": issues,
            "score": score,
        })

    priority_order = ["عالية", "متوسطة", "منخفضة"]
    vehicle_types = sorted({row["vehicle_type"] for row in rows if row["vehicle_type"]}) or ["غير محدد"]
    filter_order = ["الكل"] + vehicle_types

    def summarize(items: list[dict[str, Any]], label: str) -> dict[str, Any]:
        counts = Counter(row["priority"] for row in items)
        expired_inspection = sum(row["inspection_status"] == "منتهي" for row in items)
        expired_insurance = sum(row["insurance_status"] == "منتهي" for row in items)
        total = len(items)
        return {
            "label": label, "total": total, "high": counts["عالية"], "medium": counts["متوسطة"], "low": counts["منخفضة"],
            "high_pct": round(counts["عالية"] / total * 100, 1) if total else 0,
            "medium_pct": round(counts["متوسطة"] / total * 100, 1) if total else 0,
            "low_pct": round(counts["منخفضة"] / total * 100, 1) if total else 0,
            "missing_drivers": sum("Missing driver" in row["issues"] for row in items),
            "expired_inspection": expired_inspection,
            "expired_insurance": expired_insurance,
            "expired_any": expired_inspection + expired_insurance,
        }

    filter_data = {"الكل": summarize(rows, "الكل")}
    watchlists = {"الكل": sorted(rows, key=lambda row: (-row["score"], row["plate"]))[:10]}
    priority_by_type = {}
    vehicle_counts = {}
    for vehicle_type in vehicle_types:
        subset = [row for row in rows if row["vehicle_type"] == vehicle_type]
        filter_data[vehicle_type] = summarize(subset, vehicle_type)
        watchlists[vehicle_type] = sorted(subset, key=lambda row: (-row["score"], row["plate"]))[:10]
        vehicle_counts[vehicle_type] = len(subset)
        priority_by_type[vehicle_type] = {priority: sum(row["priority"] == priority for row in subset) for priority in priority_order}

    overall = filter_data["الكل"]
    generated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return {
        "meta": {
            "source": "live_gps_api",
            "generated_at": generated_at,
            "reconciliation": {
                "gps_count": reconciliation["gps_count"],
                "fleet_count": reconciliation["fleet_count"],
                "matched_count": reconciliation["matched_count"],
                "gps_only_count": reconciliation["gps_only_count"],
                "fleet_only_count": reconciliation["fleet_only_count"],
                "manual_review_count": reconciliation["manual_review_count"],
                "duplicate_count": reconciliation["duplicate_count"],
                "nonmatch_rate_pct": nonmatch_rate(reconciliation),
            },
            "publish_gate": validate_publish_gate(reconciliation, generated_at),
        },
        "priorityOrder": priority_order,
        "vehicleTypes": vehicle_types,
        "colors": {"عالية": "#E73B4F", "متوسطة": "#D4A740", "منخفضة": "#34C563"},
        "filterOrder": filter_order,
        "overall": {
            "totalVehicles": len(rows), "highPriority": overall["high"], "missingDrivers": overall["missing_drivers"],
            "expiredInspections": overall["expired_inspection"], "expiredInsurances": overall["expired_insurance"],
            "priorityCounts": {priority: overall["high" if priority == "عالية" else "medium" if priority == "متوسطة" else "low"] for priority in priority_order},
            "vehicleCounts": vehicle_counts, "priorityByType": priority_by_type,
        },
        "filterData": filter_data,
        "watchlists": watchlists,
    }
