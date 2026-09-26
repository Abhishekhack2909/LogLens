"""Generates a publication-grade PDF report for the LogLens project using ReportLab.

Contains the 15 required sections in exact order:
1. Cover Page
2. Introduction
3. Problem Statement
4. Functional Requirements
5. Non-functional Requirements
6. System Architecture
7. Design Diagrams
8. Design Decisions and Rationale
9. Implementation Details
10. Screenshots or Results
11. Testing Approach
12. Challenges Faced
13. Learnings and Key Takeaways
14. Future Enhancements
15. References
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.pdfgen import canvas

DOCS_DIR = Path("docs")
PDF_OUTPUT_PATH = DOCS_DIR / "report.pdf"


class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass calculation to render accurate total page counts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress header and footer on the formal cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Running Header
        self.drawString(54, 750, "LogLens: A Python-Based Server Log Analyzer and Anomaly Detector")
        self.setFont("Helvetica", 8)
        self.drawRightString(612 - 54, 750, "Python Essentials Project Report")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 742, 612 - 54, 742)

        # Running Footer
        self.line(54, 48, 612 - 54, 48)
        self.drawString(54, 34, "Author: Abhishek Tripathi  |  Course: Python Essentials")
        self.drawRightString(612 - 54, 34, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf_report():
    """Builds the comprehensive LogLens project PDF."""
    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#1B365D"),
        alignment=1, # Centered
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        alignment=1,
    )

    meta_label = ParagraphStyle(
        "CoverMetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#2D3748"),
    )

    meta_val = ParagraphStyle(
        "CoverMetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        textColor=colors.HexColor("#1B365D"),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "BulletDark",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    code_style = ParagraphStyle(
        "CodeTerminal",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#1A202C"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2D3748"),
    )

    callout_style = ParagraphStyle(
        "CalloutBox",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#744210"),
    )

    story = []

    # =========================================================================
    # SECTION 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("PROJECT SUBMISSION REPORT", ParagraphStyle("Overhead", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#718096"), alignment=1)))
    story.append(Spacer(1, 15))
    story.append(Paragraph("LogLens: A Python-Based Server Log Analyzer and Anomaly Detector", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("A Stream-Processing CLI Engine for Operational Log Diagnostics and Error Spike Detection", subtitle_style))
    story.append(Spacer(1, 25))

    story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#3182CE"), spaceBefore=10, spaceAfter=30))

    # Formal Metadata Table
    meta_data = [
        [Paragraph("Student Name:", meta_label), Paragraph("Abhishek Tripathi", meta_val)],
        [Paragraph("Course Title:", meta_label), Paragraph("Python Essentials", meta_val)],
        [Paragraph("Project Title:", meta_label), Paragraph("LogLens: A Python-Based Server Log Analyzer and Anomaly Detector", meta_val)],
        [Paragraph("Execution Platform:", meta_label), Paragraph("Python 3.10+ (Standard Library Architecture)", meta_val)],
        [Paragraph("Submission Date:", meta_label), Paragraph("September 2026", meta_val)],
        [Paragraph("Repository Scope:", meta_label), Paragraph("CLI Utility, Data Models, Parser, Analyzer, Anomaly Engine, Reporters, Test Suite", meta_val)],
    ]
    meta_table = Table(meta_data, colWidths=[150, 320])
    meta_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 40))
    story.append(Paragraph("<i>Academic Project Verification: Verified locally with standard library unittest suite and deterministic report exports.</i>", ParagraphStyle("Verify", fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#718096"), alignment=1)))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 2: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("2. Introduction", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))
    story.append(Paragraph(
        "Modern cloud backends, microservice architectures, and distributed systems generate massive volumes of server event logs. "
        "These plain-text log files serve as the definitive record of system operations, capturing user authentications, API transactions, "
        "transient retries, database queries, and unexpected infrastructure outages. However, extracting actionable insight from raw log streams "
        "is fraught with practical challenges.", body_style
    ))
    story.append(Paragraph(
        "Standard Unix utilities such as <code>grep</code>, <code>awk</code>, or <code>sed</code> lack structured date awareness and fail to calculate "
        "statistically grounded multi-service distributions. Conversely, enterprise observability platforms (such as Splunk, Datadog, or Elasticsearch) "
        "introduce high cloud subscription costs, heavyweight runtime requirements, network latency, and complex agent installations. Furthermore, "
        "overly complex machine-learning solutions introduce nondeterministic black-box models that require extensive training data and GPU resources.", body_style
    ))
    story.append(Paragraph(
        "<b>LogLens</b> is an original, command-line server log analyzer and anomaly detector engineered specifically for operational transparency. "
        "Built strictly on Python's robust standard library without external dependencies, LogLens provides high-performance stream ingestion, "
        "strict format validation, transparent statistical error spike detection, and multi-format reporting (terminal tables, deterministic JSON, and tabular CSV).", body_style
    ))

    # =========================================================================
    # SECTION 3: PROBLEM STATEMENT
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Problem Statement", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))
    story.append(Paragraph(
        "Operations engineers and backend developers triaging production incidents encounter three fundamental pain points when analyzing server logs:", body_style
    ))
    story.append(Paragraph("• <b>Memory Inefficiency & OOM Crashes:</b> Naive parsing scripts load entire multi-gigabyte log archives into RAM before processing, leading to Out-Of-Memory termination on developer laptops or resource-constrained server instances.", bullet_style))
    story.append(Paragraph("• <b>Format Fragility & Unhandled Exceptions:</b> Production logs frequently contain malformed lines, unexpected network traces, or truncated timestamps. Inflexible parsers crash upon the first malformed entry, discarding all remaining operational data.", bullet_style))
    story.append(Paragraph("• <b>Opaque Incident Diagnosis:</b> When an outage occurs (such as a database connection pool exhaustion or external API timeout), error counts spike within specific hours. Engineers need a deterministic, easily tunable heuristic to identify anomalous hours and isolate culprit services immediately.", bullet_style))
    story.append(Paragraph(
        "LogLens directly solves these issues by providing constant-memory ($O(1)$ RAM) streaming ingestion, robust line validation that isolates malformed records, "
        "and a fully explainable, configurable baseline error-spike detection rule.", body_style
    ))

    # =========================================================================
    # SECTION 4: FUNCTIONAL REQUIREMENTS
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Functional Requirements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    story.append(Paragraph("Module A: Log Ingestion and Validation", h2_style))
    story.append(Paragraph("• <b>FR-1.1 (Standard Format Conformance):</b> Parse plain-text logs adhering strictly to: <code>YYYY-MM-DD HH:MM:SS LEVEL SERVICE MESSAGE</code>. Common levels supported: <code>DEBUG</code>, <code>INFO</code>, <code>WARNING</code>, <code>ERROR</code>, <code>CRITICAL</code>.", bullet_style))
    story.append(Paragraph("• <b>FR-1.2 (Strict Calendar & Severity Validation):</b> Enforce true calendar validation (rejecting invalid dates like February 30 or hour 25) and verify case-sensitive level membership.", bullet_style))
    story.append(Paragraph("• <b>FR-1.3 (Fault-Tolerant Streaming Ingestion):</b> Ingest log files line-by-line via Python generator functions, recording total and malformed line counts without terminating prematurely.", bullet_style))
    story.append(Paragraph("• <b>FR-1.4 (Input File Verification):</b> Detect and gracefully report missing, inaccessible, or non-UTF-8 log files with informative error messages.", bullet_style))

    story.append(Paragraph("Module B: Analysis and Anomaly Detection", h2_style))
    story.append(Paragraph("• <b>FR-2.1 (Aggregation Metrics):</b> Compute total lines, valid records, malformed lines, severity breakdowns, and per-service request/error totals.", bullet_style))
    story.append(Paragraph("• <b>FR-2.2 (Hourly Distribution):</b> Aggregate log events into chronological hourly buckets (<code>YYYY-MM-DD HH:00</code>), tracking total lines and error sums (<code>ERROR</code> + <code>CRITICAL</code>).", bullet_style))
    story.append(Paragraph("• <b>FR-2.3 (Operational Highlights):</b> Identify the busiest operational hour and rank services by absolute error contribution.", bullet_style))
    story.append(Paragraph("• <b>FR-2.4 (Deterministic Anomaly Detection):</b> Flag hourly error spikes using a statistical rule parameterized by <code>--min-errors</code> ($M$) and <code>--multiplier</code> ($K$). Calculate hourly baseline ($B$). For zero or single-hour baselines, flag hours meeting $M$; for multi-hour baselines, flag hours exceeding $\\max(M, K \\times B)$.", bullet_style))

    story.append(Paragraph("Module C: Reporting and Export", h2_style))
    story.append(Paragraph("• <b>FR-3.1 (Terminal Presentation):</b> Print a clean, formatted ASCII report with aligned tabular metrics and diagnostic descriptions.", bullet_style))
    story.append(Paragraph("• <b>FR-3.2 (Deterministic JSON Export):</b> Export comprehensive operational metrics to formatted JSON with sorted keys and stable ordering.", bullet_style))
    story.append(Paragraph("• <b>FR-3.3 (Tabular CSV Export):</b> Export multi-section structured tabular data suitable for automated spreadsheet ingestion.", bullet_style))
    story.append(Paragraph("• <b>FR-3.4 (Filesystem Safety):</b> Create target directories automatically and raise <code>UnsafeOverwriteError</code> if the output destination matches the input log.", bullet_style))

    # =========================================================================
    # SECTION 5: NON-FUNCTIONAL REQUIREMENTS
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Non-functional Requirements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    nfr_table_data = [
        [Paragraph("Pillar", table_header_style), Paragraph("Requirement Specification", table_header_style), Paragraph("Architectural Solution & Validation", table_header_style)],
        [
            Paragraph("<b>Reliability</b>", table_cell_style),
            Paragraph("Zero-crash guarantee during malformed line encounters; safe error isolation.", table_cell_style),
            Paragraph("Malformed lines isolated via <code>try_parse_line</code>; specific exceptions for IO/security; 34 passing unit tests.", table_cell_style),
        ],
        [
            Paragraph("<b>Usability</b>", table_cell_style),
            Paragraph("Intuitive command-line interface with sensible defaults and clear feedback.", table_cell_style),
            Paragraph("Built with <code>argparse</code>; provides <code>--help</code>, smart positional fallback, quiet export mode (<code>-q</code>), and exit codes.", table_cell_style),
        ],
        [
            Paragraph("<b>Performance & Efficiency</b>", table_cell_style),
            Paragraph("Bounded memory usage and single-pass computation across large files.", table_cell_style),
            Paragraph("Streaming generator pipeline ensures $O(1)$ memory; single-pass $O(N)$ execution processes 274 lines in <0.02s.", table_cell_style),
        ],
        [
            Paragraph("<b>Maintainability</b>", table_cell_style),
            Paragraph("Modular codebase with strict typing, frozen dataclasses, and zero frameworks.", table_cell_style),
            Paragraph("Divided into 7 decoupled modules; comprehensive docstrings; Python standard library architecture only.", table_cell_style),
        ],
    ]
    nfr_table = Table(nfr_table_data, colWidths=[95, 195, 210])
    nfr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B365D")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(nfr_table)

    # =========================================================================
    # SECTION 6: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. System Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))
    story.append(Paragraph(
        "LogLens utilizes a modular, layered pipeline architecture. The application decouples user input parsing, filesystem validation, "
        "stream-based record tokenization, single-pass metric accumulation, anomaly rule evaluation, and output serialization into distinct modules.", body_style
    ))
    story.append(Paragraph(
        "1. <b>CLI Entry Layer (<code>main.py</code> / <code>loglens.cli</code>):</b> Parses arguments, validates parameter ranges, handles convenience fallbacks, and manages exit codes.<br/>"
        "2. <b>Filesystem Protection Layer (<code>loglens.file_utils</code>):</b> Verifies file readability, resolves absolute paths, creates target directories, and enforces overwrite protection.<br/>"
        "3. <b>Streaming Ingestion Layer (<code>loglens.parser</code>):</b> Reads log files line-by-line via <code>LogStreamReader</code>, parses tokens via pre-compiled regex, validates timestamps, and isolates malformed records.<br/>"
        "4. <b>Domain Model Layer (<code>loglens.models</code>):</b> Defines typed dataclasses (<code>LogRecord</code>, <code>HourlyStats</code>, <code>AnomalyResult</code>, <code>AnalysisSummary</code>) guaranteeing data immutability.<br/>"
        "5. <b>Analytics Engine (<code>loglens.analyzer</code> & <code>loglens.anomalies</code>):</b> Computes hourly statistics and executes deterministic statistical thresholding.<br/>"
        "6. <b>Reporting Layer (<code>loglens.reporter</code>):</b> Implements <code>TextReporter</code>, <code>JsonReporter</code>, and <code>CsvReporter</code> for deterministic rendering.", body_style
    ))

    # =========================================================================
    # SECTION 7: DESIGN DIAGRAMS
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("7. Design Diagrams", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    story.append(Paragraph("7.1 System Architecture Diagram", h2_style))
    story.append(Image(str(DOCS_DIR / "architecture.png"), width=480, height=295))
    story.append(Spacer(1, 8))

    story.append(Paragraph("7.2 Ingestion & Analysis Workflow Diagram", h2_style))
    story.append(Image(str(DOCS_DIR / "workflow.png"), width=480, height=240))
    story.append(PageBreak())

    story.append(Paragraph("7.3 Use Case Diagram", h2_style))
    story.append(Image(str(DOCS_DIR / "use_case.png"), width=470, height=280))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7.4 Sequence Diagram for Log Analysis", h2_style))
    story.append(Image(str(DOCS_DIR / "sequence.png"), width=480, height=285))
    story.append(PageBreak())

    story.append(Paragraph("7.5 Class and Component Diagram", h2_style))
    story.append(Image(str(DOCS_DIR / "class_diagram.png"), width=480, height=310))
    story.append(Spacer(1, 12))

    story.append(Paragraph("7.6 Architectural Note: Entity-Relationship (ER) Diagram", h2_style))
    er_notice = [
        [Paragraph("<b>Architectural Consideration Regarding ER Diagrams:</b><br/>"
                   "LogLens operates strictly as an in-memory streaming log processor and does not utilize an external relational database (RDBMS), "
                   "NoSQL store, or persistent entity schema. Data structures exist during runtime as transient dataclasses (<code>LogRecord</code>, "
                   "<code>HourlyStats</code>, <code>AnalysisSummary</code>) and are exported directly to flat text, JSON, or CSV files. Therefore, an "
                   "Entity-Relationship (ER) diagram is <b>not applicable</b> to this project. In adherence to honest software engineering practices, "
                   "no synthetic database tables were invented.", callout_style)]
    ]
    er_table = Table(er_notice, colWidths=[500])
    er_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEFCBF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#D69E2E")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(er_table)

    # =========================================================================
    # SECTION 8: DESIGN DECISIONS AND RATIONALE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("8. Design Decisions and Rationale", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    decisions = [
        ("1. Standard Library Exclusivity",
         "The application relies entirely on Python 3.10+ standard library modules (<code>argparse</code>, <code>dataclasses</code>, <code>datetime</code>, <code>collections</code>, <code>csv</code>, <code>json</code>, <code>pathlib</code>, <code>re</code>, <code>unittest</code>). This avoids fragile dependency chains, simplifies installation, and guarantees cross-platform stability."),
        ("2. Streaming Generator Architecture",
         "Log ingestion is implemented using a Python generator (<code>yield LogRecord</code>) inside <code>LogStreamReader</code> rather than buffering all records into a list. This bounds memory consumption to $O(1)$ auxiliary RAM, enabling the tool to parse multi-gigabyte log files without exhausting system memory."),
        ("3. Deterministic Statistical Rules vs. Machine Learning",
         "Anomaly detection uses a deterministic formula ($T = \\max(M, K \\times B)$) rather than machine learning clustering. Operational triage requires transparent, explainable alerts. Black-box ML models introduce unpredictable false positives, require historical training data, and cannot be tuned via straightforward CLI flags."),
        ("4. Immutable Frozen Dataclasses",
         "<code>LogRecord</code> is declared with <code>@dataclass(frozen=True)</code> to prevent accidental attribute tampering during metric aggregation, ensure thread safety, and enable robust unit testing."),
        ("5. Filesystem Overwrite Protection",
         "Input and output paths are canonicalized using <code>Path.resolve()</code> to prevent catastrophic data loss where a user mistakenly specifies the input log as the output destination."),
    ]

    for title, desc in decisions:
        story.append(Paragraph(f"<b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))

    # =========================================================================
    # SECTION 9: IMPLEMENTATION DETAILS
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("9. Implementation Details", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    story.append(Paragraph("The LogLens codebase is organized into 7 cohesive application modules:", body_style))
    impl_table_data = [
        [Paragraph("Module File", table_header_style), Paragraph("Primary Class / Responsibilities", table_header_style), Paragraph("Standard Library Dependencies", table_header_style)],
        [Paragraph("<code>main.py</code>", table_cell_style), Paragraph("Root CLI entrypoint delegating to <code>loglens.cli.main()</code>.", table_cell_style), Paragraph("<code>sys</code>", table_cell_style)],
        [Paragraph("<code>loglens/models.py</code>", table_cell_style), Paragraph("Data structures: <code>LogRecord</code>, <code>HourlyStats</code>, <code>AnomalyResult</code>, <code>AnalysisSummary</code>.", table_cell_style), Paragraph("<code>dataclasses</code>, <code>datetime</code>, <code>typing</code>", table_cell_style)],
        [Paragraph("<code>loglens/file_utils.py</code>", table_cell_style), Paragraph("Path resolution, directory creation, safe overwrite prevention, custom file exceptions.", table_cell_style), Paragraph("<code>pathlib</code>, <code>os</code>", table_cell_style)],
        [Paragraph("<code>loglens/parser.py</code>", table_cell_style), Paragraph("Streaming ingestion (<code>LogStreamReader</code>) and regex/calendar validation (<code>LogParser</code>).", table_cell_style), Paragraph("<code>re</code>, <code>datetime</code>, <code>pathlib</code>", table_cell_style)],
        [Paragraph("<code>loglens/analyzer.py</code>", table_cell_style), Paragraph("Single-pass metric aggregation (<code>LogAnalyzer</code>) and busiest hour calculation.", table_cell_style), Paragraph("<code>collections</code>, <code>datetime</code>", table_cell_style)],
        [Paragraph("<code>loglens/anomalies.py</code>", table_cell_style), Paragraph("Deterministic statistical error spike detection (<code>AnomalyDetector</code>).", table_cell_style), Paragraph("<code>typing</code>", table_cell_style)],
        [Paragraph("<code>loglens/reporter.py</code>", table_cell_style), Paragraph("Exporters: <code>TextReporter</code> (terminal tables), <code>JsonReporter</code>, and <code>CsvReporter</code>.", table_cell_style), Paragraph("<code>json</code>, <code>csv</code>, <code>io</code>, <code>pathlib</code>", table_cell_style)],
        [Paragraph("<code>loglens/cli.py</code>", table_cell_style), Paragraph("Argument parsing, parameter validation, subcommands, and exit codes.", table_cell_style), Paragraph("<code>argparse</code>, <code>sys</code>, <code>pathlib</code>", table_cell_style)],
    ]
    impl_table = Table(impl_table_data, colWidths=[110, 240, 150])
    impl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B365D")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(impl_table)

    # =========================================================================
    # SECTION 10: SCREENSHOTS OR RESULTS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("10. Screenshots or Results", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    story.append(Paragraph("10.1 Real Terminal Analysis Run", h2_style))
    terminal_output = (
        "$ python main.py analyze sample_logs/server.log\n\n"
        "========================================================================\n"
        "       LOGLENS: SERVER LOG ANALYSIS & ANOMALY DETECTION REPORT       \n"
        "========================================================================\n\n"
        "1. INGESTION & VALIDATION OVERVIEW\n"
        "----------------------------------------\n"
        "  Source File      : D:\\LogLens\\sample_logs\\server.log\n"
        "  Time Window      : 2026-09-26 08:00:48  -->  2026-09-26 17:55:57\n"
        "  Total Lines      : 274\n"
        "  Valid Records    : 270 (98.5%)\n"
        "  Malformed Lines  : 4\n\n"
        "2. LOG SEVERITY DISTRIBUTION\n"
        "----------------------------------------\n"
        "  LEVEL           COUNT      SHARE\n"
        "  ----------   --------   --------\n"
        "  CRITICAL           10       3.7%\n"
        "  DEBUG              46      17.0%\n"
        "  ERROR              31      11.5%\n"
        "  INFO              159      58.9%\n"
        "  WARNING            24       8.9%\n\n"
        "3. SERVICE METRICS & ERROR CONTRIBUTIONS\n"
        "-------------------------------------------------------\n"
        "  SERVICE                 TOTAL     ERRORS     ERR RATE\n"
        "  ------------------   --------   --------   ----------\n"
        "  api-gateway                43          8        18.6%\n"
        "  auth                       37          4        10.8%\n"
        "  inventory                  45          0         0.0%\n"
        "  notification-worker        36          2         5.6%\n"
        "  order-service              60         14        23.3%\n"
        "  payment-service            49         13        26.5%\n\n"
        "4. OPERATIONAL HIGHLIGHTS\n"
        "----------------------------------------\n"
        "  Busiest Hour      : 2026-09-26 14:00 (45 requests)\n"
        "  Primary Error Svc : order-service (14 errors)\n\n"
        "5. HOURLY ACTIVITY & ERROR DISTRIBUTION\n"
        "-----------------------------------------------------------------\n"
        "  HOUR                  TOTAL     ERRORS   STATUS\n"
        "  ----------------   --------   --------   --------------------\n"
        "  2026-09-26 08:00         25          2   NORMAL\n"
        "  2026-09-26 09:00         25          1   NORMAL\n"
        "  2026-09-26 10:00         25          1   NORMAL\n"
        "  2026-09-26 11:00         25          1   NORMAL\n"
        "  2026-09-26 12:00         25          1   NORMAL\n"
        "  2026-09-26 13:00         25          1   NORMAL\n"
        "  2026-09-26 14:00         45         29   ANOMALY SPIKE DETECTED\n"
        "  2026-09-26 15:00         25          3   NORMAL\n"
        "  2026-09-26 16:00         25          1   NORMAL\n"
        "  2026-09-26 17:00         25          1   NORMAL\n\n"
        "6. ANOMALY DETECTION (STATISTICAL THRESHOLDING)\n"
        "-----------------------------------------------------------------\n"
        "  Configured Min Errors  : 5\n"
        "  Configured Multiplier  : 2.0x\n"
        "  Hourly Error Baseline  : 4.10 errors/hr\n"
        "  Anomalies Flagged      : 1\n\n"
        "  DETECTED ANOMALOUS HOURS:\n"
        "    [1] Hour: 2026-09-26 14:00\n"
        "        Error Count : 29\n"
        "        Threshold   : 8.20\n"
        "        Diagnostic  : Hourly spike: error count (29) exceeded threshold (8.20) [7.1x baseline 4.10, min 5]\n"
        "========================================================================\n"
    )
    story.append(Preformatted(terminal_output, code_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("10.2 Structured Report Excerpts", h2_style))
    story.append(Paragraph("<b>JSON Report Excerpt (<code>reports/summary.json</code>):</b>", body_style))
    json_snippet = (
        '{\n'
        '  "anomaly_detection": {\n'
        '    "anomalies": [\n'
        '      {\n'
        '        "baseline_mean": 4.1,\n'
        '        "error_count": 29,\n'
        '        "hour": "2026-09-26 14:00",\n'
        '        "reason": "Hourly spike: error count (29) exceeded threshold (8.20) [7.1x baseline 4.10, min 5]",\n'
        '        "threshold": 8.2\n'
        '      }\n'
        '    ],\n'
        '    "anomalies_detected_count": 1,\n'
        '    "baseline_hourly_error_rate": 4.1\n'
        '  },\n'
        '  "busiest_hour": { "count": 45, "hour": "2026-09-26 14:00" },\n'
        '  "line_counts": { "malformed_lines": 4, "total_lines": 274, "valid_lines": 270 }\n'
        '}'
    )
    story.append(Preformatted(json_snippet, code_style))

    # =========================================================================
    # SECTION 11: TESTING APPROACH
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("11. Testing Approach", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    story.append(Paragraph(
        "LogLens utilizes Python's built-in <code>unittest</code> framework to ensure complete verification across all four functional tiers: "
        "line parsing, metric analysis, anomaly detection, and command-line execution.", body_style
    ))

    test_table_data = [
        [Paragraph("Test Module", table_header_style), Paragraph("Tests Run", table_header_style), Paragraph("Scope of Verification", table_header_style)],
        [Paragraph("<code>test_parser.py</code>", table_cell_style), Paragraph("11 tests", table_cell_style), Paragraph("Valid parsing, spaces in messages, invalid dates, unknown levels, truncated lines, streaming reader counts, malformed line sampling.", table_cell_style)],
        [Paragraph("<code>test_analyzer.py</code>", table_cell_style), Paragraph("6 tests", table_cell_style), Paragraph("Total/valid/malformed counts, severity breakdowns, service activity, busiest hour detection, top error services, dictionary conversion.", table_cell_style)],
        [Paragraph("<code>test_anomalies.py</code>", table_cell_style), Paragraph("8 tests", table_cell_style), Paragraph("Baseline calculations, normal data (zero anomalies), anomalous spikes, zero baselines with bursts, single-hour sparse baselines, parameter validation.", table_cell_style)],
        [Paragraph("<code>test_cli.py</code>", table_cell_style), Paragraph("9 tests", table_cell_style), Paragraph("CLI help flags, text analysis execution, JSON export, CSV export, missing file error (code 1), overwrite safety (code 1), invalid arguments (code 2), fallback routing.", table_cell_style)],
    ]
    test_table = Table(test_table_data, colWidths=[120, 80, 300])
    test_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B365D")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(test_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("11.1 Actual Test Execution Output", h2_style))
    test_output_snippet = (
        "$ python -m unittest discover -s tests -v\n\n"
        "test_busiest_hour_identification (test_analyzer.TestLogAnalyzer) ... ok\n"
        "test_line_counts_and_boundaries (test_analyzer.TestLogAnalyzer) ... ok\n"
        "test_service_counts_and_service_errors (test_analyzer.TestLogAnalyzer) ... ok\n"
        "test_severity_level_counts (test_analyzer.TestLogAnalyzer) ... ok\n"
        "test_to_dict_serialization (test_analyzer.TestLogAnalyzer) ... ok\n"
        "test_top_error_services_ordering (test_analyzer.TestLogAnalyzer) ... ok\n"
        "test_anomalous_spike_detected (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_configurable_threshold_tuning (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_empty_dataset (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_normal_data_no_anomalies (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_parameter_validation (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_sparse_baseline_single_hour (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_zero_baseline_with_no_errors (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_zero_baseline_with_sudden_burst (test_anomalies.TestAnomalyDetector) ... ok\n"
        "test_cli_analyze_help_flag (test_cli.TestCLI) ... ok\n"
        "test_cli_convenience_fallback_without_analyze_subcommand (test_cli.TestCLI) ... ok\n"
        "test_cli_csv_export (test_cli.TestCLI) ... ok\n"
        "test_cli_help_flag (test_cli.TestCLI) ... ok\n"
        "test_cli_invalid_parameter_values (test_cli.TestCLI) ... ok\n"
        "test_cli_json_export (test_cli.TestCLI) ... ok\n"
        "test_cli_missing_input_file (test_cli.TestCLI) ... ok\n"
        "test_cli_prevents_unsafe_input_overwrite (test_cli.TestCLI) ... ok\n"
        "test_cli_successful_text_execution (test_cli.TestCLI) ... ok\n"
        "test_all_standard_severity_levels (test_parser.TestLogParser) ... ok\n"
        "test_empty_or_blank_line (test_parser.TestLogParser) ... ok\n"
        "test_invalid_calendar_timestamp (test_parser.TestLogParser) ... ok\n"
        "test_invalid_log_level_raises_malformed (test_parser.TestLogParser) ... ok\n"
        "test_message_with_multiple_spaces_and_special_chars (test_parser.TestLogParser) ... ok\n"
        "test_truncated_lines (test_parser.TestLogParser) ... ok\n"
        "test_try_parse_line_helper (test_parser.TestLogParser) ... ok\n"
        "test_valid_line_parsing (test_parser.TestLogParser) ... ok\n"
        "test_empty_file_ingestion (test_parser.TestLogStreamReader) ... ok\n"
        "test_missing_file_raises_error (test_parser.TestLogStreamReader) ... ok\n"
        "test_streaming_ingestion_and_counts (test_parser.TestLogStreamReader) ... ok\n\n"
        "----------------------------------------------------------------------\n"
        "Ran 34 tests in 0.149s\n\n"
        "OK\n"
    )
    story.append(Preformatted(test_output_snippet, code_style))

    # =========================================================================
    # SECTION 12: CHALLENGES FACED
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("12. Challenges Faced", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    challenges = [
        ("Handling Free-Form Spaces in Log Messages",
         "A naive whitespace split (<code>str.split()</code>) divides message sentences into arbitrary tokens. This was resolved using a pre-compiled regular expression with a greedy final group (<code>(.+)</code>) and limiting string splits to 4 boundaries."),
        ("Deterministic Anomaly Baseline for Sparse / Single-Hour Logs",
         "When logs contain only one hour or have 0 historical errors, baseline multiples can lead to division-by-zero or suppressed warnings. An explicit mathematical rule was designed where single-hour and zero-baseline cases evaluate directly against <code>min_errors</code>."),
        ("Preventing Inadvertent Input File Destruction",
         "If a user accidentally specifies the input log as the output report path, opening the file in write mode would truncate the raw data before ingestion finishes. Inode/path canonicalization via <code>Path.resolve()</code> halts execution before any output file is opened."),
        ("Argparse Subcommand Duality",
         "Supporting both explicit subcommand syntax (<code>main.py analyze log.txt</code>) and natural shorthand (<code>main.py log.txt</code>) required intelligent argument vector preprocessing before invoking <code>parse_args()</code>."),
    ]

    for title, desc in challenges:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", bullet_style))

    # =========================================================================
    # SECTION 13: LEARNINGS AND KEY TAKEAWAYS
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("13. Learnings and Key Takeaways", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    learnings = [
        "<b>Power of the Standard Library:</b> Building production-quality software without third-party frameworks enhances stability, security, and portability while demonstrating deep mastery of core Python idioms.",
        "<b>Streaming Data Pipelines:</b> Employing generator patterns allows software to achieve constant-space $O(1)$ memory complexity, scaling effortlessly to large datasets.",
        "<b>Defensive Parsing Practices:</b> Real-world telemetry is inherently noisy; capturing malformed line statistics without halting execution is essential for high system availability.",
        "<b>Explainable Algorithms:</b> In operational observability, deterministic statistical rules provide actionable clarity that stochastic black-box models cannot match.",
    ]
    for item in learnings:
        story.append(Paragraph(f"• {item}", bullet_style))

    # =========================================================================
    # SECTION 14: FUTURE ENHANCEMENTS
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("14. Future Enhancements", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    enhancements = [
        "<b>Custom Format Configuration:</b> Support arbitrary formats (Apache, Nginx, Syslog) via user-defined regex templates in a local configuration file.",
        "<b>Live Log Tailing (<code>--tail</code>):</b> Integrate real-time streaming capability that continuously evaluates active log files.",
        "<b>Rolling Window Thresholding:</b> Replace top-of-the-hour buckets with 15-minute sliding windows to detect spikes crossing clock-hour boundaries.",
        "<b>Offline Interactive HTML Dashboard:</b> Add an optional export format rendering self-contained SVG/HTML charts with zero external dependencies.",
    ]
    for item in enhancements:
        story.append(Paragraph(f"• {item}", bullet_style))

    # =========================================================================
    # SECTION 15: REFERENCES
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("15. References", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

    refs = [
        "1. Python Software Foundation. <i>Python 3.13 Standard Library Documentation</i>. https://docs.python.org/3/",
        "2. Python Software Foundation. <i>PEP 557 – Data Classes</i>. https://peps.python.org/pep-0557/",
        "3. Python Software Foundation. <i>PEP 484 – Type Hints</i>. https://peps.python.org/pep-0484/",
        "4. Open Source Security Foundation (OpenSSF). <i>Best Practices for Command Line Tools</i>. https://openssf.org/",
        "5. Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). <i>Site Reliability Engineering: How Google Runs Production Systems</i>. O'Reilly Media.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, body_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf_report()
