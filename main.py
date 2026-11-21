"""VELMARIS — The Poster for a Place That Isn't There.

Entry for make.fun competition
`the-poster-for-a-place-that-i-2-20261121-0539`.

The program writes one image, /output/entry.png: a vintage travel
poster for VELMARIS, an invented lagoon city on stilts at golden
dusk — glass-domed boats on lantern-lit canals beneath crystal
cliffs. The place's name is set into the picture in large legible
art-deco capitals, with the single tagline "Where the water holds
the sky". No invented quotes, no star ratings, no endorsements.

The poster artwork ships beside this program as poster.jpg (a
1024x1024 JPEG, 309,278 bytes, under the 1 MiB cap). The program
copies it to the output directory verbatim, so the graded image is
exactly the poster reviewed during the build. Pure Python 3.13
standard library, no network, no dependencies.
"""

import os
import shutil
import sys

# The poster artwork, shipped in this repository next to main.py.
POSTER_FILE = "poster.jpg"

# Gate limits from the competition rules.
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024


def _poster_path() -> str:
    """Locate poster.jpg next to this file, wherever it is run from."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, POSTER_FILE)


def _check_jpeg(path: str) -> tuple[int, int, int]:
    """Validate the artwork before it is copied: a whole JPEG, no larger
    than 1024x1024, under the 1 MiB gate.

    Reads the JPEG SOF marker for width and height and checks the file
    size, so a corrupt or oversized asset fails loudly instead of
    producing an invalid entry.
    """
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise SystemExit(f"poster too large: {size} bytes > {MAX_BYTES}")
    with open(path, "rb") as fh:
        data = fh.read(2)
        if data != b"\xff\xd8":
            raise SystemExit("poster is not a JPEG (bad SOI marker)")
        width = height = None
        while True:
            marker = fh.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                break
            code = marker[1]
            if code in (0xC0, 0xC1, 0xC2):  # SOF0/1/2: height, width
                fh.read(3)
                raw = fh.read(4)
                height = (raw[0] << 8) | raw[1]
                width = (raw[2] << 8) | raw[3]
                break
            if code in (0xD8, 0xD9) or 0xD0 <= code <= 0xD7:
                continue
            length = fh.read(2)
            if len(length) < 2:
                break
            skip = ((length[0] << 8) | length[1]) - 2
            fh.seek(skip, os.SEEK_CUR)
    if width is None or height is None:
        raise SystemExit("poster JPEG has no SOF marker")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise SystemExit(f"poster too big: {width}x{height}")
    return width, height, size


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    source = _poster_path()
    width, height, size = _check_jpeg(source)

    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    # The grader collects outputs as another user: leave the file
    # readable by everyone (mode 0644), never 0600.
    os.chmod(target, 0o644)

    # Re-verify what actually landed in the output directory, so a
    # truncated copy or a permission slip is caught here, not by the
    # gate on the server.
    written = os.path.getsize(target)
    if written != size:
        raise SystemExit(f"output size mismatch: {written} != {size}")
    if oct(os.stat(target).st_mode & 0o777) != "0o644":
        raise SystemExit("output file is not mode 0644")

    print(f"VELMARIS poster written: {target}")
    print(f"format=JPEG {width}x{height} {size} bytes (cap {MAX_BYTES})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
