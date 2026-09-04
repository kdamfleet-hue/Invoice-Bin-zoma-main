"""Periodic vehicle speed rules and alert persistence.

Design reminder: deterministic, operational, and conservative. Alerts use fresh readings only,
classify vehicles from the existing Vehicle.v_type field, and never log provider credentials.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

SPEED_LIMITS = {"truck": 80, "light": 120, "bus": 90}


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def classify_vehicle(vehicle_type: Any, model: Any = "") -> str | None:
    text = normalize_text(f"{vehicle_type} {model}")
    if any(word in text for word in ("شاحنة", "نقل ثقيل", "تريلا", "قلاب", "truck", "heavy")):
        return "truck"
    if any(word in text for word in ("حافلة", "باص", "نقل عام", "bus", "coach")):
        return "bus"
    if any(word in text for word in ("سيارة", "خفيف", "نقل خاص", "light", "sedan", "pickup")):
        return "light"
    return None


def _plate_key(value: Any) -> str:
    from helpers import normalize_plate
    return normalize_plate(value)


def _vehicle_index() -> dict[str, dict[str, Any]]:
    from models.schema import Vehicle
    result: dict[str, dict[str, Any]] = {}
    for vehicle in Vehicle.query.all():
        plate = _plate_key(getattr(vehicle, "plate", ""))
        if plate:
            result[plate] = {"type": getattr(vehicle, "v_type", ""), "model": getattr(vehicle, "model", ""), "plate": getattr(vehicle, "plate", "")}
    return result


def _fresh_reading(updated_at: Any, max_age_seconds: int = 180) -> bool:
    if not updated_at:
        return False
    try:
        stamp = datetime.fromisoformat(str(updated_at).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - stamp.astimezone(timezone.utc)).total_seconds() <= max_age_seconds
    except (TypeError, ValueError):
        return False


def fetch_live_locations() -> list[dict[str, Any]]:
    """Reuse the provider-verified fleet fetch, including token rotation and speed_kmh."""
    import secrets
    from routes.gps import _fetch_fleet
    return _fetch_fleet(secrets.token_hex(6))


def evaluate_locations(locations: list[dict[str, Any]], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous if isinstance(previous, dict) else {}
    vehicles = _vehicle_index()
    alerts: list[dict[str, Any]] = []
    active: dict[str, Any] = {}
    now = datetime.now(timezone.utc).isoformat()
    for item in locations:
        plate = item.get("plate") or item.get("name")
        key = _plate_key(plate)
        updated = item.get("last_update") or item.get("updated_at")
        if not key or not _fresh_reading(updated):
            continue
        try:
            speed = float(item.get("speed_kmh") if item.get("speed_kmh") is not None else item.get("speed") or 0)
        except (TypeError, ValueError):
            continue
        meta = vehicles.get(key, {})
        category = classify_vehicle(meta.get("type"), meta.get("model"))
        if not category:
            continue
        limit = SPEED_LIMITS[category]
        if speed > limit:
            active[key] = {"plate": plate, "category": category, "speed": speed, "limit": limit, "since": previous.get(key, {}).get("since", now)}
            if key not in previous:
                alerts.append({"id": f"speed-{key}-{int(datetime.now().timestamp())}", "plate": plate, "category": category, "speed": speed, "limit": limit, "lat": item.get("lat") or item.get("latitude"), "lng": item.get("lng") or item.get("longitude"), "created_at": now, "status": "new"})
    return {"alerts": alerts, "active": active, "checked": len(locations), "limits": SPEED_LIMITS}


def run_speed_check() -> dict[str, Any]:
    from helpers import _global_blob_get, _global_blob_set
    evaluated = evaluate_locations(fetch_live_locations(), (_global_blob_get("speed_alerts") or {}).get("active", {}))
    stored = _global_blob_get("speed_alerts") or {}
    history = (evaluated["alerts"] + (stored.get("history", []) if isinstance(stored, dict) else []))[:200]
    _global_blob_set("speed_alerts", {"active": evaluated["active"], "history": history, "last_check": datetime.now(timezone.utc).isoformat()})
    for alert in evaluated["alerts"]:
        try:
            from app import send_push_notification
            send_push_notification("تنبيه تجاوز سرعة", f"المركبة {alert['plate']} تجاوزت حد {alert['limit']} كم/س بسرعة {alert['speed']} كم/س")
        except Exception:
            pass
    return {"new_alerts": evaluated["alerts"], "active": evaluated["active"], "checked": evaluated["checked"], "limits": evaluated["limits"]}


def get_speed_alerts() -> dict[str, Any]:
    from helpers import _global_blob_get
    stored = _global_blob_get("speed_alerts") or {}
    return stored if isinstance(stored, dict) else {}
