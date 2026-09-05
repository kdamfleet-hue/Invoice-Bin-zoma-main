"""Unified notification center backed by existing bounded GPS alert blobs."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from helpers import _global_blob_get, _global_blob_set

MAX_READ_IDS = 1500


def _read_state() -> set[str]:
    value = _global_blob_get("notification_center") or {}
    ids = value.get("read_ids", []) if isinstance(value, dict) else []
    return {str(x) for x in ids[-MAX_READ_IDS:]}


def _all_alerts() -> list[dict[str, Any]]:
    speed = _global_blob_get("speed_alerts") or {}
    geo = _global_blob_get("gps_geofence_state") or {}
    result = []
    for item in speed.get("history", []) if isinstance(speed, dict) else []:
        stamp = item.get("created_at") or item.get("updated_at") or item.get("timestamp") or ""
        aid = str(item.get("id") or "speed-" + stamp + str(item.get("plate", "")))
        result.append({"id": aid, "type": "speed", "severity": "high", "title": "تجاوز سرعة", "message": f"المركبة {item.get('plate') or item.get('vehicle') or ''} تجاوزت {item.get('limit', '')} كم/س بسرعة {item.get('speed', '')} كم/س", "created_at": stamp})
    for item in geo.get("history", []) if isinstance(geo, dict) else []:
        event = "دخول" if item.get("event") == "entry" else "خروج"
        aid = str(item.get("id") or "geo-" + str(item.get("created_at", "")) + str(item.get("vehicle_id", "")))
        result.append({"id": aid, "type": "geofence", "severity": "medium", "title": f"{event} منطقة جغرافية", "message": f"{item.get('vehicle') or item.get('plate') or item.get('vehicle_id') or ''} — {event} {item.get('geofence') or ''}", "created_at": item.get("created_at") or ""})
    result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return result[:500]


def get_notifications(limit: int = 40):
    read = _read_state()
    alerts = _all_alerts()
    rows = [{**a, "read": a["id"] in read} for a in alerts]
    return {"rows": rows[:max(1, min(int(limit or 40), 100))], "unread_count": sum(1 for a in rows if not a["read"])}


def mark_read(ids: list[str] | None = None, all_read: bool = False):
    existing = _read_state()
    alerts = _all_alerts()
    if all_read:
        existing.update(str(a["id"]) for a in alerts)
    else:
        existing.update(str(x) for x in (ids or []) if x)
    _global_blob_set("notification_center", {"read_ids": list(existing)[-MAX_READ_IDS:], "updated_at": datetime.now(timezone.utc).isoformat()})
    return get_notifications()
