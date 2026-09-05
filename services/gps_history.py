"""Persistent GPS snapshots and geofence evaluation.

The provider supplies current state, not a guaranteed historical feed. This service builds a
bounded local history from successful polls and evaluates configured circular geofences.
"""
from __future__ import annotations

import math
import secrets
import time
from datetime import datetime, timezone
from typing import Any

from helpers import _global_blob_get, _global_blob_set

MAX_VEHICLES = 250
MAX_POINTS_PER_VEHICLE = 500
MAX_GEOFENCES = 200
MAX_ALERT_HISTORY = 500


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coords(item: dict[str, Any]):
    try:
        lat = float(item.get("lat") if item.get("lat") is not None else item.get("latitude"))
        lng = float(item.get("lng") if item.get("lng") is not None else item.get("longitude"))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return None
        return lat, lng
    except (TypeError, ValueError):
        return None


def _vehicle_key(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("device_id") or item.get("plate") or item.get("name") or "")


def record_snapshot(vehicles: list[dict[str, Any]], at: str | None = None) -> int:
    """Append bounded points, deduplicating unchanged provider readings."""
    stored = _global_blob_get("gps_history") or {"vehicles": {}, "updated_at": None}
    by_vehicle = stored.get("vehicles") if isinstance(stored, dict) else {}
    if not isinstance(by_vehicle, dict):
        by_vehicle = {}
    stamp = at or _now_iso()
    count = 0
    for item in vehicles or []:
        if not isinstance(item, dict):
            continue
        key = _vehicle_key(item)
        coords = _coords(item)
        if not key or not coords:
            continue
        points = by_vehicle.setdefault(key, [])
        if not isinstance(points, list):
            points = []
        last = points[-1] if points else None
        point = {
            "vehicle_id": key,
            "name": item.get("name") or "مركبة",
            "plate": item.get("plate") or "",
            "driver": item.get("driver") or "",
            "lat": coords[0], "lng": coords[1],
            "speed_kmh": item.get("speed_kmh"),
            "status": item.get("status") or "offline",
            "heading": item.get("heading"),
            "odometer_km": item.get("odometer_km"),
            "recorded_at": stamp,
        }
        if not last or last.get("lat") != point["lat"] or last.get("lng") != point["lng"] or last.get("status") != point["status"]:
            points.append(point)
            by_vehicle[key] = points[-MAX_POINTS_PER_VEHICLE:]
            count += 1
    # Keep the blob bounded if devices disappear from the provider for a long period.
    if len(by_vehicle) > MAX_VEHICLES:
        keys = list(by_vehicle)[-MAX_VEHICLES:]
        by_vehicle = {k: by_vehicle[k] for k in keys}
    if count:
        _global_blob_set("gps_history", {"vehicles": by_vehicle, "updated_at": stamp})
    return count


def get_history(vehicle_id: str | None = None, since_epoch: float | None = None, limit: int = 500):
    stored = _global_blob_get("gps_history") or {}
    by_vehicle = stored.get("vehicles", {}) if isinstance(stored, dict) else {}
    rows = []
    for key, points in by_vehicle.items() if isinstance(by_vehicle, dict) else []:
        if vehicle_id and str(key) != str(vehicle_id):
            continue
        for point in points if isinstance(points, list) else []:
            if since_epoch is not None:
                try:
                    stamp = datetime.fromisoformat(str(point.get("recorded_at")).replace("Z", "+00:00"))
                    if stamp.timestamp() < since_epoch:
                        continue
                except (TypeError, ValueError):
                    continue
            rows.append(point)
    rows.sort(key=lambda x: x.get("recorded_at", ""), reverse=True)
    return rows[:max(1, min(int(limit or 500), 2000))]


def list_geofences():
    stored = _global_blob_get("gps_geofences") or []
    return stored if isinstance(stored, list) else []


def save_geofence(payload: dict[str, Any]):
    name = " ".join(str(payload.get("name") or "").split()).strip()
    try:
        lat, lng = float(payload.get("lat")), float(payload.get("lng"))
        radius = float(payload.get("radius_m", 250))
    except (TypeError, ValueError):
        raise ValueError("الإحداثيات ونصف القطر يجب أن تكون أرقامًا صحيحة")
    if not name or len(name) > 100:
        raise ValueError("اسم المنطقة مطلوب وبحد أقصى 100 حرف")
    if not (-90 <= lat <= 90 and -180 <= lng <= 180) or not (25 <= radius <= 100000):
        raise ValueError("الإحداثيات أو نصف القطر خارج النطاق المسموح")
    rows = list_geofences()
    row = {"id": secrets.token_urlsafe(9), "name": name, "lat": lat, "lng": lng, "radius_m": radius, "active": bool(payload.get("active", True)), "created_at": _now_iso()}
    rows.append(row)
    _global_blob_set("gps_geofences", rows[-MAX_GEOFENCES:])
    return row


def delete_geofence(geofence_id: str) -> bool:
    rows = list_geofences()
    kept = [r for r in rows if str(r.get("id")) != str(geofence_id)]
    changed = len(kept) != len(rows)
    if changed:
        _global_blob_set("gps_geofences", kept)
    return changed


def _distance_m(lat1, lng1, lat2, lng2):
    radius = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0, 1 - a)))


def evaluate_geofences(vehicles: list[dict[str, Any]]):
    geofences = [g for g in list_geofences() if g.get("active", True)]
    state = _global_blob_get("gps_geofence_state") or {"inside": {}, "history": []}
    inside = state.get("inside", {}) if isinstance(state, dict) else {}
    history = state.get("history", []) if isinstance(state, dict) else []
    events = []
    for vehicle in vehicles or []:
        coords = _coords(vehicle)
        key = _vehicle_key(vehicle)
        if not coords or not key:
            continue
        for fence in geofences:
            try:
                distance = _distance_m(coords[0], coords[1], float(fence["lat"]), float(fence["lng"]))
            except (KeyError, TypeError, ValueError):
                continue
            marker = f"{key}:{fence.get('id')}"
            now_inside = distance <= float(fence.get("radius_m", 250))
            was_inside = bool(inside.get(marker, False))
            if now_inside != was_inside:
                event = {"id": secrets.token_urlsafe(8), "vehicle_id": key, "vehicle": vehicle.get("name") or key, "plate": vehicle.get("plate") or "", "geofence_id": fence.get("id"), "geofence": fence.get("name"), "event": "entry" if now_inside else "exit", "distance_m": round(distance, 1), "created_at": _now_iso()}
                events.append(event)
                history.append(event)
            inside[marker] = now_inside
    _global_blob_set("gps_geofence_state", {"inside": inside, "history": history[-MAX_ALERT_HISTORY:], "updated_at": _now_iso()})
    return {"events": events, "history": history[-MAX_ALERT_HISTORY:], "active": inside}
