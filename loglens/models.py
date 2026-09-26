"""Data models and value containers for LogLens."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


VALID_LOG_LEVELS: frozenset[str] = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
ERROR_LOG_LEVELS: frozenset[str] = frozenset({"ERROR", "CRITICAL"})


@dataclass(frozen=True)
class LogRecord:
    """Represents a validated, parsed log line."""

    timestamp: datetime
    level: str
    service: str
    message: str
    line_number: int

    @property
    def hour_key(self) -> str:
        """Returns the hour bucket string in 'YYYY-MM-DD HH:00' format."""
        return self.timestamp.strftime("%Y-%m-%d %H:00")

    @property
    def is_error(self) -> bool:
        """Indicates whether this record is an ERROR or CRITICAL severity entry."""
        return self.level in ERROR_LOG_LEVELS


@dataclass
class HourlyStats:
    """Aggregated statistics for a single one-hour bucket."""

    hour_key: str
    total_count: int = 0
    error_count: int = 0
    level_counts: dict[str, int] = field(default_factory=lambda: {lvl: 0 for lvl in sorted(VALID_LOG_LEVELS)})

    def to_dict(self) -> dict[str, Any]:
        """Convert hourly statistics to a dictionary."""
        return {
            "hour": self.hour_key,
            "total_count": self.total_count,
            "error_count": self.error_count,
            "level_counts": dict(sorted(self.level_counts.items())),
        }


@dataclass(frozen=True)
class AnomalyResult:
    """Represents an anomaly detection event for an hourly error spike."""

    hour_key: str
    error_count: int
    baseline_mean: float
    threshold: float
    multiplier: float
    min_errors: int
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Convert anomaly result to a dictionary representation."""
        return {
            "hour": self.hour_key,
            "error_count": self.error_count,
            "baseline_mean": round(self.baseline_mean, 2),
            "threshold": round(self.threshold, 2),
            "multiplier": self.multiplier,
            "min_errors": self.min_errors,
            "reason": self.reason,
        }


@dataclass
class AnalysisSummary:
    """Consolidated summary of log ingestion, validation, and anomaly detection."""

    log_file_path: str
    total_lines: int
    valid_lines: int
    malformed_lines: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    level_counts: dict[str, int]
    service_counts: dict[str, int]
    service_error_counts: dict[str, int]
    hourly_stats: dict[str, HourlyStats]
    busiest_hour: Optional[str]
    busiest_hour_count: int
    top_error_services: list[tuple[str, int]]
    anomalies: list[AnomalyResult]
    min_errors_threshold: int
    multiplier_threshold: float
    baseline_error_rate: float

    def to_dict(self) -> dict[str, Any]:
        """Returns a deterministic dictionary representation of the analysis."""
        return {
            "meta": {
                "source_file": self.log_file_path,
                "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else None,
                "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else None,
            },
            "line_counts": {
                "total_lines": self.total_lines,
                "valid_lines": self.valid_lines,
                "malformed_lines": self.malformed_lines,
            },
            "severity_counts": dict(sorted(self.level_counts.items())),
            "service_counts": dict(sorted(self.service_counts.items())),
            "service_error_counts": dict(sorted(self.service_error_counts.items())),
            "busiest_hour": {
                "hour": self.busiest_hour,
                "count": self.busiest_hour_count,
            },
            "top_error_services": [
                {"service": svc, "error_count": count}
                for svc, count in self.top_error_services
            ],
            "anomaly_detection": {
                "parameters": {
                    "min_errors": self.min_errors_threshold,
                    "multiplier": self.multiplier_threshold,
                },
                "baseline_hourly_error_rate": round(self.baseline_error_rate, 2),
                "anomalies_detected_count": len(self.anomalies),
                "anomalies": [anom.to_dict() for anom in self.anomalies],
            },
            "hourly_statistics": [
                self.hourly_stats[hour].to_dict()
                for hour in sorted(self.hourly_stats.keys())
            ],
        }
