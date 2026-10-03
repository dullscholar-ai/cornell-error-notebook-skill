# -*- coding: utf-8 -*-
"""Crop a region, upscale, then OCR it (RapidOCR).

Usage: python ocr_region.py <image> x1 y1 x2 y2 [scale]
Coordinates are pixels in the original image; scale defaults to 3.
"""
import sys
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ENGINE = RapidOCR()


def main():
    if len(sys.argv) < 6:
        print("usage: python ocr_region.py <image> x1 y1 x2 y2 [scale]")
        sys.exit(1)
    name = sys.argv[1]
    x1, y1, x2, y2 = [int(v) for v in sys.argv[2:6]]
    scale = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    im = Image.open(name).convert("RGB").crop((x1, y1, x2, y2))
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    res, _ = ENGINE(np.asarray(im))
    if not res:
        print("  (no text)")
        return
    for box, text, score in res:
        xs = [p[0] / scale for p in box]
        ys = [p[1] / scale for p in box]
        print("  x=%4d..%4d y=%4d..%4d (%.2f) %s" % (
            x1 + min(xs), x1 + max(xs), y1 + min(ys), y1 + max(ys), score, text))


if __name__ == "__main__":
    main()

