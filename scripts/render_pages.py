# -*- coding: utf-8 -*-
"""Render PDF pages to PNG and print each page's first text line (layout QA).

Usage: python render_pages.py <in.pdf> [out_dir] [dpi]
"""
import os
import sys
import fitz

NL = chr(10)


def main():
    if len(sys.argv) < 2:
        print("usage: python render_pages.py <in.pdf> [out_dir] [dpi]")
        sys.exit(1)
    pdf = os.path.abspath(sys.argv[1])
    out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(os.path.dirname(pdf), "_pages")
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    if not os.path.isdir(out):
        os.makedirs(out)
    doc = fitz.open(pdf)
    print("pages:", doc.page_count)
    for i in range(doc.page_count):
        t = doc[i].get_text().strip()
        head = t.split(NL)[0][:46] if t else "(blank)"
        print("%3d | %s" % (i + 1, head))
        doc[i].get_pixmap(dpi=dpi).save(os.path.join(out, "p%02d.png" % (i + 1)))
    print("PNG dir:", out)


main()

