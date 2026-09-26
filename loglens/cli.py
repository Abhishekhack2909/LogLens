"""Command-line interface (CLI) for LogLens."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .analyzer import LogAnalyzer
from .file_utils import (
    InputFileNotFoundError,
    LogLensFileError,
    UnreadableFileError,
    UnsafeOverwriteError,
)
from .parser import LogStreamReader
from .reporter import CsvReporter, JsonReporter, TextReporter


def build_parser() -> argparse.ArgumentParser:
    """Builds and configures the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="loglens",
        description="LogLens: A Python-Based Server Log Analyzer and Anomaly Detector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py analyze sample_logs/server.log\n"
            "  python main.py analyze sample_logs/server.log --format json --output reports/summary.json\n"
            "  python main.py analyze sample_logs/server.log --format csv --output reports/summary.csv\n"
            "  python main.py analyze sample_logs/server.log --min-errors 5 --multiplier 2.0\n"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="LogLens 1.0.0",
        help="Show program version and exit.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="Commands",
        description="Valid LogLens subcommands",
    )

    # analyze subcommand
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a log file, generate metrics, and detect anomalies.",
        description="Reads a structured log file, performs hourly anomaly detection, and formats reports.",
    )

    analyze_parser.add_argument(
        "logfile",
        type=str,
        help="Path to the plain-text application log file (UTF-8 encoded).",
    )

    analyze_parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Report presentation format (default: %(default)s).",
    )

    analyze_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Destination path for exported report file. If omitted for text, prints to stdout.",
    )

    analyze_parser.add_argument(
        "--min-errors",
        type=int,
        default=5,
        help="Minimum error count in an hour required to trigger an anomaly (default: %(default)s).",
    )

    analyze_parser.add_argument(
        "--multiplier",
        type=float,
        default=2.0,
        help="Multiplier against hourly baseline required to trigger an anomaly (default: %(default)s).",
    )

    analyze_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress console stdout summary when exporting report to file.",
    )

    return parser


def run_analyze(args: argparse.Namespace) -> int:
    """Executes log analysis based on parsed command line arguments.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    if args.min_errors < 1:
        print(f"Error: --min-errors must be an integer >= 1 (got {args.min_errors})", file=sys.stderr)
        return 2

    if args.multiplier <= 0.0:
        print(f"Error: --multiplier must be a positive float > 0.0 (got {args.multiplier})", file=sys.stderr)
        return 2

    log_path = Path(args.logfile)

    try:
        reader = LogStreamReader(log_path)
    except InputFileNotFoundError as err:
        print(f"File Error: {err}", file=sys.stderr)
        return 1
    except UnreadableFileError as err:
        print(f"Access Error: {err}", file=sys.stderr)
        return 1
    except LogLensFileError as err:
        print(f"Filesystem Error: {err}", file=sys.stderr)
        return 1

    analyzer = LogAnalyzer(min_errors=args.min_errors, multiplier=args.multiplier)

    try:
        summary = analyzer.analyze_stream(reader)
    except UnreadableFileError as err:
        print(f"Ingestion Error: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Processing Error: Unexpected error during analysis: {err}", file=sys.stderr)
        return 3

    text_reporter = TextReporter(summary)

    try:
        if args.format == "text":
            if args.output:
                out_path = Path(args.output)
                # Ensure safety check against overwriting input
                from .file_utils import check_safe_output_path, ensure_output_directory
                dest = ensure_output_directory(out_path)
                check_safe_output_path(reader.file_path, dest)
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(text_reporter.render())
                if not args.quiet:
                    print(f"Text report successfully saved to: {dest}")
            else:
                text_reporter.print_report()

        elif args.format == "json":
            json_reporter = JsonReporter(summary)
            if args.output:
                saved_path = json_reporter.export(args.output)
                if not args.quiet:
                    text_reporter.print_report()
                    print(f"\n[+] JSON report successfully exported to: {saved_path}")
            else:
                print(json_reporter.render())

        elif args.format == "csv":
            csv_reporter = CsvReporter(summary)
            if args.output:
                saved_path = csv_reporter.export(args.output)
                if not args.quiet:
                    text_reporter.print_report()
                    print(f"\n[+] CSV report successfully exported to: {saved_path}")
            else:
                print(csv_reporter.render(), end="")

    except UnsafeOverwriteError as err:
        print(f"Security/Overwrite Error: {err}", file=sys.stderr)
        return 1
    except LogLensFileError as err:
        print(f"Export File Error: {err}", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"IO Error writing report: {err}", file=sys.stderr)
        return 1

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main CLI entrypoint.

    Args:
        argv: Optional argument sequence (defaults to sys.argv[1:]).

    Returns:
        Exit status code.
    """
    if argv is None:
        argv = sys.argv[1:]

    # Fallback convenience: If the first positional argument is not a command or flag,
    # prepend 'analyze' to sys.argv so `python main.py sample.log` works seamlessly.
    normalized_argv = list(argv)
    if normalized_argv and not normalized_argv[0].startswith("-") and normalized_argv[0] != "analyze":
        normalized_argv.insert(0, "analyze")

    parser = build_parser()

    if not normalized_argv:
        parser.print_help()
        return 0

    args = parser.parse_args(normalized_argv)

    if args.command == "analyze":
        return run_analyze(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
