import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.reconciliation import nonmatch_rate, reconcile_records, validate_publish_gate


def test_reconciliation_matches_by_normalized_plate_and_flags_letter_changes():
    result = reconcile_records(
        [{"vehicle_id": 1, "plate": "ر ل ر 5059"}, {"vehicle_id": 2, "plate": "ب ح ل 4434"}],
        [{"device_id": "gps-1", "plate": "ر ن ر 5059"}, {"device_id": "gps-2", "plate": "ب ح ل 4434"}],
    )
    assert result["matched_count"] == 1
    assert result["manual_review_count"] == 1
    assert result["gps_only_count"] == 0
    assert nonmatch_rate(result) == 0.0


def test_reconciliation_counts_gps_only_fleet_only_and_duplicates():
    result = reconcile_records(
        [{"vehicle_id": 1, "plate": "أ ب ج 1234"}, {"vehicle_id": 2, "plate": "أ ب ج 1234"}],
        [{"device_id": "gps-1", "plate": "س د ر 9999"}],
    )
    assert result["gps_only_count"] == 1
    assert result["fleet_only_count"] == 2
    assert result["duplicate_count"] == 1
    assert nonmatch_rate(result) == 150.0


def test_publish_gate_rejects_old_snapshot_and_high_nonmatch_rate():
    result = {"gps_count": 100, "fleet_count": 100, "gps_only_count": 6, "fleet_only_count": 0}
    generated = datetime.now(timezone.utc) - timedelta(minutes=20)
    gate = validate_publish_gate(result, generated, now=datetime.now(timezone.utc), max_age_seconds=900, max_nonmatch_rate_pct=5)
    assert gate["publish"] is False
    assert "snapshot_too_old" in gate["reasons"]
    assert "nonmatch_rate_above_threshold" in gate["reasons"]


def test_publish_gate_accepts_fresh_matching_snapshot():
    result = {"gps_count": 10, "fleet_count": 10, "gps_only_count": 0, "fleet_only_count": 0}
    generated = datetime.now(timezone.utc)
    gate = validate_publish_gate(result, generated, now=datetime.now(timezone.utc))
    assert gate["publish"] is True
    assert gate["reasons"] == []
