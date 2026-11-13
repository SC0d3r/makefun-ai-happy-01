# make.fun art entry: ai-happy-01

`main.py` publishes `entry.png` by copying the image beside the script to an
output directory. The source image is never modified.

## Behavior

1. Locate `entry.png` in the same directory as `main.py`, independent of the
   current working directory.
2. Use the directory named by `MAKEFUN_OUTPUT_DIR` when that variable contains
   a non-whitespace value. Otherwise use `/output`.
3. Create the output directory, including any missing parents.
4. Copy the source to `<output-dir>/entry.png` byte for byte.
5. Verify that the copied file exists, is non-empty, and is byte-identical to
   the source.
6. Print the output path and the number of bytes written.

The script uses only the Python standard library and targets Python 3.13.

## Usage

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The script takes no command-line arguments. A relative
`MAKEFUN_OUTPUT_DIR` is resolved from the current working directory.

With `MAKEFUN_OUTPUT_DIR` unset, empty, or whitespace-only, the destination is
`/output/entry.png`.

## Errors and exit status

The script exits with status `1` and prints a clear error to stderr when:

- the source image is missing;
- the output directory cannot be created or the copy fails;
- the copied file is missing or empty;
- the copied file is not byte-identical to the source.

## Local verification

From this repository:

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Expected output:

```text
output: out/entry.png
bytes written: 466518
```

Verify the copy with:

```sh
cmp entry.png out/entry.png
```

A successful `cmp` run confirms that `out/entry.png` is identical to
`entry.png`.
