"""Safe inbound-email import helpers.

This module intentionally does not connect to an inbox and never sends mail.
A trusted adapter may pass already-read message dictionaries to import_messages.
Automatic scheduling is deliberately out of scope.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from models.schema import db, InboundEmailTask

READ_ONLY_IMPORT = True


def _text(value: Any, limit: int) -> str:
    return str(value or "").strip()[:limit]


def _parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    raw = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def import_messages(messages: Iterable[dict[str, Any]], branch_id: int | None = None) -> dict[str, int]:
    """Create inbound tasks from trusted, already-read messages.

    Required field: ``message_id``. Duplicate message IDs are ignored. The
    function only writes local task rows; it performs no outbound operation.
    """
    created = skipped = rejected = 0
    for item in messages:
        if not isinstance(item, dict) or not _text(item.get("message_id"), 255):
            rejected += 1
            continue
        message_id = _text(item["message_id"], 255)
        if InboundEmailTask.query.filter_by(message_id=message_id).first():
            skipped += 1
            continue
        received_at = _parse_date(item.get("received_at")) or datetime.now(timezone.utc)
        task = InboundEmailTask(
            branch_id=branch_id,
            message_id=message_id,
            thread_id=_text(item.get("thread_id"), 255) or None,
            sender=_text(item.get("sender"), 255) or None,
            recipients=_text(item.get("recipients"), 1000) or None,
            subject=_text(item.get("subject"), 500) or "رسالة واردة بدون موضوع",
            body_preview=_text(item.get("body_preview"), 4000) or None,
            received_at=received_at,
            status="وارد",
            source="inbound_read_only",
        )
        db.session.add(task)
        created += 1
    if created:
        db.session.commit()
    return {"created": created, "skipped": skipped, "rejected": rejected}
