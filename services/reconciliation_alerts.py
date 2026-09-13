"""Notifications for reconciliation breaches.

Email uses the application's configured Flask-Mail transport. Slack uses an
incoming webhook stored only in the environment. Notification failures never
break the reconciliation request.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger("InvoiceApp")
_ALERT_STATE_KEY = "reconciliation_alert_state"


def _state() -> dict[str, Any]:
    try:
        from helpers import _global_blob_get
        value = _global_blob_get(_ALERT_STATE_KEY)
        return value if isinstance(value, dict) else {}
    except Exception:
        logger.exception("Could not read reconciliation alert state")
        return {}


def _save_state(value: dict[str, Any]) -> None:
    try:
        from helpers import _global_blob_set
        _global_blob_set(_ALERT_STATE_KEY, value)
    except Exception:
        logger.exception("Could not persist reconciliation alert state")


def _message(result: dict[str, Any], gate: dict[str, Any]) -> tuple[str, str]:
    rate = float(gate.get("nonmatch_rate_pct", 0))
    threshold = float(gate.get("max_nonmatch_rate_pct", 5))
    subject = f"تنبيه مطابقة GPS — نسبة عدم المطابقة {rate:.2f}% (الحد {threshold:.2f}%)"
    text = (
        "تنبيه آلي من نظام إدارة الأسطول\n\n"
        f"نسبة عدم المطابقة: {rate:.2f}%\n"
        f"الحد المسموح: {threshold:.2f}%\n"
        f"سجلات GPS: {result.get('gps_count', 0)}\n"
        f"سجلات الأسطول: {result.get('fleet_count', 0)}\n"
        f"المطابقات: {result.get('matched_count', 0)}\n"
        f"GPS فقط: {result.get('gps_only_count', 0)}\n"
        f"الأسطول فقط: {result.get('fleet_only_count', 0)}\n"
        f"مراجعة يدوية: {result.get('manual_review_count', 0)}\n"
        f"التكرارات: {result.get('duplicate_count', 0)}\n"
        "\nتم منع نشر Snapshot حتى معالجة الفارق."
    )
    return subject, text


def _send_email(subject: str, text: str) -> dict[str, Any]:
    recipients = [x.strip() for x in os.environ.get("RECONCILIATION_ALERT_RECIPIENTS", os.environ.get("ALERT_RECIPIENTS", "")).split(",") if x.strip()]
    if not recipients:
        return {"sent": False, "reason": "no_recipients"}
    try:
        from flask_mail import Message
        from app import app, _mail_send_safe
        if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
            return {"sent": False, "reason": "mail_not_configured"}
        msg = Message(subject=subject, recipients=recipients, body=text, sender=app.config.get("MAIL_DEFAULT_SENDER") or app.config.get("MAIL_USERNAME"))
        _mail_send_safe(msg)
        return {"sent": True, "recipients": recipients}
    except Exception:
        logger.exception("reconciliation email notification failed")
        return {"sent": False, "reason": "send_error"}


def _send_slack(subject: str, text: str) -> dict[str, Any]:
    webhook = os.environ.get("RECONCILIATION_SLACK_WEBHOOK_URL", "").strip()
    if not webhook:
        return {"sent": False, "reason": "webhook_not_configured"}
    try:
        response = requests.post(webhook, json={"text": f"*{subject}*\n{text}"}, timeout=10)
        if response.status_code >= 300:
            logger.warning("reconciliation Slack notification failed status=%s", response.status_code)
            return {"sent": False, "reason": "webhook_error", "status": response.status_code}
        return {"sent": True}
    except Exception:
        logger.exception("reconciliation Slack notification failed")
        return {"sent": False, "reason": "send_error"}


def notify_reconciliation_breach(result: dict[str, Any], gate: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    """Send configured notifications once per breach fingerprint and cooldown."""
    if gate.get("publish", True):
        return {"sent": False, "reason": "within_threshold"}
    subject, text = _message(result, gate)
    fingerprint = json.dumps({
        "rate": gate.get("nonmatch_rate_pct"),
        "gps": result.get("gps_count"),
        "fleet": result.get("fleet_count"),
        "gps_only": result.get("gps_only_count"),
        "fleet_only": result.get("fleet_only_count"),
    }, sort_keys=True, ensure_ascii=False)
    cooldown = max(60, int(os.environ.get("RECONCILIATION_ALERT_COOLDOWN_SECONDS", "3600")))
    state = _state()
    now = time.time()
    if not force and state.get("fingerprint") == fingerprint and now - float(state.get("sent_at", 0)) < cooldown:
        return {"sent": False, "reason": "cooldown", "fingerprint": fingerprint}
    email = _send_email(subject, text)
    slack = _send_slack(subject, text)
    sent = bool(email.get("sent") or slack.get("sent"))
    if sent:
        _save_state({"fingerprint": fingerprint, "sent_at": now, "channels": {"email": email.get("sent", False), "slack": slack.get("sent", False)}})
    return {"sent": sent, "fingerprint": fingerprint, "email": email, "slack": slack}
