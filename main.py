#!/usr/bin/env python3
"""Entry program for make.fun's news-image-20261123 bounty,
"Sum up 23 November's world news in one image".

Publishes the committed entry.png as /output/entry.png. The image is
a one-page front page of the world news of Monday 23 November 2026,
compiled from wire reports published that day.

The publish is atomic and self-checking: the bytes are first written
to a scratch file inside /output, flushed to disk, then renamed over
the target path, so the target never holds a partial file. The
published file is then hashed and compared with the source; a
mismatch makes the program exit with an error.

Standard library only, no network. Deterministic: the program runs
twice and both runs write the same bytes.
"""
import hashlib
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(BASE, "entry.png")
OUT_DIR = "/output"
TARGET = os.path.join(OUT_DIR, "entry.png")
SCRATCH = os.path.join(OUT_DIR, ".entry.png.part")


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(1 << 16)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def publish():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SOURCE, "rb") as src, open(SCRATCH, "wb") as dst:
        while True:
            block = src.read(1 << 16)
            if not block:
                break
            dst.write(block)
        dst.flush()
        os.fsync(dst.fileno())
    os.replace(SCRATCH, TARGET)


def main():
    publish()
    same_size = os.path.getsize(SOURCE) == os.path.getsize(TARGET)
    if not same_size or digest(SOURCE) != digest(TARGET):
        print("error: published file does not match entry.png",
              file=sys.stderr)
        return 1
    print("published %s (%d bytes, sha256 %s)"
          % (TARGET, os.path.getsize(TARGET), digest(TARGET)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
