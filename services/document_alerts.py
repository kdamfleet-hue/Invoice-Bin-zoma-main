"""Read-only document alert preparation.

Sending is intentionally disabled by default. Providers must be configured through
hosting environment variables and an explicit enable flag before dispatching.
"""
from __future__ import annotations

import os
from datetime import date
from typing import Iterable, Mapping


ALERT_WINDOW_DAYS = int(os.getenv("DOCUMENT_ALERT_WINDOW_DAYS", "30"))
ALERTS_ENABLED = os.getenv("DOCUMENT_ALERTS_ENABLED", "0").lower() in {"1", "true", "yes"}
EMAIL_ENABLED = os.getenv("DOCUMENT_ALERT_EMAIL_ENABLED", "0").lower() in {"1", "true", "yes"}
WHATSAPP_ENABLED = os.getenv("DOCUMENT_ALERT_WHATSAPP_ENABLED", "0").lower() in {"1", "true", "yes"}


def normalize_alerts(rows: Iterable[Mapping]) -> list[dict]:
    """Return a stable, non-secret alert payload for rendering or later dispatch."""
    result = []
    for row in rows:
        result.append({
            "name": str(row.get("name") or "غير محدد"),
            "plate": str(row.get("plate") or "غير مرتبط"),
            "document": str(row.get("doc") or row.get("document") or "وثيقة"),
            "expiry_date": str(row.get("date") or row.get("expiry_date") or "غير محدد"),
            "days": row.get("days"),
            "severity": "expired" if row.get("days") is not None and row.get("days") < 0 else "due_soon",
        })
    return result


def build_message(alerts: Iterable[Mapping], language: str = "ar") -> str:
    """Build a provider-neutral message; does not send it."""
    normalized = normalize_alerts(alerts)
    if language == "en":
        lines = ["BIN ZOMAH document expiry alert", "Expired or due within 30 days:"]
        lines.extend(f"- {a['name']} | {a['plate']} | {a['document']} | {a['expiry_date']}" for a in normalized)
    else:
        lines = ["تنبيه صلاحية وثائق BIN ZOMAH", "الوثائق المنتهية أو التي ستنتهي خلال 30 يومًا:"]
        lines.extend(f"- {a['name']} | {a['plate']} | {a['document']} | {a['expiry_date']}" for a in normalized)
    return "\n".join(lines)


def configuration_status() -> dict:
    """Expose only safe booleans; never return recipients or secret values."""
    return {
        "alerts_enabled": ALERTS_ENABLED,
        "email_enabled": EMAIL_ENABLED,
        "whatsapp_enabled": WHATSAPP_ENABLED,
        "window_days": ALERT_WINDOW_DAYS,
        "send_capable": ALERTS_ENABLED and (EMAIL_ENABLED or WHATSAPP_ENABLED),
        "mode": "disabled" if not ALERTS_ENABLED else "configured",
    }
