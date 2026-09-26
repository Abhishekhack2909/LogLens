"""Core log analysis engine for LogLens."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable, Optional

from .anomalies import AnomalyDetector
from .models import (
    AnalysisSummary,
    HourlyStats,
    LogRecord,
    VALID_LOG_LEVELS,
)
from .parser import LogStreamReader


class LogAnalyzer:
    """Aggregates log metrics and evaluates operational anomalies."""

    def __init__(self, min_errors: int = 5, multiplier: float = 2.0) -> None:
        self.min_errors = min_errors
        self.multiplier = multiplier
        self.detector = AnomalyDetector(min_errors=min_errors, multiplier=multiplier)

    def analyze_stream(self, reader: LogStreamReader) -> AnalysisSummary:
        """Analyzes logs directly from a streaming reader without buffering entire log.

        Args:
            reader: LogStreamReader instance.

        Returns:
            An AnalysisSummary containing aggregated metrics and anomaly detections.
        """
        records_generator = reader.stream_records()
        return self._process_records(
            records=records_generator,
            log_file_path=str(reader.file_path),
            get_total_lines=lambda: reader.total_lines,
            get_valid_lines=lambda: reader.valid_lines,
            get_malformed_lines=lambda: reader.malformed_lines,
        )

    def analyze_records(
        self,
        records: Iterable[LogRecord],
        log_file_path: str = "in-memory",
        total_lines: Optional[int] = None,
        malformed_lines: int = 0,
    ) -> AnalysisSummary:
        """Analyzes an in-memory iterable of LogRecord instances (useful for testing)."""
        record_list = list(records)
        v_count = len(record_list)
        t_count = total_lines if total_lines is not None else (v_count + malformed_lines)

        return self._process_records(
            records=record_list,
            log_file_path=log_file_path,
            get_total_lines=lambda: t_count,
            get_valid_lines=lambda: v_count,
            get_malformed_lines=lambda: malformed_lines,
        )

    def _process_records(
        self,
        records: Iterable[LogRecord],
        log_file_path: str,
        get_total_lines,
        get_valid_lines,
        get_malformed_lines,
    ) -> AnalysisSummary:
        """Internal worker that processes records in a single streaming pass."""
        level_counts: dict[str, int] = {lvl: 0 for lvl in sorted(VALID_LOG_LEVELS)}
        service_counts: dict[str, int] = defaultdict(int)
        service_error_counts: dict[str, int] = defaultdict(int)
        hourly_stats: dict[str, HourlyStats] = {}

        earliest_time: Optional[datetime] = None
        latest_time: Optional[datetime] = None

        for record in records:
            # Timestamp boundaries
            if earliest_time is None or record.timestamp < earliest_time:
                earliest_time = record.timestamp
            if latest_time is None or record.timestamp > latest_time:
                latest_time = record.timestamp

            # Severity counts
            level_counts[record.level] = level_counts.get(record.level, 0) + 1

            # Service counts
            service_counts[record.service] += 1
            if record.is_error:
                service_error_counts[record.service] += 1

            # Hourly distribution
            hour_key = record.hour_key
            if hour_key not in hourly_stats:
                hourly_stats[hour_key] = HourlyStats(hour_key=hour_key)

            stats = hourly_stats[hour_key]
            stats.total_count += 1
            stats.level_counts[record.level] = stats.level_counts.get(record.level, 0) + 1
            if record.is_error:
                stats.error_count += 1

        # Calculate busiest hour (hour with the most total valid lines)
        busiest_hour: Optional[str] = None
        busiest_hour_count: int = 0
        if hourly_stats:
            # Deterministic sorting: highest total_count, then earliest hour_key
            sorted_hours_by_traffic = sorted(
                hourly_stats.items(),
                key=lambda item: (-item[1].total_count, item[0]),
            )
            busiest_hour, busiest_stats = sorted_hours_by_traffic[0]
            busiest_hour_count = busiest_stats.total_count

        # Top error services: sorted by error count desc, then service name asc
        top_error_services = sorted(
            service_error_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

        # Anomaly detection across hourly errors
        hourly_errors = {hour: stats.error_count for hour, stats in hourly_stats.items()}
        baseline_rate, anomalies = self.detector.detect_anomalies(hourly_errors)

        return AnalysisSummary(
            log_file_path=log_file_path,
            total_lines=get_total_lines(),
            valid_lines=get_valid_lines(),
            malformed_lines=get_malformed_lines(),
            start_time=earliest_time,
            end_time=latest_time,
            level_counts=level_counts,
            service_counts=dict(sorted(service_counts.items())),
            service_error_counts=dict(sorted(service_error_counts.items())),
            hourly_stats=hourly_stats,
            busiest_hour=busiest_hour,
            busiest_hour_count=busiest_hour_count,
            top_error_services=top_error_services,
            anomalies=anomalies,
            min_errors_threshold=self.min_errors,
            multiplier_threshold=self.multiplier,
            baseline_error_rate=baseline_rate,
        )
