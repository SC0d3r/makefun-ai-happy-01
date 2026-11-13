# make.fun art entry: ai-happy-01

`main.py` publishes `entry.png` as the entry image. It looks for `entry.png`
beside itself, copies it byte for byte into the directory named by
`MAKEFUN_OUTPUT_DIR` (or `/output` when that variable is unset or empty),
creating the directory if needed, and prints the output path and the number of
bytes written.

The script fails with a clear message on stderr and exit status 1 when:

- the source image is missing;
- the copied file is empty; or
- the copy is not byte-identical to the source.

It also fails with a clear message if the output directory cannot be created or
the copy cannot be written. The source image is only read, never modified. On
success it exits with status 0.

It is written for Python 3.13 and uses only the standard library.

Run it locally:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

The output looks like:

    output: out/entry.png
    bytes written: 466518

`out/entry.png` will be an exact copy of the submitted image.
