# Project Statement: LogLens

**Project Name:** LogLens: A Python-Based Server Log Analyzer and Anomaly Detector  
**Course:** Python Essentials  
**Author:** Abhishek Tripathi  
**Target Platform:** Python 3.10+ (Cross-platform CLI)  

---

## 1. Problem Statement
Distributed backend applications and cloud services generate massive volumes of server event logs every second. These plain-text files record critical operational details, including user authentication sequences, API payload requests, background worker tasks, and system failures. 

When infrastructure outages or degraded service states occur, operations teams face three critical challenges:
1. **Memory Exhaustion on Large Files:** Common log-processing scripts load entire multi-gigabyte log archives into RAM before analyzing them, resulting in Out-Of-Memory (OOM) fatal crashes.
2. **Brittle Parsers Halting on Corrupted Data:** Real-world production logs frequently contain malformed lines, unexpected trace dumps, or truncated lines. Inflexible tools crash on the first invalid entry, halting triage and preventing inspection of remaining valid events.
3. **Lack of Transparent Incident Detection:** When service failures occur, errors spike dramatically within specific hours. Systems engineers need an explainable, deterministic mechanism to flag these anomalies without relying on opaque, nondeterministic machine learning models.

LogLens provides an accessible, deterministic, dependency-free command-line log analysis and anomaly detector that operates in bounded memory, isolates malformed records, and provides verifiable incident reports.

---

## 2. Project Scope
LogLens is engineered as a standalone, dependency-free command-line interface (CLI) application built strictly on the Python standard library. 

### Supported Scope:
- Ingestion of plain-text application logs conforming to the standardized format:
  `YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE`
- Supported log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
- Multi-word log messages containing arbitrary spaces and symbols.
- Single-pass streaming ingestion with constant $O(1)$ memory consumption.
- Comprehensive metric aggregation: total/valid/malformed counts, severity breakdowns, per-service traffic and error rates, and hourly request distribution.
- Deterministic, explainable hourly error spike anomaly detection parameterized by minimum absolute error count (`--min-errors`) and baseline multiplier factor (`--multiplier`).
- Exporting reports to human-readable terminal output, structured JSON, and tabular CSV files.
- Filesystem safety enforcement (automatic directory creation, input log overwrite prevention).

### Explicit Exclusions (Out of Scope):
- LogLens does not support arbitrary, non-standardized log formats (e.g., Apache combined, Nginx access logs, or Windows Event Logs) unless converted to the documented format.
- LogLens does not utilize black-box machine learning, neural networks, or probabilistic clustering models.
- LogLens does not incorporate persistent relational databases (RDBMS), web frameworks, or graphical user interfaces (GUIs).

---

## 3. Target Users
LogLens is tailored for technical professionals and learners operating in backend systems environments:
- **DevOps Engineers and Site Reliability Engineers (SREs):** Triaging production outages, validating deployment health, and pinpointing failing services during operational incidents.
- **Backend Developers:** Inspecting local service logs, verifying error rates, and debugging microservice interactions during staging or local development.
- **System Administrators:** Auditing server health, monitoring scheduled batch jobs, and generating compliance reports without installing third-party package dependencies.
- **Python Learners and Educators:** Studying robust software engineering practices, standard library capabilities, streaming data processing, and object-oriented architectural patterns.

---

## 4. High-Level Features
- **Streaming Log Reader (`LogStreamReader`):** Memory-bounded log ingestion using Python generator expressions.
- **Strict Format Validator (`LogParser`):** Pre-compiled regular expression matching combined with calendar date verification.
- **Single-Pass Metric Aggregator (`LogAnalyzer`):** Computes multi-dimensional operational distributions in a single traversal.
- **Deterministic Anomaly Engine (`AnomalyDetector`):** Statistical threshold rule ($T = \max(M, K \times B)$) with explicit handling for sparse and zero baselines.
- **Multi-Format Reporting Suite (`reporter.py`):**
  - **Terminal (`TextReporter`):** Rich ASCII tables and diagnostic summaries.
  - **JSON (`JsonReporter`):** Deterministic, formatted JSON with sorted keys.
  - **CSV (`CsvReporter`):** Multi-section structured tabular data for spreadsheet ingestion.
- **Defensive Filesystem Handling (`file_utils.py`):** Path resolution and overwrite conflict prevention.
- **Comprehensive CLI (`cli.py`):** Full argument parsing with help text, subcommands, smart fallbacks, and standardized exit codes.

---

## 5. Non-Functional Requirements and Solutions

LogLens addresses four essential non-functional software quality requirements:

### 1. Reliability
- **Fault-Tolerant Ingestion:** Parsing failures on individual lines are captured and recorded as malformed lines without throwing unhandled exceptions or halting execution.
- **Strict Input Validation:** Custom exception hierarchy (`InputFileNotFoundError`, `UnreadableFileError`, `UnsafeOverwriteError`) prevents unhandled crashes.
- **Full Test Coverage:** 34 unit and integration tests written using Python’s standard `unittest` framework verify end-to-end functionality with 100% pass rate.

### 2. Usability
- **Intuitive Command-Line Interface:** Configured with `argparse`, providing detailed `--help` output for discovery.
- **Convenient Shorthand Execution:** Automatically routes `python main.py server.log` directly to the analysis engine without requiring the explicit `analyze` subcommand.
- **Configurable Defaults & Quiet Mode:** Sensible defaults (`--min-errors 5`, `--multiplier 2.0`) and a `-q`/`--quiet` flag for clean pipeline scripting.
- **Standardized Process Exit Codes:** Exits with `0` on success, `1` on filesystem/IO errors, and `2` on invalid argument parameters.

### 3. Performance & Resource Efficiency
- **$O(1)$ Auxiliary Space Complexity:** Uses generator functions (`yield LogRecord`) to stream log lines, ensuring memory consumption remains low and constant regardless of file size (tested up to hundreds of megabytes).
- **Single-Pass Processing ($O(N)$ Time Complexity):** Accumulates line counts, service frequencies, and hourly error statistics simultaneously in a single pass over the log file.
- **Sub-Second Execution:** Processes 274 lines of multi-service telemetry, computes statistical baselines, and generates reports in under 0.02 seconds.

### 4. Maintainability
- **Decoupled Modular Architecture:** Clear separation of concerns across 7 distinct application modules (`models`, `file_utils`, `parser`, `analyzer`, `anomalies`, `reporter`, `cli`).
- **Strict Type Annotations:** Fully typed with Python type hints throughout, enabling static analysis verification.
- **Immutable Domain Objects:** Utilizes `@dataclass(frozen=True)` for `LogRecord` and `AnomalyResult`, guaranteeing immutability across the processing pipeline.
- **Zero Third-Party Application Dependencies:** Eliminates dependency rot, security advisories, and version deprecations.
