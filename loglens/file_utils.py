"""File and filesystem utility helpers for LogLens."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union


class LogLensFileError(Exception):
    """Base exception for file handling errors in LogLens."""


class InputFileNotFoundError(LogLensFileError):
    """Raised when the specified input log file does not exist."""


class UnreadableFileError(LogLensFileError):
    """Raised when the input log file cannot be read due to permissions or corruption."""


class UnsafeOverwriteError(LogLensFileError):
    """Raised when an output report path would overwrite the input log file."""


def validate_input_file(path_str_or_path: Union[str, Path]) -> Path:
    """Validates that the input path exists, is a file, and is readable.

    Args:
        path_str_or_path: The file path to inspect.

    Returns:
        The resolved Path object.

    Raises:
        InputFileNotFoundError: If the path does not exist or is a directory.
        UnreadableFileError: If the file lacks read permissions.
    """
    path = Path(path_str_or_path).expanduser()

    if not path.exists():
        raise InputFileNotFoundError(f"Input log file not found: '{path}'")

    if not path.is_file():
        raise InputFileNotFoundError(f"Input path is not a regular file: '{path}'")

    if not os.access(path, os.R_OK):
        raise UnreadableFileError(f"Cannot read log file (permission denied): '{path}'")

    return path.resolve()


def ensure_output_directory(output_path_str_or_path: Union[str, Path]) -> Path:
    """Ensures parent directory for the output file exists, creating it if needed.

    Args:
        output_path_str_or_path: The intended output file path.

    Returns:
        The resolved Path object for the target output file.

    Raises:
        LogLensFileError: If the parent directory cannot be created.
    """
    path = Path(output_path_str_or_path).expanduser().resolve()
    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        raise LogLensFileError(f"Failed to create output directory '{parent}': {err}") from err
    return path


def check_safe_output_path(input_file: Path, output_file: Path) -> None:
    """Verifies that the output file will not overwrite the source input log.

    Args:
        input_file: Resolved input log file path.
        output_file: Resolved destination report path.

    Raises:
        UnsafeOverwriteError: If both paths resolve to the same filesystem location.
    """
    if input_file.resolve() == output_file.resolve():
        raise UnsafeOverwriteError(
            f"Unsafe operation: output destination '{output_file}' cannot be identical to input log file."
        )
