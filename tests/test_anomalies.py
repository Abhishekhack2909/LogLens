"""Unit tests for LogLens anomaly detection module."""

from __future__ import annotations

import unittest

from loglens.anomalies import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):
    """Test suite for deterministic hourly error spike detection."""

    def test_parameter_validation(self) -> None:
        with self.assertRaises(ValueError):
            AnomalyDetector(min_errors=0)
        with self.assertRaises(ValueError):
            AnomalyDetector(min_errors=-5)
        with self.assertRaises(ValueError):
            AnomalyDetector(multiplier=0.0)
        with self.assertRaises(ValueError):
            AnomalyDetector(multiplier=-1.5)

    def test_empty_dataset(self) -> None:
        detector = AnomalyDetector(min_errors=5, multiplier=2.0)
        baseline, anomalies = detector.detect_anomalies({})
        self.assertEqual(baseline, 0.0)
        self.assertEqual(len(anomalies), 0)

    def test_normal_data_no_anomalies(self) -> None:
        # 5 hours with low steady error counts (1, 2, 1, 2, 1)
        hourly_errors = {
            "2026-09-26 08:00": 1,
            "2026-09-26 09:00": 2,
            "2026-09-26 10:00": 1,
            "2026-09-26 11:00": 2,
            "2026-09-26 12:00": 1,
        }
        # Baseline = 7 / 5 = 1.4
        # Threshold = max(5, 2.0 * 1.4) = 5.0
        # No hour >= 5
        detector = AnomalyDetector(min_errors=5, multiplier=2.0)
        baseline, anomalies = detector.detect_anomalies(hourly_errors)

        self.assertAlmostEqual(baseline, 1.4)
        self.assertEqual(len(anomalies), 0)

    def test_anomalous_spike_detected(self) -> None:
        hourly_errors = {
            "2026-09-26 08:00": 1,
            "2026-09-26 09:00": 2,
            "2026-09-26 10:00": 1,
            "2026-09-26 11:00": 20,  # Clear spike!
            "2026-09-26 12:00": 1,
        }
        # Baseline = 25 / 5 = 5.0
        # Threshold = max(5, 2.0 * 5.0) = 10.0
        # Hour 11:00 has 20 errors >= 10.0
        detector = AnomalyDetector(min_errors=5, multiplier=2.0)
        baseline, anomalies = detector.detect_anomalies(hourly_errors)

        self.assertAlmostEqual(baseline, 5.0)
        self.assertEqual(len(anomalies), 1)
        anom = anomalies[0]
        self.assertEqual(anom.hour_key, "2026-09-26 11:00")
        self.assertEqual(anom.error_count, 20)
        self.assertEqual(anom.threshold, 10.0)
        self.assertIn("Hourly spike", anom.reason)

    def test_zero_baseline_with_no_errors(self) -> None:
        hourly_errors = {
            "2026-09-26 08:00": 0,
            "2026-09-26 09:00": 0,
            "2026-09-26 10:00": 0,
        }
        detector = AnomalyDetector(min_errors=5, multiplier=2.0)
        baseline, anomalies = detector.detect_anomalies(hourly_errors)

        self.assertEqual(baseline, 0.0)
        self.assertEqual(len(anomalies), 0)

    def test_zero_baseline_with_sudden_burst(self) -> None:
        # Previous hours had 0 errors, but a sudden burst occurs
        hourly_errors = {
            "2026-09-26 08:00": 0,
            "2026-09-26 09:00": 0,
            "2026-09-26 10:00": 6,  # Meets min_errors
        }
        detector = AnomalyDetector(min_errors=5, multiplier=2.0)
        baseline, anomalies = detector.detect_anomalies(hourly_errors)

        # Baseline = 6 / 3 = 2.0
        # Multiplier * 2.0 = 4.0; max(5, 4.0) = 5.0
        # 6 >= 5.0 -> anomaly!
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].hour_key, "2026-09-26 10:00")
        self.assertEqual(anomalies[0].error_count, 6)

    def test_sparse_baseline_single_hour(self) -> None:
        # Only 1 hour in log
        detector = AnomalyDetector(min_errors=5, multiplier=2.0)

        # Single hour with count < min_errors: not flagged
        _, anoms_low = detector.detect_anomalies({"2026-09-26 10:00": 3})
        self.assertEqual(len(anoms_low), 0)

        # Single hour with count >= min_errors: flagged under sparse baseline rule
        _, anoms_high = detector.detect_anomalies({"2026-09-26 10:00": 7})
        self.assertEqual(len(anoms_high), 1)
        self.assertIn("Sparse baseline", anoms_high[0].reason)
        self.assertEqual(anoms_high[0].error_count, 7)

    def test_configurable_threshold_tuning(self) -> None:
        hourly_errors = {
            "2026-09-26 08:00": 2,
            "2026-09-26 09:00": 2,
            "2026-09-26 10:00": 8,  # Spike
            "2026-09-26 11:00": 2,
        }
        # Baseline = 14 / 4 = 3.5

        # With min_errors=5, multiplier=2.0: threshold = max(5, 7.0) = 7.0 -> 8 is flagged
        det1 = AnomalyDetector(min_errors=5, multiplier=2.0)
        _, anoms1 = det1.detect_anomalies(hourly_errors)
        self.assertEqual(len(anoms1), 1)

        # With min_errors=10: threshold = max(10, 7.0) = 10.0 -> 8 is NOT flagged
        det2 = AnomalyDetector(min_errors=10, multiplier=2.0)
        _, anoms2 = det2.detect_anomalies(hourly_errors)
        self.assertEqual(len(anoms2), 0)


if __name__ == "__main__":
    unittest.main()
