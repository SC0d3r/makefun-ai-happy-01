#!/usr/bin/env python3
"""Publish entry.png as the make.fun entry image.

The image is copied byte for byte into MAKEFUN_OUTPUT_DIR when that
environment variable is set, otherwise into /output.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import NoReturn

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"
CHUNK_SIZE = 1024 * 1024


def fail(message: str) -> NoReturn:
    """Report a fatal error on stderr and exit with a non-zero status."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def files_identical(first: Path, second: Path) -> bool:
    """Compare two files byte by byte without loading either one whole."""
    with first.open("rb") as left, second.open("rb") as right:
        while True:
            left_chunk = left.read(CHUNK_SIZE)
            right_chunk = right.read(CHUNK_SIZE)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def main() -> int:
    source = Path(__file__).resolve().parent / SOURCE_NAME
    if not source.is_file():
        fail(f"source image not found: {source} (expected {SOURCE_NAME} beside main.py)")

    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_OUTPUT_DIR).expanduser()
    destination = output_dir / SOURCE_NAME

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"cannot create output directory {output_dir}: {exc}")

    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        fail(f"cannot copy {source} to {destination}: {exc}")

    try:
        size = destination.stat().st_size
    except OSError as exc:
        fail(f"cannot inspect copied file {destination}: {exc}")

    if size == 0:
        fail(f"copied file is empty: {destination}")

    try:
        identical = files_identical(source, destination)
    except OSError as exc:
        fail(f"cannot verify copied file {destination}: {exc}")

    if not identical:
        fail(f"copy is not byte-identical: {destination} does not match {source}")

    print(f"output: {destination}")
    print(f"bytes written: {size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
