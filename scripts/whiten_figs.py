# -*- coding: utf-8 -*-
"""Whiten photo-paper background of figure crops (flat-field + white point).

题目配图从手机照片裁出来时纸底是灰绿色的。本脚本把纸底拉成纯白，
同时保留黑笔、红笔、蓝笔笔迹与图形。

Usage:
    python whiten_figs.py <dir|file> [more paths...]

传目录则处理其中所有 fig_*.jpg；传文件则处理该文件（就地覆盖）。
"""
import os, sys, glob
import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None


def whiten(path):
    im = Image.open(path).convert("RGB")
    # 估计纸底：MaxFilter 膨胀掉深色墨迹，再高斯模糊抹平彩色笔迹与阴影
    bg = im.filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.GaussianBlur(35))
    a = np.asarray(im).astype(np.float32)
    b = np.maximum(np.asarray(bg).astype(np.float32), 40.0)  # 永不除以近黑
    out = np.clip(a / b * 250.0, 0, 255)                     # flat-field: 纸底 -> ~250
    mask = out.min(axis=2) > 222                             # 近白推到纯白
    out[mask] = 255
    out = 255.0 * np.power(out / 255.0, 1.12)                # 轻微加深笔迹
    Image.fromarray(out.astype(np.uint8)).save(path, quality=90)
    print("whitened", path)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            for p in sorted(glob.glob(os.path.join(arg, "fig_*.jpg"))):
                whiten(p)
        else:
            whiten(arg)


if __name__ == "__main__":
    main()
