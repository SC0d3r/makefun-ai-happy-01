# make.fun art entry: ai-happy-01

`main.py` publishes `entry.png` as the make.fun entry image. The source is
always the `entry.png` file stored beside `main.py`; the script never modifies
it.

## What it does

1. Locates `entry.png` next to `main.py`, regardless of the current working
   directory.
2. Checks that the source starts with a PNG or JPEG signature.
3. Chooses the output directory, creating it (including parents) if needed.
4. Copies the source to `<output-dir>/entry.png` byte for byte, streaming in
   1 MiB chunks.
5. Verifies that the destination exists, is a regular non-empty file, has the
   expected size, and is byte-identical to the source (again streamed in
   chunks).
6. Prints the output path and the number of bytes written.

The script uses only the Python standard library and targets Python 3.13.

## Choosing the output directory

The destination is resolved in this order:

1. `--output-dir DIR` on the command line.
2. The `MAKEFUN_OUTPUT_DIR` environment variable, when set to a non-empty
   value.
3. `/output` when neither of the above is provided (an empty or
   whitespace-only `MAKEFUN_OUTPUT_DIR` counts as unset).

The output file is always named `entry.png`, even if the source has a different
name.

## Usage

```text
python3 main.py [--output-dir DIR]
```

Show the built-in help (including `--output-dir`) with:

```text
python3 main.py --help
```

## Exit codes

| Code | Meaning |
| ---- | ------- |
| `0`  | The copy succeeded and was verified byte-identical. |
| `1`  | The source is missing or is not a PNG/JPEG, the output directory cannot be created, the copy fails, or the destination is missing, empty, or different. A clear message is printed on stderr. |
| `2`  | Invalid command line usage, such as an unknown option (reported by `argparse`). |

## Running locally

From this repository:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This creates `out/` if necessary and copies `entry.png` into it. Expected
output:

```text
output: out/entry.png
bytes written: 466518
```

To use the command line flag instead of the environment variable:

```sh
python3 main.py --output-dir out
```

The flag wins when both are present:

```sh
MAKEFUN_OUTPUT_DIR=ignored python3 main.py --output-dir out
```

`out/entry.png` will be an exact, verified copy of the submitted image.
