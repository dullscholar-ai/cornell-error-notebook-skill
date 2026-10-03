# -*- coding: utf-8 -*-
"""Screenshot the cover and question blocks of a notebook HTML (visual QA).

Usage: python shot_html.py <notebook.html> [out_dir] [width]
"""
import os
import sys
import pathlib
from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) < 2:
        print("usage: python shot_html.py <notebook.html> [out_dir] [width]")
        sys.exit(1)
    html = os.path.abspath(sys.argv[1])
    out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(os.path.dirname(html), "_shots")
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    if not os.path.isdir(out):
        os.makedirs(out)
    uri = pathlib.Path(html).as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 1200}, device_scale_factor=2)
        pg.goto(uri)
        pg.wait_for_timeout(600)
        n = pg.locator(".question-block").count()
        print("question blocks:", n)
        pg.locator(".cover").screenshot(path=os.path.join(out, "cover.png"))
        for idx in sorted(set([0, n - 1])):
            if 0 <= idx < n:
                pg.locator(".question-block").nth(idx).screenshot(path=os.path.join(out, "q%02d.png" % (idx + 1)))
        b.close()
    print("shots dir:", out)


main()

