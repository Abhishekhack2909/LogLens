"""Reporting engines for LogLens: Text, JSON, and CSV exporters."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Union

from .file_utils import check_safe_output_path, ensure_output_directory
from .models import AnalysisSummary


class TextReporter:
    """Renders human-readable, formatted text summaries for the terminal."""

    def __init__(self, summary: AnalysisSummary) -> None:
        self.summary = summary

    def render(self) -> str:
        """Constructs the formatted text report string."""
        s = self.summary
        buf = io.StringIO()

        buf.write("=" * 72 + "\n")
        buf.write("       LOGLENS: SERVER LOG ANALYSIS & ANOMALY DETECTION REPORT       \n")
        buf.write("=" * 72 + "\n\n")

        # Metadata & Ingestion Overview
        buf.write("1. INGESTION & VALIDATION OVERVIEW\n")
        buf.write("-" * 40 + "\n")
        buf.write(f"  Source File      : {s.log_file_path}\n")
        start_str = s.start_time.strftime("%Y-%m-%d %H:%M:%S") if s.start_time else "N/A"
        end_str = s.end_time.strftime("%Y-%m-%d %H:%M:%S") if s.end_time else "N/A"
        buf.write(f"  Time Window      : {start_str}  -->  {end_str}\n")
        buf.write(f"  Total Lines      : {s.total_lines:,}\n")
        pct_valid = (s.valid_lines / s.total_lines * 100) if s.total_lines > 0 else 0.0
        buf.write(f"  Valid Records    : {s.valid_lines:,} ({pct_valid:.1f}%)\n")
        buf.write(f"  Malformed Lines  : {s.malformed_lines:,}\n\n")

        # Severity Level Breakdown
        buf.write("2. LOG SEVERITY DISTRIBUTION\n")
        buf.write("-" * 40 + "\n")
        buf.write(f"  {'LEVEL':<12} {'COUNT':>8}   {'SHARE':>8}\n")
        buf.write(f"  {'-'*10:<12} {'-'*8:>8}   {'-'*8:>8}\n")
        for lvl, count in sorted(s.level_counts.items()):
            pct = (count / s.valid_lines * 100) if s.valid_lines > 0 else 0.0
            buf.write(f"  {lvl:<12} {count:>8,d}   {pct:>7.1f}%\n")
        buf.write("\n")

        # Service Activity Breakdown
        buf.write("3. SERVICE METRICS & ERROR CONTRIBUTIONS\n")
        buf.write("-" * 55 + "\n")
        buf.write(f"  {'SERVICE':<20} {'TOTAL':>8}   {'ERRORS':>8}   {'ERR RATE':>10}\n")
        buf.write(f"  {'-'*18:<20} {'-'*8:>8}   {'-'*8:>8}   {'-'*10:>10}\n")
        for svc, count in sorted(s.service_counts.items()):
            errs = s.service_error_counts.get(svc, 0)
            err_pct = (errs / count * 100) if count > 0 else 0.0
            buf.write(f"  {svc:<20} {count:>8,d}   {errs:>8,d}   {err_pct:>9.1f}%\n")
        buf.write("\n")

        # Operational Highlights
        buf.write("4. OPERATIONAL HIGHLIGHTS\n")
        buf.write("-" * 40 + "\n")
        if s.busiest_hour:
            buf.write(f"  Busiest Hour      : {s.busiest_hour} ({s.busiest_hour_count:,} requests)\n")
        else:
            buf.write("  Busiest Hour      : None (no valid records)\n")

        if s.top_error_services:
            top_svc, top_err_count = s.top_error_services[0]
            buf.write(f"  Primary Error Svc : {top_svc} ({top_err_count:,} errors)\n")
        else:
            buf.write("  Primary Error Svc : None (zero errors observed)\n")
        buf.write("\n")

        # Hourly Distribution Table
        buf.write("5. HOURLY ACTIVITY & ERROR DISTRIBUTION\n")
        buf.write("-" * 65 + "\n")
        buf.write(f"  {'HOUR':<18} {'TOTAL':>8}   {'ERRORS':>8}   {'STATUS'}\n")
        buf.write(f"  {'-'*16:<18} {'-'*8:>8}   {'-'*8:>8}   {'-'*20}\n")
        anomaly_hours = {anom.hour_key for anom in s.anomalies}
        for hour in sorted(s.hourly_stats.keys()):
            h_stat = s.hourly_stats[hour]
            status = "ANOMALY SPIKE DETECTED" if hour in anomaly_hours else "NORMAL"
            buf.write(f"  {hour:<18} {h_stat.total_count:>8,d}   {h_stat.error_count:>8,d}   {status}\n")
        buf.write("\n")

        # Anomaly Detection Evaluation
        buf.write("6. ANOMALY DETECTION (STATISTICAL THRESHOLDING)\n")
        buf.write("-" * 65 + "\n")
        buf.write(f"  Configured Min Errors  : {s.min_errors_threshold}\n")
        buf.write(f"  Configured Multiplier  : {s.multiplier_threshold:.1f}x\n")
        buf.write(f"  Hourly Error Baseline  : {s.baseline_error_rate:.2f} errors/hr\n")
        buf.write(f"  Anomalies Flagged      : {len(s.anomalies)}\n\n")

        if s.anomalies:
            buf.write("  DETECTED ANOMALOUS HOURS:\n")
            for idx, anom in enumerate(s.anomalies, start=1):
                buf.write(f"    [{idx}] Hour: {anom.hour_key}\n")
                buf.write(f"        Error Count : {anom.error_count}\n")
                buf.write(f"        Threshold   : {anom.threshold:.2f}\n")
                buf.write(f"        Diagnostic  : {anom.reason}\n")
        else:
            buf.write("  No hourly error spikes exceeded current anomaly criteria.\n")

        buf.write("\n" + "=" * 72 + "\n")
        return buf.getvalue()

    def print_report(self) -> None:
        """Prints report to standard output."""
        print(self.render())


class JsonReporter:
    """Exports structured, deterministic JSON analysis reports."""

    def __init__(self, summary: AnalysisSummary) -> None:
        self.summary = summary

    def render(self) -> str:
        """Returns pretty-printed deterministic JSON."""
        data = self.summary.to_dict()
        return json.dumps(data, indent=2, sort_keys=True)

    def export(self, output_path: Union[str, Path]) -> Path:
        """Writes JSON to destination file, enforcing directory and overwrite safety."""
        input_p = Path(self.summary.log_file_path)
        dest_p = ensure_output_directory(output_path)
        check_safe_output_path(input_p, dest_p)

        with open(dest_p, mode="w", encoding="utf-8") as f:
            f.write(self.render())
            f.write("\n")
        return dest_p


class CsvReporter:
    """Exports structured, tabular CSV reports with deterministic ordering."""

    def __init__(self, summary: AnalysisSummary) -> None:
        self.summary = summary

    def render(self) -> str:
        """Generates deterministic multi-section tabular CSV content."""
        s = self.summary
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")

        # Header
        writer.writerow(["Section", "Category", "Item", "Value", "Details"])

        # Metadata
        writer.writerow(["METADATA", "Source", "LogFilePath", s.log_file_path, ""])
        start_str = s.start_time.strftime("%Y-%m-%d %H:%M:%S") if s.start_time else "N/A"
        end_str = s.end_time.strftime("%Y-%m-%d %H:%M:%S") if s.end_time else "N/A"
        writer.writerow(["METADATA", "TimeWindow", "StartTime", start_str, ""])
        writer.writerow(["METADATA", "TimeWindow", "EndTime", end_str, ""])
        writer.writerow(["METADATA", "Counts", "TotalLines", s.total_lines, ""])
        writer.writerow(["METADATA", "Counts", "ValidLines", s.valid_lines, ""])
        writer.writerow(["METADATA", "Counts", "MalformedLines", s.malformed_lines, ""])

        # Severity breakdown
        for lvl, count in sorted(s.level_counts.items()):
            pct = round((count / s.valid_lines * 100), 2) if s.valid_lines > 0 else 0.0
            writer.writerow(["SEVERITY", "LogLevel", lvl, count, f"{pct}% share"])

        # Service breakdown
        for svc, count in sorted(s.service_counts.items()):
            errs = s.service_error_counts.get(svc, 0)
            err_pct = round((errs / count * 100), 2) if count > 0 else 0.0
            writer.writerow(["SERVICE", "ServiceTraffic", svc, count, f"{errs} errors ({err_pct}%)"])

        # Hourly stats
        anomaly_hours = {anom.hour_key for anom in s.anomalies}
        for hour in sorted(s.hourly_stats.keys()):
            h_stat = s.hourly_stats[hour]
            status = "ANOMALY" if hour in anomaly_hours else "NORMAL"
            writer.writerow([
                "HOURLY",
                "TrafficAndErrors",
                hour,
                h_stat.total_count,
                f"{h_stat.error_count} errors | Status: {status}",
            ])

        # Anomaly parameters & results
        writer.writerow(["ANOMALY_CONFIG", "Parameter", "MinErrors", s.min_errors_threshold, ""])
        writer.writerow(["ANOMALY_CONFIG", "Parameter", "Multiplier", s.multiplier_threshold, ""])
        writer.writerow(["ANOMALY_CONFIG", "Metric", "BaselineHourlyErrorRate", round(s.baseline_error_rate, 2), ""])
        writer.writerow(["ANOMALY_CONFIG", "Metric", "AnomaliesCount", len(s.anomalies), ""])

        for anom in s.anomalies:
            writer.writerow([
                "ANOMALY_EVENT",
                "DetectedSpike",
                anom.hour_key,
                anom.error_count,
                f"Threshold: {anom.threshold:.2f} | Reason: {anom.reason}",
            ])

        return buf.getvalue()

    def export(self, output_path: Union[str, Path]) -> Path:
        """Writes CSV to destination file, enforcing directory and overwrite safety."""
        input_p = Path(self.summary.log_file_path)
        dest_p = ensure_output_directory(output_path)
        check_safe_output_path(input_p, dest_p)

        with open(dest_p, mode="w", encoding="utf-8") as f:
            f.write(self.render())
        return dest_p
