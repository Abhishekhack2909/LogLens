"""Log ingestion and line validation for LogLens.

Enforces the standardized format:
    YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional, Union

from .file_utils import UnreadableFileError, validate_input_file
from .models import LogRecord, VALID_LOG_LEVELS


# Regex matching the 5 documented components:
# 1: Date (YYYY-MM-DD)
# 2: Time (HH:MM:SS)
# 3: Log level (e.g., INFO, ERROR)
# 4: Service name (alphanumeric with underscores, hyphens, and dots)
# 5: Message (the remainder of the line, non-empty)
LOG_LINE_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) ([A-Z]+) ([A-Za-z0-9_.-]+) (.+)$"
)


class MalformedLineError(Exception):
    """Raised when a log line fails format validation."""

    def __init__(self, raw_line: str, reason: str, line_number: int = 0) -> None:
        self.raw_line = raw_line
        self.reason = reason
        self.line_number = line_number
        super().__init__(f"Line {line_number} is malformed: {reason} -> {raw_line!r}")


class LogParser:
    """Validates and parses raw text lines into structured LogRecord instances."""

    @staticmethod
    def parse_line(raw_line: str, line_number: int = 0) -> LogRecord:
        """Parses a single log line into a LogRecord.

        Args:
            raw_line: The raw text line from the log file.
            line_number: Line number within the source file for error reporting.

        Returns:
            A validated LogRecord instance.

        Raises:
            MalformedLineError: If the line does not strictly match the expected format.
        """
        line = raw_line.rstrip("\r\n")

        if not line:
            raise MalformedLineError(raw_line, "Empty or blank line", line_number)

        match = LOG_LINE_PATTERN.match(line)
        if not match:
            raise MalformedLineError(
                raw_line,
                "Does not match 'YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE'",
                line_number,
            )

        date_str, time_str, level_str, service_str, message_str = match.groups()

        # Validate severity level
        if level_str not in VALID_LOG_LEVELS:
            raise MalformedLineError(
                raw_line,
                f"Unknown severity level '{level_str}'. Expected one of {sorted(VALID_LOG_LEVELS)}",
                line_number,
            )

        # Validate calendar timestamp strictly
        timestamp_str = f"{date_str} {time_str}"
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as err:
            raise MalformedLineError(
                raw_line,
                f"Invalid calendar date/time '{timestamp_str}': {err}",
                line_number,
            ) from err

        return LogRecord(
            timestamp=timestamp,
            level=level_str,
            service=service_str,
            message=message_str,
            line_number=line_number,
        )

    @classmethod
    def try_parse_line(
        cls, raw_line: str, line_number: int = 0
    ) -> tuple[Optional[LogRecord], Optional[str]]:
        """Attempts to parse a line, returning (record, None) or (None, error_reason)."""
        try:
            record = cls.parse_line(raw_line, line_number=line_number)
            return record, None
        except MalformedLineError as err:
            return None, err.reason


class LogStreamReader:
    """Streams and parses a log file line by line to minimize memory footprint."""

    def __init__(self, file_path: Union[str, Path], max_malformed_samples: int = 10) -> None:
        self.file_path = validate_input_file(file_path)
        self.max_malformed_samples = max_malformed_samples

        self.total_lines: int = 0
        self.valid_lines: int = 0
        self.malformed_lines: int = 0
        self.malformed_samples: list[dict[str, Union[int, str]]] = []

    def stream_records(self) -> Generator[LogRecord, None, None]:
        """Generator that yields valid LogRecord instances while tracking counts."""
        self.total_lines = 0
        self.valid_lines = 0
        self.malformed_lines = 0
        self.malformed_samples.clear()

        try:
            with open(self.file_path, mode="r", encoding="utf-8") as stream:
                for line_num, line in enumerate(stream, start=1):
                    self.total_lines += 1
                    record, error_reason = LogParser.try_parse_line(line, line_number=line_num)

                    if record is not None:
                        self.valid_lines += 1
                        yield record
                    else:
                        self.malformed_lines += 1
                        if len(self.malformed_samples) < self.max_malformed_samples:
                            self.malformed_samples.append({
                                "line_number": line_num,
                                "raw": line.rstrip("\r\n"),
                                "reason": error_reason or "Unknown parsing error",
                            })
        except UnicodeDecodeError as err:
            raise UnreadableFileError(
                f"File '{self.file_path}' is not valid UTF-8: {err}"
            ) from err
        except OSError as err:
            raise UnreadableFileError(
                f"Error reading file '{self.file_path}': {err}"
            ) from err
