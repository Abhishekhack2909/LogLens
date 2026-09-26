"""Unit and integration tests for LogLens CLI."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from loglens.cli import main


class TestCLI(unittest.TestCase):
    """Test suite for LogLens command-line interface execution."""

    def setUp(self) -> None:
        self.sample_lines = (
            "2026-09-26 10:00:00 INFO auth User signed in\n"
            "2026-09-26 10:05:00 DEBUG api Processing payload\n"
            "2026-09-26 10:10:00 ERROR payment Gateway timeout\n"
            "CORRUPTED LINE TO TEST MALFORMED\n"
            "2026-09-26 11:00:00 CRITICAL payment DB down\n"
        )
        self.temp_log = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.temp_log.write(self.sample_lines)
        self.temp_log.close()
        self.log_path = self.temp_log.name

    def tearDown(self) -> None:
        Path(self.log_path).unlink(missing_ok=True)

    def test_cli_help_flag(self) -> None:
        stdout_buf = io.StringIO()
        with redirect_stdout(stdout_buf):
            with self.assertRaises(SystemExit) as cm:
                main(["--help"])
            self.assertEqual(cm.exception.code, 0)
        self.assertIn("LogLens", stdout_buf.getvalue())

    def test_cli_analyze_help_flag(self) -> None:
        stdout_buf = io.StringIO()
        with redirect_stdout(stdout_buf):
            with self.assertRaises(SystemExit) as cm:
                main(["analyze", "--help"])
            self.assertEqual(cm.exception.code, 0)
        self.assertIn("--min-errors", stdout_buf.getvalue())

    def test_cli_successful_text_execution(self) -> None:
        stdout_buf = io.StringIO()
        with redirect_stdout(stdout_buf):
            exit_code = main(["analyze", self.log_path])
        self.assertEqual(exit_code, 0)
        output = stdout_buf.getvalue()
        self.assertIn("LOGLENS: SERVER LOG ANALYSIS", output)
        self.assertIn("Malformed Lines  : 1", output)
        self.assertIn("Valid Records    : 4", output)

    def test_cli_convenience_fallback_without_analyze_subcommand(self) -> None:
        # Running `main.py <file>` directly without typing `analyze`
        stdout_buf = io.StringIO()
        with redirect_stdout(stdout_buf):
            exit_code = main([self.log_path])
        self.assertEqual(exit_code, 0)
        self.assertIn("LOGLENS: SERVER LOG ANALYSIS", stdout_buf.getvalue())

    def test_cli_json_export(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            out_json = tf.name

        try:
            exit_code = main(["analyze", self.log_path, "--format", "json", "--output", out_json, "-q"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(Path(out_json).exists())

            with open(out_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["line_counts"]["valid_lines"], 4)
            self.assertEqual(data["line_counts"]["malformed_lines"], 1)
        finally:
            Path(out_json).unlink(missing_ok=True)

    def test_cli_csv_export(self) -> None:
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            out_csv = tf.name

        try:
            exit_code = main(["analyze", self.log_path, "--format", "csv", "--output", out_csv, "-q"])
            self.assertEqual(exit_code, 0)
            self.assertTrue(Path(out_csv).exists())

            with open(out_csv, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Section,Category,Item,Value,Details", content)
            self.assertIn("METADATA,Counts,ValidLines,4", content)
        finally:
            Path(out_csv).unlink(missing_ok=True)

    def test_cli_missing_input_file(self) -> None:
        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            exit_code = main(["analyze", "non_existent_file_98765.log"])
        self.assertEqual(exit_code, 1)
        self.assertIn("File Error", stderr_buf.getvalue())

    def test_cli_prevents_unsafe_input_overwrite(self) -> None:
        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            exit_code = main(["analyze", self.log_path, "--output", self.log_path])
        self.assertEqual(exit_code, 1)
        self.assertIn("Unsafe operation", stderr_buf.getvalue())

    def test_cli_invalid_parameter_values(self) -> None:
        stderr_buf = io.StringIO()
        with redirect_stderr(stderr_buf):
            exit_code1 = main(["analyze", self.log_path, "--min-errors", "0"])
        self.assertEqual(exit_code1, 2)

        stderr_buf2 = io.StringIO()
        with redirect_stderr(stderr_buf2):
            exit_code2 = main(["analyze", self.log_path, "--multiplier", "-2.5"])
        self.assertEqual(exit_code2, 2)


if __name__ == "__main__":
    unittest.main()
