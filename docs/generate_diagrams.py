"""Generates legible, high-resolution design diagrams for the LogLens project report.

Diagrams produced:
1. System Architecture Diagram (docs/architecture.png)
2. Ingestion & Analysis Workflow Diagram (docs/workflow.png)
3. Use Case Diagram (docs/use_case.png)
4. Sequence Diagram for Log Analysis (docs/sequence.png)
5. Class and Component Diagram (docs/class_diagram.png)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def create_architecture_diagram():
    """Generates the System Architecture Diagram."""
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    # Title
    ax.text(5, 5.8, "LogLens System Architecture", ha="center", va="center", fontsize=16, fontweight="bold", color="#1B365D")

    # Layer 1: CLI Interface & Ingestion
    ax.add_patch(patches.FancyBboxPatch((0.6, 3.8), 2.5, 1.4, boxstyle="round,pad=0.08", facecolor="#EBF8FF", edgecolor="#3182CE", linewidth=2))
    ax.text(1.85, 4.8, "CLI Interface Layer\n(main.py / cli.py)", ha="center", va="center", fontsize=10, fontweight="bold", color="#2B6CB0")
    ax.text(1.85, 4.15, "- argparse CLI flags\n- Input path validation\n- Exit code routing", ha="center", va="center", fontsize=8, color="#2D3748")

    # Layer 2: Ingestion & Validation
    ax.add_patch(patches.FancyBboxPatch((3.75, 3.8), 2.5, 1.4, boxstyle="round,pad=0.08", facecolor="#E6FFFA", edgecolor="#319795", linewidth=2))
    ax.text(5.0, 4.8, "Ingestion & Validation\n(parser.py)", ha="center", va="center", fontsize=10, fontweight="bold", color="#234E52")
    ax.text(5.0, 4.15, "- LogStreamReader (O(1) RAM)\n- Regex tokenization\n- Calendar & Level validation", ha="center", va="center", fontsize=8, color="#2D3748")

    # Layer 3: Processing & Detection
    ax.add_patch(patches.FancyBboxPatch((6.9, 3.8), 2.5, 1.4, boxstyle="round,pad=0.08", facecolor="#FEFCBF", edgecolor="#D69E2E", linewidth=2))
    ax.text(8.15, 4.8, "Analysis & Anomaly Engine\n(analyzer.py / anomalies.py)", ha="center", va="center", fontsize=10, fontweight="bold", color="#744210")
    ax.text(8.15, 4.15, "- Single-pass metrics\n- Hourly error buckets\n- Deterministic spike rule", ha="center", va="center", fontsize=8, color="#2D3748")

    # Core Models & Data Layer
    ax.add_patch(patches.FancyBboxPatch((2.0, 2.0), 6.0, 1.2, boxstyle="round,pad=0.08", facecolor="#EDF2F7", edgecolor="#4A5568", linewidth=2))
    ax.text(5.0, 2.85, "Domain Model Layer (models.py)", ha="center", va="center", fontsize=11, fontweight="bold", color="#1A202C")
    ax.text(5.0, 2.35, "LogRecord (frozen dataclass)  |  HourlyStats  |  AnomalyResult  |  AnalysisSummary", ha="center", va="center", fontsize=9, color="#4A5568")

    # Output & Reporting Layer
    ax.add_patch(patches.FancyBboxPatch((1.0, 0.3), 8.0, 1.2, boxstyle="round,pad=0.08", facecolor="#FAF5FF", edgecolor="#805AD5", linewidth=2))
    ax.text(5.0, 1.15, "Reporting & Presentation Layer (reporter.py)", ha="center", va="center", fontsize=11, fontweight="bold", color="#553C9A")
    ax.text(5.0, 0.65, "TextReporter (Terminal ANSI table)   |   JsonReporter (Deterministic JSON)   |   CsvReporter (Multi-section tabular)", ha="center", va="center", fontsize=9, color="#4A5568")

    # Connecting Arrows
    arrow_props = dict(facecolor="#4A5568", edgecolor="#4A5568", arrowstyle="->", lw=1.5)
    ax.annotate("", xy=(3.75, 4.5), xytext=(3.1, 4.5), arrowprops=arrow_props)
    ax.annotate("", xy=(6.9, 4.5), xytext=(6.25, 4.5), arrowprops=arrow_props)
    ax.annotate("", xy=(5.0, 3.2), xytext=(5.0, 3.8), arrowprops=arrow_props)
    ax.annotate("", xy=(5.0, 1.5), xytext=(5.0, 2.0), arrowprops=arrow_props)

    plt.tight_layout()
    output_path = DOCS_DIR / "architecture.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def create_workflow_diagram():
    """Generates the Ingestion & Analysis Workflow Diagram."""
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    ax.text(5, 4.6, "LogLens End-to-End Processing Workflow", ha="center", va="center", fontsize=15, fontweight="bold", color="#1B365D")

    steps = [
        ("Input Log\n(UTF-8)", 1.0, "#E2E8F0", "#4A5568"),
        ("Streaming\nReader", 2.8, "#BEE3F8", "#2B6CB0"),
        ("Validation &\nTokenization", 4.6, "#C6F6D5", "#22543D"),
        ("Metric Aggregation &\nAnomaly Detection", 6.8, "#FEFCBF", "#744210"),
        ("Deterministic\nReport Export", 9.0, "#E9D8FD", "#553C9A"),
    ]

    for label, x, fcol, ecol in steps:
        ax.add_patch(patches.FancyBboxPatch((x - 0.75, 2.0), 1.5, 1.5, boxstyle="round,pad=0.08", facecolor=fcol, edgecolor=ecol, linewidth=2))
        ax.text(x, 2.75, label, ha="center", va="center", fontsize=8.5, fontweight="bold", color=ecol)

    # Arrows between steps
    arrow_props = dict(facecolor="#4A5568", edgecolor="#4A5568", arrowstyle="->", lw=2)
    ax.annotate("", xy=(1.95, 2.75), xytext=(1.75, 2.75), arrowprops=arrow_props)
    ax.annotate("", xy=(3.75, 2.75), xytext=(3.55, 2.75), arrowprops=arrow_props)
    ax.annotate("", xy=(5.95, 2.75), xytext=(5.35, 2.75), arrowprops=arrow_props)
    ax.annotate("", xy=(8.15, 2.75), xytext=(7.55, 2.75), arrowprops=arrow_props)

    # Decision branches / callouts
    ax.text(4.6, 1.3, "[Valid Line] -> Yield LogRecord\n[Malformed] -> Increment malformed_lines & Continue",
            ha="center", va="center", fontsize=8, style="italic", bbox=dict(boxstyle="square,pad=0.4", facecolor="#FFF5F5", edgecolor="#E53E3E"))
    ax.annotate("", xy=(4.6, 2.0), xytext=(4.6, 1.6), arrowprops=dict(facecolor="#E53E3E", edgecolor="#E53E3E", arrowstyle="<-", lw=1))

    plt.tight_layout()
    output_path = DOCS_DIR / "workflow.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def create_use_case_diagram():
    """Generates the System Use Case Diagram."""
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 5.5)
    ax.axis("off")

    ax.text(4.5, 5.1, "LogLens System Use Case Diagram", ha="center", va="center", fontsize=15, fontweight="bold", color="#1B365D")

    # Actor: DevOps Engineer / Analyst
    ax.plot([1.2, 1.2], [3.3, 2.7], color="#2B6CB0", lw=2.5) # body
    circle = patches.Circle((1.2, 3.6), 0.25, facecolor="#BEE3F8", edgecolor="#2B6CB0", lw=2) # head
    ax.add_patch(circle)
    ax.plot([0.8, 1.6], [3.0, 3.0], color="#2B6CB0", lw=2.5) # arms
    ax.plot([1.2, 0.9], [2.7, 2.2], color="#2B6CB0", lw=2.5) # leg L
    ax.plot([1.2, 1.5], [2.7, 2.2], color="#2B6CB0", lw=2.5) # leg R
    ax.text(1.2, 1.8, "DevOps Engineer /\nSystem Admin", ha="center", va="center", fontsize=9, fontweight="bold", color="#1A202C")

    # Boundary Box
    ax.add_patch(patches.Rectangle((2.8, 0.4), 5.8, 4.4, facecolor="#F7FAFC", edgecolor="#CBD5E0", linestyle="--", linewidth=1.5))
    ax.text(5.7, 4.5, "LogLens Application Boundary", ha="center", va="center", fontsize=10, style="italic", color="#718096")

    # Use cases
    use_cases = [
        ("UC-1: Ingest & Validate Log File", 3.8),
        ("UC-2: Detect Hourly Error Spikes", 3.0),
        ("UC-3: View Terminal Operational Summary", 2.2),
        ("UC-4: Export JSON Audit Report", 1.4),
        ("UC-5: Export Tabular CSV Report", 0.7),
    ]

    for uc_text, y_pos in use_cases:
        ellipse = patches.Ellipse((5.7, y_pos), 4.2, 0.55, facecolor="#EBF8FF", edgecolor="#3182CE", lw=1.5)
        ax.add_patch(ellipse)
        ax.text(5.7, y_pos, uc_text, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#2B6CB0")
        # Line from actor
        ax.plot([1.6, 3.6], [3.1, y_pos], color="#718096", lw=1.2)

    plt.tight_layout()
    output_path = DOCS_DIR / "use_case.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def create_sequence_diagram():
    """Generates the Sequence Diagram for Log Analysis."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5, 5.7, "Sequence Diagram: Log Analysis & Reporting Execution", ha="center", va="center", fontsize=15, fontweight="bold", color="#1B365D")

    lifelines = [
        ("User / CLI", 1.2),
        ("LogStreamReader", 3.2),
        ("LogParser", 5.2),
        ("LogAnalyzer", 7.2),
        ("Reporter", 9.0),
    ]

    for name, x in lifelines:
        ax.add_patch(patches.FancyBboxPatch((x - 0.75, 4.9), 1.5, 0.45, boxstyle="round,pad=0.04", facecolor="#E2E8F0", edgecolor="#4A5568", lw=1.5))
        ax.text(x, 5.12, name, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#2D3748")
        ax.plot([x, x], [0.6, 4.9], color="#CBD5E0", linestyle="--", lw=1.2)

    # Sequence steps (arrows and labels)
    steps = [
        (1.2, 3.2, 4.4, "1. run_analyze(logfile, format, thresholds)", "#2B6CB0"),
        (3.2, 5.2, 3.8, "2. parse_line(raw_line, line_num)", "#234E52"),
        (5.2, 3.2, 3.3, "3. return LogRecord or error reason", "#234E52"),
        (3.2, 7.2, 2.7, "4. stream records to analyzer", "#744210"),
        (7.2, 7.2, 2.1, "5. detect_anomalies(hourly_errors)", "#D69E2E"),
        (7.2, 9.0, 1.5, "6. create summary & render report", "#553C9A"),
        (9.0, 1.2, 0.9, "7. terminal output / saved file path", "#2B6CB0"),
    ]

    for x1, x2, y, msg, col in steps:
        if x1 == x2: # self call
            ax.plot([x1, x1 + 0.5, x1 + 0.5, x1], [y, y, y - 0.25, y - 0.25], color=col, lw=1.5)
            ax.text(x1 + 0.6, y - 0.12, msg, va="center", fontsize=8, color=col)
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(facecolor=col, edgecolor=col, arrowstyle="->", lw=1.5))
            ax.text((x1 + x2) / 2, y + 0.12, msg, ha="center", va="bottom", fontsize=8, color=col)

    plt.tight_layout()
    output_path = DOCS_DIR / "sequence.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def create_class_diagram():
    """Generates the Class & Component Diagram."""
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    ax.text(5, 6.1, "LogLens Class & Component Architecture", ha="center", va="center", fontsize=15, fontweight="bold", color="#1B365D")

    # LogRecord Box
    ax.add_patch(patches.FancyBboxPatch((0.6, 3.8), 2.6, 1.9, boxstyle="round,pad=0.06", facecolor="#EBF8FF", edgecolor="#3182CE", lw=1.5))
    ax.text(1.9, 5.45, "<<dataclass>>\nLogRecord", ha="center", va="center", fontsize=9, fontweight="bold", color="#2B6CB0")
    ax.plot([0.6, 3.2], [5.1, 5.1], color="#3182CE", lw=1)
    ax.text(0.7, 4.55, "+ timestamp: datetime\n+ level: str\n+ service: str\n+ message: str\n+ line_number: int", fontsize=7.5, color="#2D3748")
    ax.plot([0.6, 3.2], [4.15, 4.15], color="#3182CE", lw=1)
    ax.text(0.7, 3.95, "+ hour_key() -> str\n+ is_error() -> bool", fontsize=7.5, color="#2D3748")

    # AnalysisSummary Box
    ax.add_patch(patches.FancyBboxPatch((3.7, 3.4), 2.7, 2.3, boxstyle="round,pad=0.06", facecolor="#FEFCBF", edgecolor="#D69E2E", lw=1.5))
    ax.text(5.05, 5.45, "<<dataclass>>\nAnalysisSummary", ha="center", va="center", fontsize=9, fontweight="bold", color="#744210")
    ax.plot([3.7, 6.4], [5.1, 5.1], color="#D69E2E", lw=1)
    ax.text(3.8, 4.3, "+ total_lines: int\n+ valid_lines: int\n+ malformed_lines: int\n+ level_counts: dict\n+ service_counts: dict\n+ hourly_stats: dict\n+ anomalies: list", fontsize=7.5, color="#2D3748")
    ax.plot([3.7, 6.4], [3.75, 3.75], color="#D69E2E", lw=1)
    ax.text(3.8, 3.55, "+ to_dict() -> dict", fontsize=7.5, color="#2D3748")

    # AnomalyDetector Box
    ax.add_patch(patches.FancyBboxPatch((6.9, 3.8), 2.6, 1.9, boxstyle="round,pad=0.06", facecolor="#FED7D7", edgecolor="#E53E3E", lw=1.5))
    ax.text(8.2, 5.45, "AnomalyDetector", ha="center", va="center", fontsize=9, fontweight="bold", color="#9B2C2C")
    ax.plot([6.9, 9.5], [5.1, 5.1], color="#E53E3E", lw=1)
    ax.text(7.0, 4.6, "+ min_errors: int\n+ multiplier: float", fontsize=7.5, color="#2D3748")
    ax.plot([6.9, 9.5], [4.25, 4.25], color="#E53E3E", lw=1)
    ax.text(7.0, 3.95, "+ detect_anomalies(hours)\n  -> (mean, anomalies)", fontsize=7.5, color="#2D3748")

    # LogStreamReader & LogParser
    ax.add_patch(patches.FancyBboxPatch((0.6, 0.8), 2.6, 2.0, boxstyle="round,pad=0.06", facecolor="#E6FFFA", edgecolor="#319795", lw=1.5))
    ax.text(1.9, 2.55, "LogStreamReader", ha="center", va="center", fontsize=9, fontweight="bold", color="#234E52")
    ax.plot([0.6, 3.2], [2.25, 2.25], color="#319795", lw=1)
    ax.text(0.7, 1.6, "+ file_path: Path\n+ total_lines: int\n+ valid_lines: int\n+ malformed_lines: int", fontsize=7.5, color="#2D3748")
    ax.plot([0.6, 3.2], [1.15, 1.15], color="#319795", lw=1)
    ax.text(0.7, 0.95, "+ stream_records() -> Gen", fontsize=7.5, color="#2D3748")

    # LogAnalyzer
    ax.add_patch(patches.FancyBboxPatch((3.7, 0.8), 2.7, 2.0, boxstyle="round,pad=0.06", facecolor="#FAF5FF", edgecolor="#805AD5", lw=1.5))
    ax.text(5.05, 2.55, "LogAnalyzer", ha="center", va="center", fontsize=9, fontweight="bold", color="#553C9A")
    ax.plot([3.7, 6.4], [2.25, 2.25], color="#805AD5", lw=1)
    ax.text(3.8, 1.65, "+ min_errors: int\n+ multiplier: float\n+ detector: AnomalyDetector", fontsize=7.5, color="#2D3748")
    ax.plot([3.7, 6.4], [1.25, 1.25], color="#805AD5", lw=1)
    ax.text(3.8, 0.95, "+ analyze_stream(reader)\n+ analyze_records(recs)", fontsize=7.5, color="#2D3748")

    # Reporters
    ax.add_patch(patches.FancyBboxPatch((6.9, 0.8), 2.6, 2.0, boxstyle="round,pad=0.06", facecolor="#EDF2F7", edgecolor="#4A5568", lw=1.5))
    ax.text(8.2, 2.55, "Reporters", ha="center", va="center", fontsize=9, fontweight="bold", color="#1A202C")
    ax.plot([6.9, 9.5], [2.25, 2.25], color="#4A5568", lw=1)
    ax.text(7.0, 1.6, "TextReporter\nJsonReporter\nCsvReporter", fontsize=8, color="#2D3748")
    ax.plot([6.9, 9.5], [1.15, 1.15], color="#4A5568", lw=1)
    ax.text(7.0, 0.95, "+ render() -> str\n+ export(path) -> Path", fontsize=7.5, color="#2D3748")

    # Connections
    arrow_props = dict(facecolor="#4A5568", edgecolor="#4A5568", arrowstyle="->", lw=1.2)
    ax.annotate("", xy=(1.9, 3.8), xytext=(1.9, 2.8), arrowprops=arrow_props)
    ax.annotate("", xy=(3.7, 1.8), xytext=(3.2, 1.8), arrowprops=arrow_props)
    ax.annotate("", xy=(5.05, 3.4), xytext=(5.05, 2.8), arrowprops=arrow_props)
    ax.annotate("", xy=(6.9, 4.75), xytext=(6.4, 4.75), arrowprops=arrow_props)
    ax.annotate("", xy=(6.9, 1.8), xytext=(6.4, 1.8), arrowprops=arrow_props)

    plt.tight_layout()
    output_path = DOCS_DIR / "class_diagram.png"
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    create_architecture_diagram()
    create_workflow_diagram()
    create_use_case_diagram()
    create_sequence_diagram()
    create_class_diagram()
    print("All 5 design diagrams successfully generated!")
