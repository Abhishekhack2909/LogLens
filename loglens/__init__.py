"""LogLens: A Python-based server log analyzer and anomaly detector.

LogLens provides stream-based parsing, deterministic hourly error spike detection,
and multi-format reporting (terminal, JSON, CSV) using Python's standard library.
"""

__version__ = "1.0.0"
__author__ = "Abhishek Tripathi"

from .models import LogRecord, AnalysisSummary, AnomalyResult, HourlyStats
from .parser import LogParser, LogStreamReader
from .analyzer import LogAnalyzer
from .anomalies import AnomalyDetector
from .reporter import TextReporter, JsonReporter, CsvReporter

__all__ = [
    "LogRecord",
    "AnalysisSummary",
    "AnomalyResult",
    "HourlyStats",
    "LogParser",
    "LogStreamReader",
    "LogAnalyzer",
    "AnomalyDetector",
    "TextReporter",
    "JsonReporter",
    "CsvReporter",
]
