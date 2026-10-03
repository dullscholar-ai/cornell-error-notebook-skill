# -*- coding: utf-8 -*-
"""ASCII density map of a region: '#' dark, 'R' red pen, ' ' blank. Use to locate layout.

Usage: python pixel_map.py <image> x1 y1 x2 y2 [block_x] [block_y]
"""
import sys
import numpy as np
from PIL import Image


def main():
    if len(sys.argv) < 6:
        print("usage: python pixel_map.py <image> x1 y1 x2 y2 [block_x] [block_y]")
        sys.exit(1)
    name = sys.argv[1]
    x1, y1, x2, y2 = [int(v) for v in sys.argv[2:6]]
    bx = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    by = int(sys.argv[7]) if len(sys.argv) > 7 else 3
    a = np.asarray(Image.open(name).convert("RGB"))[y1:y2, x1:x2].astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    gray = 0.3 * R + 0.59 * G + 0.11 * B
    dark = gray < 150
    red = (R > 90) & (R - G > 35) & (R - B > 35)
    print("box x%d-%d y%d-%d" % (x1, x2, y1, y2))
    h, w = dark.shape
    for yy in range(0, h, by):
        line = ""
        for xx in range(0, w, bx):
            d = dark[yy:yy + by, xx:xx + bx].mean()
            r = red[yy:yy + by, xx:xx + bx].mean()
            if r > 0.3:
                line += "R"
            elif d > 0.6:
                line += "#"
            elif d > 0.3:
                line += "+"
            elif d > 0.12:
                line += "."
            else:
                line += " "
        print("%4d %s" % (y1 + yy, line))
    ruler = "".join(("|" if (xx // bx) % 5 == 0 else " ") for xx in range(0, w, bx))
    print("     " + ruler)
    print("x ruler: '|' every %d px, start x=%d" % (bx * 5, x1))


if __name__ == "__main__":
    main()

