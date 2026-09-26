"""Unit tests for LogLens analyzer module."""

from __future__ import annotations

import unittest
from datetime import datetime

from loglens.analyzer import LogAnalyzer
from loglens.models import LogRecord


class TestLogAnalyzer(unittest.TestCase):
    """Test suite for LogAnalyzer metric calculations."""

    def setUp(self) -> None:
        self.records = [
            LogRecord(
                timestamp=datetime(2026, 9, 26, 8, 10, 0),
                level="INFO",
                service="auth",
                message="User signed in",
                line_number=1,
            ),
            LogRecord(
                timestamp=datetime(2026, 9, 26, 8, 20, 0),
                level="DEBUG",
                service="auth",
                message="Session cached",
                line_number=2,
            ),
            LogRecord(
                timestamp=datetime(2026, 9, 26, 8, 30, 0),
                level="ERROR",
                service="auth",
                message="DB timeout",
                line_number=3,
            ),
            LogRecord(
                timestamp=datetime(2026, 9, 26, 9, 5, 0),
                level="INFO",
                service="api",
                message="GET /health",
                line_number=4,
            ),
            LogRecord(
                timestamp=datetime(2026, 9, 26, 9, 10, 0),
                level="INFO",
                service="api",
                message="POST /checkout",
                line_number=5,
            ),
            LogRecord(
                timestamp=datetime(2026, 9, 26, 9, 15, 0),
                level="CRITICAL",
                service="payment",
                message="Bank gateway unreachable",
                line_number=6,
            ),
            LogRecord(
                timestamp=datetime(2026, 9, 26, 9, 20, 0),
                level="WARNING",
                service="api",
                message="High latency observed",
                line_number=7,
            ),
        ]

    def test_line_counts_and_boundaries(self) -> None:
        analyzer = LogAnalyzer(min_errors=5, multiplier=2.0)
        summary = analyzer.analyze_records(self.records, malformed_lines=2)

        self.assertEqual(summary.valid_lines, 7)
        self.assertEqual(summary.malformed_lines, 2)
        self.assertEqual(summary.total_lines, 9)
        self.assertEqual(summary.start_time, datetime(2026, 9, 26, 8, 10, 0))
        self.assertEqual(summary.end_time, datetime(2026, 9, 26, 9, 20, 0))

    def test_severity_level_counts(self) -> None:
        analyzer = LogAnalyzer()
        summary = analyzer.analyze_records(self.records)

        self.assertEqual(summary.level_counts["INFO"], 3)
        self.assertEqual(summary.level_counts["DEBUG"], 1)
        self.assertEqual(summary.level_counts["WARNING"], 1)
        self.assertEqual(summary.level_counts["ERROR"], 1)
        self.assertEqual(summary.level_counts["CRITICAL"], 1)

    def test_service_counts_and_service_errors(self) -> None:
        analyzer = LogAnalyzer()
        summary = analyzer.analyze_records(self.records)

        self.assertEqual(summary.service_counts["auth"], 3)
        self.assertEqual(summary.service_counts["api"], 3)
        self.assertEqual(summary.service_counts["payment"], 1)

        self.assertEqual(summary.service_error_counts["auth"], 1)
        self.assertEqual(summary.service_error_counts["payment"], 1)
        self.assertNotIn("api", summary.service_error_counts)

    def test_busiest_hour_identification(self) -> None:
        analyzer = LogAnalyzer()
        summary = analyzer.analyze_records(self.records)

        # Hour 08:00 has 3 records; hour 09:00 has 4 records
        self.assertEqual(summary.busiest_hour, "2026-09-26 09:00")
        self.assertEqual(summary.busiest_hour_count, 4)

    def test_top_error_services_ordering(self) -> None:
        analyzer = LogAnalyzer()
        summary = analyzer.analyze_records(self.records)

        # Both auth and payment have 1 error. Alphabetical order ties: auth, payment
        self.assertEqual(summary.top_error_services, [("auth", 1), ("payment", 1)])

    def test_to_dict_serialization(self) -> None:
        analyzer = LogAnalyzer()
        summary = analyzer.analyze_records(self.records)
        data = summary.to_dict()

        self.assertIn("meta", data)
        self.assertIn("line_counts", data)
        self.assertIn("severity_counts", data)
        self.assertIn("service_counts", data)
        self.assertIn("hourly_statistics", data)
        self.assertEqual(data["line_counts"]["valid_lines"], 7)


if __name__ == "__main__":
    unittest.main()
