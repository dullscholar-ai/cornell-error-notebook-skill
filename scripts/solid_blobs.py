# -*- coding: utf-8 -*-
"""Find solid blobs (filled bubbles, stamps, dark boxes) via connected components.

Usage: python solid_blobs.py <image> x1 y1 x2 y2 [min_area] [min_fill]
"""
import sys
import numpy as np
import cv2
from PIL import Image


def main():
    if len(sys.argv) < 6:
        print("usage: python solid_blobs.py <image> x1 y1 x2 y2 [min_area] [min_fill]")
        sys.exit(1)
    name = sys.argv[1]
    x1, y1, x2, y2 = [int(v) for v in sys.argv[2:6]]
    min_area = int(sys.argv[6]) if len(sys.argv) > 6 else 70
    min_fill = float(sys.argv[7]) if len(sys.argv) > 7 else 0.42
    a = np.asarray(Image.open(name).convert("RGB")).astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    gray = 0.3 * R + 0.59 * G + 0.11 * B
    red = (R > 90) & (R - G > 20) & (R - B > 20)
    dark = ((gray < 145) & (~red)).astype(np.uint8)
    sub = dark[y1:y2, x1:x2]
    sub = cv2.morphologyEx(sub, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    n, lab, stats, cent = cv2.connectedComponentsWithStats(sub, 8)
    rows = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area < min_area:
            continue
        fill = area / float(w * h)
        if fill < min_fill:
            continue
        rows.append((x + x1, y + y1, w, h, area, fill))
    rows.sort()
    print("solid blobs x%d-%d y%d-%d (area>=%d fill>=%.2f):" % (x1, x2, y1, y2, min_area, min_fill))
    for x, y, w, h, area, fill in rows:
        print("  x=%4d..%4d y=%4d..%4d w=%3d h=%3d area=%5d fill=%.2f" % (
            x, x + w, y, y + h, w, h, area, fill))


if __name__ == "__main__":
    main()

