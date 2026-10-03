# -*- coding: utf-8 -*-
"""Rotate an image (deskew a scan). Use before OCR when the page is tilted.

Usage: python rotate_image.py <in_image> <degrees> <out_image>
"""
import sys
from PIL import Image


def main():
    if len(sys.argv) < 4:
        print("usage: python rotate_image.py <in_image> <degrees> <out_image>")
        sys.exit(1)
    im = Image.open(sys.argv[1])
    deg = float(sys.argv[2])
    im.rotate(deg, expand=True, fillcolor=(255, 255, 255)).save(sys.argv[3], quality=95)
    print("wrote", sys.argv[3], Image.open(sys.argv[3]).size)


if __name__ == "__main__":
    main()

