import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import reconciliation_alerts


def breach_result():
    return {"gps_count": 100, "fleet_count": 100, "matched_count": 90, "gps_only_count": 6, "fleet_only_count": 4, "manual_review_count": 2, "duplicate_count": 1}


def breach_gate():
    return {"publish": False, "nonmatch_rate_pct": 10.0, "max_nonmatch_rate_pct": 5.0}


def test_breach_sends_configured_channels_and_persists_dedup(monkeypatch):
    calls = []
    monkeypatch.setattr(reconciliation_alerts, "_state", lambda: {})
    monkeypatch.setattr(reconciliation_alerts, "_send_email", lambda subject, text: calls.append("email") or {"sent": True})
    monkeypatch.setattr(reconciliation_alerts, "_send_slack", lambda subject, text: calls.append("slack") or {"sent": True})
    saved = []
    monkeypatch.setattr(reconciliation_alerts, "_save_state", lambda value: saved.append(value))

    result = reconciliation_alerts.notify_reconciliation_breach(breach_result(), breach_gate())

    assert result["sent"] is True
    assert calls == ["email", "slack"]
    assert saved and saved[0]["fingerprint"]


def test_breach_is_suppressed_during_cooldown(monkeypatch):
    monkeypatch.setattr(reconciliation_alerts, "_state", lambda: {"fingerprint": reconciliation_alerts.json.dumps({"fleet": 100, "gps": 100, "fleet_only": 4, "gps_only": 6, "rate": 10.0}, sort_keys=True, ensure_ascii=False), "sent_at": reconciliation_alerts.time.time()})
    monkeypatch.setattr(reconciliation_alerts, "_send_email", lambda *_: (_ for _ in ()).throw(AssertionError("email should not send")))
    monkeypatch.setattr(reconciliation_alerts, "_send_slack", lambda *_: (_ for _ in ()).throw(AssertionError("slack should not send")))

    result = reconciliation_alerts.notify_reconciliation_breach(breach_result(), breach_gate())

    assert result["reason"] == "cooldown"


def test_within_threshold_does_not_notify(monkeypatch):
    monkeypatch.setattr(reconciliation_alerts, "_send_email", lambda *_: (_ for _ in ()).throw(AssertionError("email should not send")))
    monkeypatch.setattr(reconciliation_alerts, "_send_slack", lambda *_: (_ for _ in ()).throw(AssertionError("slack should not send")))

    result = reconciliation_alerts.notify_reconciliation_breach(breach_result(), {"publish": True})

    assert result["reason"] == "within_threshold"
