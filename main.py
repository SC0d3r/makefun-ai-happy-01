#!/usr/bin/env python3
"""Publish entry.png as the make.fun entry image.

The source image is always ``entry.png`` stored beside this script. The
destination directory is chosen by the optional ``--output-dir`` argument,
which overrides the ``MAKEFUN_OUTPUT_DIR`` environment variable. When neither
is provided the directory is ``/output``. Missing output directories are
created automatically.

Before anything is copied, the source is checked for a known image signature:
it must start with either the PNG or the JPEG magic bytes.

After copying, the destination is checked again: it must exist, be a regular
non-empty file, and be byte-identical to the source. Both files are streamed
in fixed-size chunks so that large images never have to be loaded into memory
as a whole.

On success the output path and the number of bytes written are printed and the
process exits with status 0. Any failure prints a clear message on stderr and
exits with status 1.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import BinaryIO, Final, NoReturn

# Name of the image that lives next to this script.
SOURCE_NAME: Final[str] = "entry.png"

# Name of the environment variable that selects the destination directory.
OUTPUT_ENV_VAR: Final[str] = "MAKEFUN_OUTPUT_DIR"

# Fallback destination used when no argument and no variable are provided.
DEFAULT_OUTPUT_DIR: Final[str] = "/output"

# Read/write block size for streaming copies and comparisons.
CHUNK_SIZE: Final[int] = 1024 * 1024

# Magic bytes accepted for the source image.
PNG_SIGNATURE: Final[bytes] = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE: Final[bytes] = b"\xff\xd8\xff"
SIGNATURE_SIZE: Final[int] = max(len(PNG_SIGNATURE), len(JPEG_SIGNATURE))


def fail(message: str) -> NoReturn:
    """Print a fatal error message on stderr and terminate with status 1."""
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def resolve_source() -> Path:
    """Return the absolute path of entry.png beside this script.

    ``Path(__file__).resolve()`` makes the lookup independent of the current
    working directory, so the script can be started from anywhere.
    """
    source = Path(__file__).resolve().parent / SOURCE_NAME
    if not source.is_file():
        fail(f"source image not found: {source} (expected {SOURCE_NAME} beside main.py)")
    return source


def validate_image_signature(source: Path) -> None:
    """Require the source to begin with a PNG or JPEG magic number.

    Only the first few bytes are read, so this check is cheap even for large
    files. It guards against accidentally publishing a renamed or truncated
    file that is not an image at all.
    """
    try:
        with source.open("rb") as reader:
            header = reader.read(SIGNATURE_SIZE)
    except OSError as exc:
        fail(f"cannot read source image {source}: {exc}")

    if header.startswith(PNG_SIGNATURE) or header.startswith(JPEG_SIGNATURE):
        return

    fail(f"source is not a PNG or JPEG image: {source}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments, keeping the environment as fallback."""
    parser = argparse.ArgumentParser(
        description="Copy entry.png into the make.fun output directory.",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=None,
        help=(
            "destination directory; overrides the MAKEFUN_OUTPUT_DIR "
            f"environment variable and defaults to {DEFAULT_OUTPUT_DIR}"
        ),
    )
    return parser.parse_args(argv)


def resolve_output_dir(cli_output_dir: str | None) -> Path:
    """Return the destination directory for this run.

    The command line argument has the highest priority, then the environment
    variable. An empty or whitespace-only value is treated as unset so that
    container environments which export empty variables still work.
    """
    if cli_output_dir and cli_output_dir.strip():
        return Path(cli_output_dir).expanduser()

    configured = os.environ.get(OUTPUT_ENV_VAR, "").strip()
    return Path(configured or DEFAULT_OUTPUT_DIR).expanduser()


def ensure_directory(directory: Path) -> None:
    """Create ``directory`` (and parents) if needed and require a directory."""
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"cannot create output directory {directory}: {exc}")

    if not directory.is_dir():
        fail(f"output path is not a directory: {directory}")


def stream_copy(source: Path, destination: Path) -> int:
    """Copy ``source`` to ``destination`` in chunks and return bytes written.

    The file is opened with ``wb`` so an existing destination is replaced
    completely rather than appended to. ``fsync`` makes sure the data has
    reached the file before the verification step reads it back.
    """
    written = 0
    try:
        with source.open("rb") as reader, destination.open("wb") as writer:
            written = transfer(reader, writer)
            writer.flush()
            os.fsync(writer.fileno())
    except OSError as exc:
        fail(f"cannot copy {source} to {destination}: {exc}")
    return written


def transfer(reader: BinaryIO, writer: BinaryIO) -> int:
    """Stream every byte from ``reader`` into ``writer``; return the count."""
    total = 0
    while chunk := reader.read(CHUNK_SIZE):
        writer.write(chunk)
        total += len(chunk)
    return total


def files_identical(first: Path, second: Path) -> bool:
    """Compare two files chunk by chunk without loading either one whole."""
    with first.open("rb") as left, second.open("rb") as right:
        while True:
            left_chunk = left.read(CHUNK_SIZE)
            right_chunk = right.read(CHUNK_SIZE)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def verify_copy(source: Path, destination: Path, written: int) -> int:
    """Validate the copied file and return its verified size in bytes."""
    if not destination.is_file():
        fail(f"copied file is missing: {destination}")

    try:
        size = destination.stat().st_size
    except OSError as exc:
        fail(f"cannot inspect copied file {destination}: {exc}")

    if size == 0:
        fail(f"copied file is empty: {destination}")

    if size != written:
        fail(f"copied file has {size} bytes but {written} were written: {destination}")

    try:
        identical = files_identical(source, destination)
    except OSError as exc:
        fail(f"cannot verify copied file {destination}: {exc}")

    if not identical:
        fail(f"copy is not byte-identical: {destination} does not match {source}")

    return size


def main(argv: Sequence[str] | None = None) -> int:
    """Run the copy-and-verify workflow; return the process exit status."""
    args = parse_args(argv)

    source = resolve_source()
    validate_image_signature(source)

    output_dir = resolve_output_dir(args.output_dir)
    destination = output_dir / SOURCE_NAME

    ensure_directory(output_dir)
    written = stream_copy(source, destination)
    size = verify_copy(source, destination, written)

    print(f"output: {destination}")
    print(f"bytes written: {size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
