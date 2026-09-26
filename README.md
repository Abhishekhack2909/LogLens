# LogLens: A Python-Based Server Log Analyzer and Anomaly Detector

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-Standard%20Library%20Only-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-34%20passed%20%7C%20100%25-success.svg)]()

> A stream-processing, command-line log analysis and anomaly detection tool built entirely with Python's standard library. Ingests application logs in constant memory, validates line structures, identifies deterministic hourly error spikes, and exports auditable reports in Terminal, JSON, and CSV formats.

---

## Table of Contents
- [Overview](#overview)
- [Problem Being Solved](#problem-being-solved)
- [Target Users](#target-users)
- [Major Functional Modules](#major-functional-modules)
- [Technologies Used](#technologies-used)
- [Documented Log Format & Sample Input](#documented-log-format--sample-input)
- [Prerequisites & Step-by-Step Setup](#prerequisites--step-by-step-setup)
- [Terminal Run Examples](#terminal-run-examples)
- [Actual Run Output](#actual-run-output)
- [Testing Instructions](#testing-instructions)
- [Error Handling & Filesystem Safety](#error-handling--filesystem-safety)
- [Known Limitations](#known-limitations)
- [Project Directory Structure](#project-directory-structure)

---

## Overview
**LogLens** is a high-performance command-line server log analysis and anomaly detection engine developed for the *Python Essentials* course. It processes plain-text application server logs, verifies timestamps and severity levels, aggregates multi-service operational metrics, flags hourly error spikes using deterministic statistical thresholding, and exports comprehensive audit reports.

LogLens prioritizes transparency, code maintainability, and zero external runtime dependencies. It does **not** rely on heavy machine learning frameworks, web servers, databases, or third-party packages for core execution.

---

## Problem Being Solved
When cloud services, web applications, or microservice platforms experience operational regressions, engineers face three common bottlenecks:
1. **Memory Inefficiencies:** Naive scripts read entire log files into memory at once, crashing with Out-Of-Memory (OOM) errors on large log dumps.
2. **Brittle Parsers:** Real-world logs often contain corrupted lines, system heartbeat messages, or truncated records. Fragile parsers crash on the first bad line, discarding all subsequent data.
3. **Opaque Incident Detection:** Heavyweight ML anomaly tools introduce nondeterministic black-box models that are difficult to tune and impossible to verify offline.

LogLens solves these challenges by providing:
- **Streaming Ingestion:** Line-by-line reading using Python generators ($O(1)$ auxiliary RAM).
- **Fault-Tolerant Validation:** Valid lines are parsed into immutable dataclasses while malformed lines are isolated and counted.
- **Explainable Anomaly Detection:** Deterministic thresholding based on an hourly baseline and configurable multipliers.

---

## Target Users
- **DevOps Engineers & Site Reliability Engineers (SREs):** Rapidly triage production incidents and isolate failing microservices.
- **Backend Developers:** Inspect local service logs and verify error distributions during staging or local testing.
- **System Administrators:** Audit server health and generate structured compliance reports without installing third-party packages.
- **Students & Python Developers:** Study production-quality standard library architecture, generator patterns, and clean CLI design.

---

## Major Functional Modules

### A. Log Ingestion and Validation
- **Streaming Reader (`LogStreamReader`):** Reads UTF-8 log files line-by-line without buffering the whole file in memory.
- **Strict Format Validation (`LogParser`):** Matches tokens via regular expressions and validates timestamps against real calendar rules.
- **Fault Tolerance:** Counts malformed lines, records diagnostic samples, and continues processing valid records.
- **Safety Checks:** Reports clear errors for missing, unreadable, or invalid input files.

### B. Analysis and Anomaly Detection
- **Metric Aggregation:** Computes total lines, valid records, malformed lines, severity distributions, and per-service request/error counts.
- **Hourly Activity:** Buckets events into `YYYY-MM-DD HH:00` intervals, tracking total requests and errors (`ERROR` + `CRITICAL`).
- **Operational Highlights:** Identifies the busiest operational hour and ranks services by total errors.
- **Deterministic Spike Detection (`AnomalyDetector`):** Flags hours where error counts exceed a statistical threshold:
  $$\text{Effective Threshold} = \max(\text{min\_errors}, \text{multiplier} \times \text{baseline})$$
  - Handled explicitly for zero baselines and sparse (single-hour) datasets without division-by-zero errors.
  - Fully deterministic; **not** machine learning.

### C. Reporting and Export
- **Terminal Presentation (`TextReporter`):** Clean, formatted ASCII tables and operational diagnostic highlights.
- **Structured JSON (`JsonReporter`):** Deterministic JSON export with stable key sorting.
- **Tabular CSV (`CsvReporter`):** Multi-section tabular CSV export ready for spreadsheet analysis.
- **Filesystem Protection:** Automatically creates parent destination directories and prevents overwriting the source input log.

---

## Technologies Used
- **Language:** Python 3.10 or newer (tested on Python 3.13)
- **Application Dependencies:** **100% Python Standard Library Only**:
  - `argparse` (CLI parsing and help generation)
  - `pathlib`, `os` (Cross-platform filesystem operations)
  - `datetime` (Calendar parsing and interval calculation)
  - `dataclasses` (Typed, immutable domain models)
  - `collections` (`defaultdict` metric aggregation)
  - `csv`, `json`, `io` (Deterministic report serialization)
  - `re` (Regular expression tokenization)
  - `unittest` (Test suite execution)
- **Development-Only Dependencies (Documentation):** `reportlab` and `matplotlib` (used only for generating `docs/report.pdf` and architectural diagrams; **not** required to run the core LogLens CLI application).

---

## Documented Log Format & Sample Input
LogLens strictly expects plain-text application logs conforming to this exact format:
```text
YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE
```

### Format Specification:
| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `YYYY-MM-DD` | Calendar Date | 4-digit year, 2-digit month, 2-digit day | `2026-09-26` |
| `HH:MM:SS` | 24-Hour Time | 2-digit hour, 2-digit minute, 2-digit second | `10:15:30` |
| `LEVEL` | Severity String | Must be `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` | `ERROR` |
| `SERVICE` | Alphanumeric | Service name identifier (letters, numbers, `_`, `-`, `.`) | `auth` |
| `MESSAGE` | Text String | The remainder of the line, including spaces and symbols | `Login failed for user 4921` |

### Sample Valid Lines:
```text
2026-09-26 10:15:30 ERROR auth Login failed for user 4921
2026-09-26 10:16:02 INFO api-gateway Request GET /v1/catalog completed in 45ms
2026-09-26 14:02:11 CRITICAL payment-service Primary payment gateway unresponsive
```

> **Note:** LogLens does not claim to parse Apache, Nginx, or syslog formats unless they are formatted to match the documented structure above.

---

## Prerequisites & Step-by-Step Setup

### Prerequisites
- Python 3.10 or newer installed on your machine.
- Verify Python installation:
  ```bash
  python --version
  ```

### Step-by-Step Setup
1. Clone or extract the LogLens repository into your working directory:
   ```bash
   cd LogLens
   ```
2. Verify that the sample log file is present:
   ```bash
   # On Windows
   dir sample_logs\server.log

   # On Linux/macOS
   ls -la sample_logs/server.log
   ```
3. Run the help command to confirm the CLI is ready:
   ```bash
   python main.py --help
   ```

*(No `pip install` is required to run the LogLens application! Core execution uses Python's standard library).*

---

## Terminal Run Examples

### 1. Standard Analysis (Terminal Output)
```bash
python main.py analyze sample_logs/server.log
```
*(Convenience shorthand also supported: `python main.py sample_logs/server.log`)*

### 2. Export to Structured JSON
```bash
python main.py analyze sample_logs/server.log --format json --output reports/summary.json
```

### 3. Export to Tabular CSV
```bash
python main.py analyze sample_logs/server.log --format csv --output reports/summary.csv
```

### 4. Custom Anomaly Thresholding
```bash
python main.py analyze sample_logs/server.log --min-errors 5 --multiplier 2.0
```

### 5. Quiet Mode (File Export Only)
```bash
python main.py analyze sample_logs/server.log --format json --output reports/summary.json --quiet
```

---

## Actual Run Output
Below is the exact output produced by LogLens when analyzing `sample_logs/server.log`:

```text
$ python main.py analyze sample_logs/server.log

========================================================================
       LOGLENS: SERVER LOG ANALYSIS & ANOMALY DETECTION REPORT       
========================================================================

1. INGESTION & VALIDATION OVERVIEW
----------------------------------------
  Source File      : D:\LogLens\sample_logs\server.log
  Time Window      : 2026-09-26 08:00:48  -->  2026-09-26 17:55:57
  Total Lines      : 274
  Valid Records    : 270 (98.5%)
  Malformed Lines  : 4

2. LOG SEVERITY DISTRIBUTION
----------------------------------------
  LEVEL           COUNT      SHARE
  ----------   --------   --------
  CRITICAL           10       3.7%
  DEBUG              46      17.0%
  ERROR              31      11.5%
  INFO              159      58.9%
  WARNING            24       8.9%

3. SERVICE METRICS & ERROR CONTRIBUTIONS
-------------------------------------------------------
  SERVICE                 TOTAL     ERRORS     ERR RATE
  ------------------   --------   --------   ----------
  api-gateway                43          8        18.6%
  auth                       37          4        10.8%
  inventory                  45          0         0.0%
  notification-worker        36          2         5.6%
  order-service              60         14        23.3%
  payment-service            49         13        26.5%

4. OPERATIONAL HIGHLIGHTS
----------------------------------------
  Busiest Hour      : 2026-09-26 14:00 (45 requests)
  Primary Error Svc : order-service (14 errors)

5. HOURLY ACTIVITY & ERROR DISTRIBUTION
-----------------------------------------------------------------
  HOUR                  TOTAL     ERRORS   STATUS
  ----------------   --------   --------   --------------------
  2026-09-26 08:00         25          2   NORMAL
  2026-09-26 09:00         25          1   NORMAL
  2026-09-26 10:00         25          1   NORMAL
  2026-09-26 11:00         25          1   NORMAL
  2026-09-26 12:00         25          1   NORMAL
  2026-09-26 13:00         25          1   NORMAL
  2026-09-26 14:00         45         29   ANOMALY SPIKE DETECTED
  2026-09-26 15:00         25          3   NORMAL
  2026-09-26 16:00         25          1   NORMAL
  2026-09-26 17:00         25          1   NORMAL

6. ANOMALY DETECTION (STATISTICAL THRESHOLDING)
-----------------------------------------------------------------
  Configured Min Errors  : 5
  Configured Multiplier  : 2.0x
  Hourly Error Baseline  : 4.10 errors/hr
  Anomalies Flagged      : 1

  DETECTED ANOMALOUS HOURS:
    [1] Hour: 2026-09-26 14:00
        Error Count : 29
        Threshold   : 8.20
        Diagnostic  : Hourly spike: error count (29) exceeded threshold (8.20) [7.1x baseline 4.10, min 5]

========================================================================
```

---

## Testing Instructions
The complete test suite is implemented using Python's built-in `unittest` framework and requires no external packages.

To run the complete test suite with verbose output, execute:
```bash
python -m unittest discover -s tests -v
```

### Verified Test Results:
```text
Ran 34 tests in 0.149s

OK
```
All 34 tests pass across four test modules:
- `tests/test_parser.py`: 11 tests (Valid line parsing, multi-word messages, invalid dates, unknown levels, truncated lines, blank lines, streaming ingestion).
- `tests/test_analyzer.py`: 6 tests (Total/valid/malformed counts, severity distributions, service counts, busiest hour detection, top error services, dictionary conversion).
- `tests/test_anomalies.py`: 8 tests (Baseline calculations, normal multi-hour data, anomalous spikes, zero baselines with sudden bursts, single-hour sparse baselines, parameter validation).
- `tests/test_cli.py`: 9 tests (CLI help flags, text analysis execution, JSON export, CSV export, missing file handling, input overwrite prevention, invalid arguments, fallback routing).

---

## Error Handling & Filesystem Safety

LogLens provides defensive error handling with clear exit codes:
- **Missing File Error (Exit Code 1):** If the input file does not exist or is a directory, LogLens reports an informative message:
  ```text
  File Error: Input log file not found: 'sample_logs/non_existent.log'
  ```
- **Unsafe Overwrite Prevention (Exit Code 1):** If the destination `--output` path points to the same file as the input log, LogLens halts before creating file streams:
  ```text
  Security/Overwrite Error: Unsafe operation: output destination '...' cannot be identical to input log file.
  ```
- **Invalid CLI Arguments (Exit Code 2):** If parameters are invalid (e.g., `--min-errors 0` or `--multiplier -1.5`):
  ```text
  Error: --min-errors must be an integer >= 1 (got 0)
  ```
- **Malformed Line Tolerance (Exit Code 0):** Corrupted lines do not crash the engine; they are counted, recorded in diagnostics, and valid records are processed uninterrupted.

---

## Known Limitations
1. **Single Accepted Log Format:** LogLens only processes logs matching `YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE`. It does not support arbitrary custom formats (such as Apache Common or Nginx log formats) unless pre-formatted.
2. **Batch Processing (No Real-Time Tailing):** LogLens operates as a static batch analyzer. It does not currently implement real-time log tailing (`tail -f`).
3. **Top-of-the-Hour Grouping:** The anomaly detection groups errors into discrete clock-hour buckets (`HH:00`). Spikes spanning across the boundary of an hour (e.g., 10:45 to 11:15) are evaluated across their respective calendar hours rather than a sliding window.

---

## Project Directory Structure
```text
LogLens/
├── .gitignore                      # Git exclusion rules
├── README.md                       # Comprehensive repository documentation
├── statement.md                    # Project statement and NFR specifications
├── main.py                         # Root application entrypoint
├── loglens/                        # Core package
│   ├── __init__.py                 # Package exports and version metadata
│   ├── models.py                   # Data models (LogRecord, HourlyStats, etc.)
│   ├── file_utils.py               # Path validation and overwrite safety
│   ├── parser.py                   # Streaming reader and format validation
│   ├── analyzer.py                 # Single-pass metric aggregation engine
│   ├── anomalies.py                # Deterministic anomaly detection heuristic
│   ├── reporter.py                 # Text, JSON, and CSV exporters
│   └── cli.py                      # argparse CLI configuration and routing
├── sample_logs/                    # Sample data
│   └── server.log                  # Realistic 274-line log with normal & spike data
├── reports/                        # Export directory
│   ├── summary.json                # Sample generated JSON report
│   └── summary.csv                 # Sample generated CSV report
├── docs/                           # Design documentation & PDF report
│   ├── architecture.png            # System architecture diagram
│   ├── workflow.png                # Processing workflow diagram
│   ├── use_case.png                # Use case diagram
│   ├── sequence.png                # Sequence execution diagram
│   ├── class_diagram.png           # Class and component diagram
│   ├── generate_diagrams.py        # Diagram rendering script (matplotlib)
│   ├── generate_pdf.py             # PDF builder script (ReportLab)
│   ├── report.md                   # Editable 15-section source report
│   └── report.pdf                  # Publication-grade PDF report (15 pages)
└── tests/                          # Automated unit test suite
    ├── __init__.py
    ├── test_parser.py              # Parsing & stream ingestion tests
    ├── test_analyzer.py            # Metric calculation & aggregation tests
    ├── test_anomalies.py           # Anomaly detection & baseline tests
    └── test_cli.py                 # CLI interface, argument, & safety tests
```
