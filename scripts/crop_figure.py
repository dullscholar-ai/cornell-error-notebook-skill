# -*- coding: utf-8 -*-
"""Crop a question figure from a photo/scan by fractional coords, optionally zoom.

Usage:
    python crop_figure.py <img> <x0> <y0> <x1> <y1> <out> [scale]

Fractions are relative to the FULL image (0..1). scale > 1 enlarges the crop
(useful when reading the crop with a vision model). Output is JPEG q88 with a
mild contrast boost.
"""
import sys
import os
from PIL import Image, ImageEnhance

Image.MAX_IMAGE_PIXELS = None


def main():
    if len(sys.argv) < 7:
        print(__doc__)
        sys.exit(1)
    img, x0, y0, x1, y1, out = sys.argv[1:7]
    scale = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
    im = Image.open(img)
    w, h = im.size
    c = im.crop((int(float(x0) * w), int(float(y0) * h),
                 int(float(x1) * w), int(float(y1) * h)))
    if scale != 1.0:
        nw = int(c.width * scale)
        c = c.resize((nw, int(c.height * nw / c.width)), Image.LANCZOS)
    if c.width > 1500:
        c = c.resize((1500, int(c.height * 1500 / c.width)), Image.LANCZOS)
    c = ImageEnhance.Contrast(c).enhance(1.1)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    c.save(out, quality=88)
    print(out, c.size)


if __name__ == "__main__":
    main()
