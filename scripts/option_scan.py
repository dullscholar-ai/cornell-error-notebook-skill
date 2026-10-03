# -*- coding: utf-8 -*-
"""Estimate which option is filled in one answer-card row.

Splits the row into n equal bins and reports dark-pixel fraction per bin;
the filled bubble is normally the darkest bin.

Usage: python option_scan.py <image> x1 y1 x2 y2 [n_options]
Refine with pixel_map.py if the option boxes are not evenly spaced.
"""
import sys
import numpy as np
from PIL import Image


def main():
    if len(sys.argv) < 6:
        print("usage: python option_scan.py <image> x1 y1 x2 y2 [n_options]")
        sys.exit(1)
    name = sys.argv[1]
    x1, y1, x2, y2 = [int(v) for v in sys.argv[2:6]]
    n = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    a = np.asarray(Image.open(name).convert("RGB"))[y1:y2, x1:x2].astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    gray = 0.3 * R + 0.59 * G + 0.11 * B
    red = (R > 90) & (R - G > 30) & (R - B > 30)
    dark = (gray < 150) & (~red)
    w = x2 - x1
    fracs = []
    for i in range(n):
        lo = int(round(i * w / float(n)))
        hi = int(round((i + 1) * w / float(n)))
        fracs.append(float(dark[:, lo:hi].mean()))
    letters = "ABCDEFGH"
    print("region x%d-%d y%d-%d  n=%d" % (x1, x2, y1, y2, n))
    for i, f in enumerate(fracs):
        bar = "#" * int(round(f * 40))
        print("  %s  %.3f  %s" % (letters[i], f, bar))
    best = int(np.argmax(fracs))
    print("  -> darkest bin: %s (%.3f)" % (letters[best], fracs[best]))
    print("  NOTE: verify against the teacher red mark; a filled bubble is dark AND round.")


if __name__ == "__main__":
    main()

