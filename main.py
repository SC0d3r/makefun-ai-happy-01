#!/usr/bin/env python3
"""Copy the entry image beside this script to the configured output directory."""

from __future__ import annotations

import filecmp
import os
import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = Path("/output")


def fail(message: str) -> None:
    """Print a clear error and exit with a non-zero status."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    source = Path(__file__).resolve().with_name(SOURCE_NAME)

    if not source.is_file():
        fail(f"source image entry.png not found at {source}")

    configured_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    output_dir = (
        Path(configured_dir)
        if configured_dir and configured_dir.strip()
        else DEFAULT_OUTPUT_DIR
    )

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"could not create output directory {output_dir}: {exc}")

    destination = output_dir / SOURCE_NAME

    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        fail(f"could not copy {source} to {destination}: {exc}")

    try:
        size = destination.stat().st_size
    except OSError as exc:
        fail(f"copied file is missing or unreadable at {destination}: {exc}")

    if size == 0:
        fail(f"copied file is empty: {destination}")

    if not filecmp.cmp(source, destination, shallow=False):
        fail(f"copied file is not byte-identical to the source: {destination}")

    print(f"output: {destination}")
    print(f"bytes written: {size}")


if __name__ == "__main__":
    main()
