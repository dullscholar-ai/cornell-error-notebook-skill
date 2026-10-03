# -*- coding: utf-8 -*-
"""HTML -> PDF via headless Chromium (A4, print media).

Usage: python html_to_pdf.py <in.html> <out.pdf>
"""
import os
import sys
from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) < 3:
        print("usage: python html_to_pdf.py <in.html> <out.pdf>")
        sys.exit(1)
    src = os.path.abspath(sys.argv[1])
    out = os.path.abspath(sys.argv[2])
    uri = "file:///" + src.replace(os.sep, "/")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(uri)
        pg.emulate_media(media="print")
        pg.wait_for_timeout(800)
        pg.pdf(path=out, format="A4", print_background=True,
               margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
               prefer_css_page_size=False)
        b.close()
    print("PDF:", out, os.path.getsize(out))


main()

