# -*- coding: utf-8 -*-
"""Keep only black ink (drop teacher red pen), then OCR. Use to read student handwriting.

Usage: python ocr_handwriting.py <image> x1 y1 x2 y2 [scale]
"""
import sys
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ENGINE = RapidOCR()


def main():
    if len(sys.argv) < 6:
        print("usage: python ocr_handwriting.py <image> x1 y1 x2 y2 [scale]")
        sys.exit(1)
    name = sys.argv[1]
    x1, y1, x2, y2 = [int(v) for v in sys.argv[2:6]]
    scale = int(sys.argv[6]) if len(sys.argv) > 6 else 8
    im = Image.open(name).convert("RGB").crop((x1, y1, x2, y2))
    arr = np.asarray(im).astype(np.int16)
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    red = (R > 90) & (R - G > 30) & (R - B > 30)
    gray = 0.3 * R + 0.59 * G + 0.11 * B
    blk = (gray < 150) & (~red)
    out = np.full(arr.shape, 255, dtype=np.uint8)
    out[blk] = 0
    oi = Image.fromarray(out).resize(((x2 - x1) * scale, (y2 - y1) * scale), Image.LANCZOS)
    res, _ = ENGINE(np.asarray(oi))
    if not res:
        print("  (no text)")
        return
    for box, text, score in res:
        print("  (%.2f) %s" % (score, text))


if __name__ == "__main__":
    main()

