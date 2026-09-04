import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import services.speed_alerts as speed_alerts


class SpeedAlertTests(unittest.TestCase):
    def test_category_limits_and_deduplication(self):
        now = datetime.now(timezone.utc).isoformat()
        vehicle_index = {
            "1001": {"type": "شاحنة", "model": "", "plate": "1001"},
            "1002": {"type": "سيارة خفيفة", "model": "", "plate": "1002"},
            "1003": {"type": "حافلة", "model": "", "plate": "1003"},
        }
        locations = [
            {"plate": "1001", "speed": 81, "updated_at": now},
            {"plate": "1002", "speed": 121, "updated_at": now},
            {"plate": "1003", "speed": 91, "updated_at": now},
        ]
        with patch.object(speed_alerts, "_vehicle_index", return_value=vehicle_index):
            first = speed_alerts.evaluate_locations(locations)
            self.assertEqual({a["limit"] for a in first["alerts"]}, {80, 90, 120})
            second = speed_alerts.evaluate_locations(locations, first["active"])
            self.assertEqual(second["alerts"], [])

    def test_stale_reading_is_ignored(self):
        with patch.object(speed_alerts, "_vehicle_index", return_value={
            "1001": {"type": "شاحنة", "model": "", "plate": "1001"},
        }):
            result = speed_alerts.evaluate_locations([{
                "plate": "1001", "speed": 140, "updated_at": "2020-01-01T00:00:00+00:00"
            }])
            self.assertEqual(result["alerts"], [])


if __name__ == "__main__":
    unittest.main()
