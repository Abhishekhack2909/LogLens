"""Unit tests for LogLens parser module."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from loglens.file_utils import InputFileNotFoundError, UnreadableFileError
from loglens.parser import LogParser, LogStreamReader, MalformedLineError


class TestLogParser(unittest.TestCase):
    """Test suite for LogParser line parsing and validation."""

    def test_valid_line_parsing(self) -> None:
        raw = "2026-09-26 10:15:30 ERROR auth Login failed for user"
        record = LogParser.parse_line(raw, line_number=1)
        self.assertEqual(record.timestamp, datetime(2026, 9, 26, 10, 15, 30))
        self.assertEqual(record.level, "ERROR")
        self.assertEqual(record.service, "auth")
        self.assertEqual(record.message, "Login failed for user")
        self.assertEqual(record.line_number, 1)
        self.assertEqual(record.hour_key, "2026-09-26 10:00")
        self.assertTrue(record.is_error)

    def test_message_with_multiple_spaces_and_special_chars(self) -> None:
        raw = "2026-09-26 11:20:05 INFO api-gateway Request GET /v1/users?id=42&sort=asc (200 OK) took 15ms"
        record = LogParser.parse_line(raw, line_number=5)
        self.assertEqual(record.level, "INFO")
        self.assertEqual(record.service, "api-gateway")
        self.assertEqual(
            record.message,
            "Request GET /v1/users?id=42&sort=asc (200 OK) took 15ms",
        )
        self.assertFalse(record.is_error)

    def test_all_standard_severity_levels(self) -> None:
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for lvl in levels:
            raw = f"2026-09-26 12:00:00 {lvl} worker Processing task #100"
            record = LogParser.parse_line(raw)
            self.assertEqual(record.level, lvl)

    def test_invalid_log_level_raises_malformed(self) -> None:
        invalid_levels = ["TRACE", "FATAL", "info", "Error", "UNKNOWN", "ALERT"]
        for bad_lvl in invalid_levels:
            raw = f"2026-09-26 12:00:00 {bad_lvl} worker Service heartbeat"
            with self.assertRaises(MalformedLineError):
                LogParser.parse_line(raw)

    def test_invalid_calendar_timestamp(self) -> None:
        # Invalid month 13
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("2026-13-26 12:00:00 INFO api Ping")

        # Invalid day 32
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("2026-09-32 12:00:00 INFO api Ping")

        # Invalid hour 25
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("2026-09-26 25:00:00 INFO api Ping")

        # Invalid minute 60
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("2026-09-26 12:60:00 INFO api Ping")

    def test_empty_or_blank_line(self) -> None:
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("")
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("   \n")

    def test_truncated_lines(self) -> None:
        # Missing message and service
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("2026-09-26 12:00:00 INFO")

        # Missing message
        with self.assertRaises(MalformedLineError):
            LogParser.parse_line("2026-09-26 12:00:00 INFO auth")

    def test_try_parse_line_helper(self) -> None:
        rec, err = LogParser.try_parse_line("2026-09-26 12:00:00 INFO auth Login ok")
        self.assertIsNotNone(rec)
        self.assertIsNone(err)

        bad_rec, bad_err = LogParser.try_parse_line("CORRUPTED LINE")
        self.assertIsNone(bad_rec)
        self.assertIsNotNone(bad_err)


class TestLogStreamReader(unittest.TestCase):
    """Test suite for LogStreamReader streaming file ingestion."""

    def test_streaming_ingestion_and_counts(self) -> None:
        content = (
            "2026-09-26 10:00:01 INFO auth User login\n"
            "NOT A LOG LINE\n"
            "2026-09-26 10:00:02 ERROR auth Invalid password\n"
            "2026-09-26 10:00:03 TRACE worker Debugging trace\n"
            "2026-09-26 10:00:04 CRITICAL payment Gateway down\n"
        )
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            tf.write(content)
            temp_path = tf.name

        try:
            reader = LogStreamReader(temp_path)
            records = list(reader.stream_records())

            self.assertEqual(len(records), 3)
            self.assertEqual(reader.total_lines, 5)
            self.assertEqual(reader.valid_lines, 3)
            self.assertEqual(reader.malformed_lines, 2)
            self.assertEqual(len(reader.malformed_samples), 2)
            self.assertEqual(reader.malformed_samples[0]["line_number"], 2)
            self.assertEqual(reader.malformed_samples[1]["line_number"], 4)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_empty_file_ingestion(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as tf:
            temp_path = tf.name

        try:
            reader = LogStreamReader(temp_path)
            records = list(reader.stream_records())
            self.assertEqual(len(records), 0)
            self.assertEqual(reader.total_lines, 0)
            self.assertEqual(reader.valid_lines, 0)
            self.assertEqual(reader.malformed_lines, 0)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_missing_file_raises_error(self) -> None:
        with self.assertRaises(InputFileNotFoundError):
            LogStreamReader("non_existent_file_path_12345.log")


if __name__ == "__main__":
    unittest.main()
