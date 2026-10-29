import unittest
from scripts.incident_logic import classify_observation, build_incidents, load_day3_output, Day3OutputError
from pathlib import Path

class IncidentLogicTests(unittest.TestCase):
    def base_row(self):
        return {
            "timestamp": "2026-10-20T09:35:00",
            "host": "app-server-01",
            "cpu_percent": 97.0,
            "memory_percent": 91.0,
            "response_time_ms": 1200.0,
            "http_5xx_count": 25.0,
            "rule_anomaly": 1,
            "ml_anomaly": 1,
            "reference_flag": 1,
            "investigation_reason": "Flagged by both methods",
        }

    def test_critical_pattern(self):
        result = classify_observation(self.base_row())
        self.assertEqual(result["severity"], "CRITICAL")
        self.assertTrue(result["create_issue"])

    def test_high_when_both_detectors_flag_without_critical_pattern(self):
        row = self.base_row()
        row.update(cpu_percent=95.0, response_time_ms=950.0, http_5xx_count=18.0)
        result = classify_observation(row)
        self.assertEqual(result["severity"], "HIGH")

    def test_medium_when_only_one_detector_flags(self):
        row = self.base_row()
        row.update(rule_anomaly=1, ml_anomaly=0, cpu_percent=92.0, response_time_ms=500.0, http_5xx_count=0.0)
        result = classify_observation(row)
        self.assertEqual(result["severity"], "MEDIUM")
        self.assertFalse(result["create_issue"])

    def test_unflagged_row_is_ignored(self):
        row = self.base_row()
        row.update(rule_anomaly=0, ml_anomaly=0)
        self.assertIsNone(classify_observation(row))

    def test_bundled_day3_file_has_three_incidents(self):
        root = Path(__file__).resolve().parent.parent
        rows = load_day3_output(root / "data" / "day3" / "anomaly_comparison.csv")
        incidents = build_incidents(rows)
        self.assertEqual(len(rows), 20)
        self.assertEqual(len(incidents), 3)
        self.assertEqual([i["severity"] for i in incidents], ["HIGH", "CRITICAL", "HIGH"])

    def test_bad_numeric_value_is_rejected(self):
        # Validation is covered against the supplied file in the executable workflow;
        # this unit test verifies that invalid test data cannot be silently converted.
        row = self.base_row()
        row["cpu_percent"] = "unknown"
        with self.assertRaises((ValueError, TypeError)):
            classify_observation(row)

if __name__ == "__main__":
    unittest.main()
