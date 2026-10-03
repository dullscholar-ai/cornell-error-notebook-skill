# -*- coding: utf-8 -*-
"""康奈尔错题集 generator: content.json -> <code>.md + <code>.html

Usage:
    python build_notebook.py <path/to/content.json> [output_dir]

Schema and a worked example: references/content-schema.md
"""
import io
import os
import sys
import json

BT = chr(96)
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
CSS_FILE = os.path.normpath(os.path.join(HERE, "..", "assets", "notebook.css"))

DEFAULT_JUDGE = [
    "本次“学生实际作答”**一律以答卷（答题卡）为准**，题卷上印的、写的答案只作对照参考。判定用三重交叉验证：",
    "",
    "1. **答题卡客观题涂卡**：用像素灰度采样（涂黑选项的灰度值明显最低）逐个还原选项，再用“红笔标记位置”交叉核对。",
    "2. **答题卡主观题手写**：在答卷手写区逐格辨认，并参考老师红笔的改错（打叉 + 红字改正）。",
    "3. **题卷原文**：从题卷 OCR 出完整题干与选项，逐题确认正确答案。",
]

COVER_HOWTO = [
    ("遮住右边", "（主笔记区）→ 只看左边「线索栏」→ 用自己的话回忆这道题怎么做"),
    ("想不起来？", "展开右边，对照「正确解法」看一遍"),
    ("读底部「总结栏」", "→ 记住那句「下次提醒」"),
    ("每周翻一次", "→ 能回忆起来的打勾，卡壳的留着考前重看"),
]


def md_inline(s):
    return s.replace("@@", BT)


def inline_html(s):
    s = s.replace("@@", BT)
    out = []
    i = 0
    while i < len(s):
        if s[i] == BT:
            j = s.find(BT, i + 1)
            if j == -1:
                out.append(s[i]); i += 1; continue
            out.append("<code>%s</code>" % s[i + 1:j]); i = j + 1
        elif s.startswith("**", i):
            j = s.find("**", i + 2)
            if j == -1:
                out.append(s[i]); i += 1; continue
            out.append("<strong>%s</strong>" % s[i + 2:j]); i = j + 2
        else:
            out.append(s[i]); i += 1
    return "".join(out)


def cover_subtitle(C):
    parts = []
    if C.get("grade_line"):
        parts.append(C["grade_line"])
    if C.get("class_name"):
        parts.append("%s 班" % C["class_name"])
    if C.get("subject"):
        parts.append(C["subject"])
    return " · ".join(parts)


def build_md(C):
    Q = C.get("questions", [])
    RO = C.get("review_ok", [])
    L = []
    A = L.append
    A("# 康奈尔错题本 · %s" % C.get("subject", ""))
    A("")
    A("| 项目 | 内容 | 项目 | 内容 |")
    A("|:---|:---|:---|:---|")
    A("| 学科 | %s | 日期 | %s |" % (C.get("subject", ""), C.get("date", "")))
    A("| 班级 | %s | 来源 | %s |" % (C.get("class_name", ""), C.get("source", "")))
    A("| 满分 | %s | 得分 | %s |" % (C.get("total", ""), C.get("score", "")))
    A("| 错题数 | %d 处 | 编号 | %s |" % (len(Q), C.get("code", "")))
    A("")
    A("**编号**：%s" % C.get("code", ""))
    A("")
    A("---")
    A("")
    A("## 错题索引")
    A("")
    A("| 序号 | 题号 | 题型 | 考点 | 出处（扫描件/位置） | 难度 |")
    A("|:---:|:---:|:---|:---|:---|:---:|")
    for i, x in enumerate(Q, 1):
        A("| %d | %s | %s | %s | %s | %s |" % (
            i, x.get("q", ""), x.get("sec", ""), x.get("topic", ""),
            x.get("src", ""), x.get("star", "")))
    A("")
    for nt in C.get("notes", []):
        A("> %s" % nt)
    A("")
    A("---")
    A("")
    A("## %s" % C.get("judge_heading", "〇、判定依据说明（先看这一段）"))
    A("")
    for ln in C.get("judge_note", DEFAULT_JUDGE):
        A(md_inline(ln))
    A("")
    A("**本次共归集 %d 处错题**。" % len(Q))
    A("")
    if RO:
        A("---")
        A("")
        A("## 复习追踪")
        A("")
        A("已核对正确的题目（复习时快速过一遍，能在脑子里答对就打勾）：")
        A("")
        A("| 题号 | 我的作答 | 正确答案 | 复习 |")
        A("|:---:|:---|:---|:---:|")
        for row in RO:
            A("| %s | %s | %s |  |" % (row[0], row[1], row[2]))
        A("")
    A("---")
    A("")
    n = len(Q)
    cb = True
    for i, x in enumerate(Q, 1):
        A("## 第 %s 题 ｜ %s ｜ %s ｜ %s" % (
            x.get("q", ""), x.get("sec", ""), x.get("topic", ""), x.get("star", "")))
        A("")
        if x.get("src"):
            A("出处：%s" % md_inline(x["src"]))
            A("")
        A("%s ｜ 第 %d 页 / 共 %d 页" % (C.get("date", ""), i, n))
        A("")
        A("| 线索栏 ▸ 只看这栏回忆 | 主笔记区 ▸ 卡壳再展开 |")
        A("|:---|:---|")
        cue_cells = "<br>".join("**%s**：%s" % (k, md_inline(v)) for k, v in x.get("cue", []))
        main_cells = []
        for title, lines in x.get("body", []):
            cell_lines = list(lines)
            if title.startswith("①") and x.get("images"):
                for im in x["images"]:
                    cell_lines.append("![题目配图](%s)" % im)
            main_cells.append("**%s**<br>%s" % (
                title, "<br>————<br>".join(md_inline(z) for z in cell_lines)))
        A("| %s | %s |" % (cue_cells, "<br>————<br>".join(main_cells)))
        A("")
        A("| 总结栏 ▸ 读完立刻写，考前只读这一栏 |")
        A("|:---|")
        A("| %s |" % "<br>".join("**%s**：%s" % (k, md_inline(v)) for k, v in x.get("summ", [])))
        A("")
        if cb:
            A("### ✏️ 订正区（不看笔记，把这道题重新做一遍）")
            A("")
            A("```")
            for _ in range(12):
                A("")
            A("```")
            A("")
        A("---")
        A("")
    A("## 错因归纳")
    A("")
    A("| 错因类型 | 题号 | 出现次数 |")
    A("|:---|:---|:---:|")
    for row in C.get("cause_rows", []):
        A("| %s | %s | %s |" % (row[0], row[1], row[2]))
    A("")
    A("---")
    A("")
    A("## 核心问题（不超过 3 条）")
    A("")
    for i, s in enumerate(C.get("core_issues", []), 1):
        A("%d. %s" % (i, md_inline(s)))
    A("")
    A("---")
    A("")
    A("## 学习建议")
    A("")
    A("> 基于以上错因分析，建议重点练习：")
    A(">")
    for i, s in enumerate(C.get("advice", []), 1):
        A("> %d. %s" % (i, md_inline(s)))
    A("")
    return NL.join(L)


def build_html(C, css):
    Q = C.get("questions", [])
    RO = C.get("review_ok", [])
    H = []
    A = H.append
    A('<!DOCTYPE html>')
    A('<html lang="zh-CN">')
    A('<head>')
    A('<meta charset="UTF-8">')
    A('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    A('<title>康奈尔错题本 · %s · %s</title>' % (C.get("subject", ""), C.get("date", "")))
    A('<style>')
    A(css)
    A('</style>')
    A('</head>')
    A('<body>')
    A('<div class="page cover">')
    A('  <h1>康奈尔错题本</h1>')
    A('  <p class="subtitle">%s</p>' % inline_html(cover_subtitle(C)))
    A('  <table class="meta-table">')
    A('    <tr><td>学科</td><td>%s</td><td>日期</td><td>%s</td></tr>' % (
        C.get("subject", ""), C.get("date", "")))
    A('    <tr><td>来源</td><td colspan="3">%s</td></tr>' % C.get("source", ""))
    A('    <tr><td>满分</td><td>%s</td><td>得分</td><td>%s</td></tr>' % (
        C.get("total", ""), C.get("score", "")))
    A('    <tr><td>错题数</td><td>%d 处</td><td>编号</td><td>%s</td></tr>' % (
        len(Q), C.get("code", "")))
    A('  </table>')
    A('  <div class="how-to-use">')
    A('    <h3>怎么用这本错题本</h3>')
    A('    <ol>')
    for name, desc in COVER_HOWTO:
        A('      <li><strong>%s</strong>%s</li>' % (name, desc))
    A('    </ol>')
    for nt in C.get("notes", []):
        A('    <p style="margin-top:10px;font-size:12px;color:#333;">%s</p>' % nt)
    A('  </div>')
    A('</div>')
    A('<div class="page">')
    A('  <div class="page-title">错题索引</div>')
    A('  <table class="error-table">')
    A('    <thead><tr><th class="c" style="width:7%">序号</th><th class="c" style="width:11%">题号</th>'
      '<th style="width:12%">题型</th><th style="width:32%">考点</th><th style="width:30%">出处（扫描件/位置）</th><th class="c" style="width:8%">难度</th></tr></thead>')
    A('    <tbody>')
    for i, x in enumerate(Q, 1):
        A('      <tr><td class="c">%d</td><td class="c">%s</td><td>%s</td><td>%s</td><td style="font-size:10.5px;">%s</td><td class="c">%s</td></tr>' % (
            i, x.get("q", ""), x.get("sec", ""), x.get("topic", ""),
            inline_html(x.get("src", "")), x.get("star", "")))
    A('    </tbody>')
    A('  </table>')
    A('  <div class="callout">')
    A('    <h3>%s</h3>' % C.get("judge_heading", "〇、判定依据说明（先看这一段）"))
    judge = C.get("judge_note", DEFAULT_JUDGE)
    in_list = False
    for ln in judge:
        if ln.strip() == "":
            if in_list:
                A('    </ol>')
                in_list = False
            continue
        if ln[:2] in ("1.", "2.", "3.", "4.", "5."):
            if not in_list:
                A('    <ol>')
                in_list = True
            A('      <li>%s</li>' % inline_html(ln[ln.find(" ") + 1:]))
        else:
            if in_list:
                A('    </ol>')
                in_list = False
            A('    <p>%s</p>' % inline_html(ln))
    if in_list:
        A('    </ol>')
    A('    <p><strong>本次共归集 %d 处错题</strong>。</p>' % len(Q))
    A('  </div>')
    A('</div>')
    if RO:
        A('<div class="page">')
        A('  <div class="page-title">复习追踪</div>')
        A('  <div class="redo-area">')
        A('    <h4>已核对正确的题目（复习时快速过一遍，能在脑子里答对就打勾）</h4>')
        A('    <table class="redo-table">')
        A('      <thead><tr><th>题号</th><th>我的作答</th><th>正确答案</th><th>复习</th></tr></thead>')
        A('      <tbody>')
        for row in RO:
            A('        <tr><td>%s</td><td>%s</td><td>%s</td><td></td></tr>' % (row[0], row[1], row[2]))
        A('      </tbody>')
        A('    </table>')
        A('  </div>')
        A('</div>')
    n = len(Q)
    cb = C.get("correction_box", True)
    for i, x in enumerate(Q, 1):
        A('<div class="page%s">' % (" qpage" if cb else ""))
        A('  <div class="question-block">')
        A('    <div class="q-header">')
        A('      <h2>第 %s 题 ｜ %s ｜ %s ｜ %s</h2>' % (
            x.get("q", ""), x.get("sec", ""), x.get("topic", ""), x.get("star", "")))
        A('      <span class="q-meta">%s ｜ 第 %d 页 / 共 %d 页</span>' % (C.get("date", ""), i, n))
        A('    </div>')
        if x.get("src"):
            A('    <div class="q-src">出处：%s</div>' % inline_html(x["src"]))
        A('    <div class="cornell-grid">')
        A('      <div class="cue-column">')
        A('        <div class="zone-label">线索栏 ▸ 只看这栏回忆</div>')
        for k, v in x.get("cue", []):
            A('        <div class="field"><div class="field-name">%s</div><div class="field-value">%s</div></div>' % (
                k, inline_html(v)))
        A('      </div>')
        A('      <div class="main-column">')
        A('        <div class="zone-label">主笔记区 ▸ 卡壳再展开</div>')
        for title, lines in x.get("body", []):
            A('        <div class="section"><span class="section-title">%s</span>' % title)
            for ln in lines:
                if ln == "————":
                    A('        <hr class="divider">')
                else:
                    A('        <div>%s</div>' % inline_html(ln))
            if title.startswith("①") and x.get("images"):
                for im in x["images"]:
                    A('        <img class="q-img" src="%s" alt="题目配图">' % im)
            A('        </div>')
        A('      </div>')
        A('    </div>')
        A('    <div class="summary-column">')
        A('      <div class="zone-label">总结栏 ▸ 读完立刻写，考前只读这一栏</div>')
        for k, v in x.get("summ", []):
            A('      <div class="field"><span class="field-name">%s</span>：%s</div>' % (k, inline_html(v)))
        A('    </div>')
        if cb:
            A('    <div class="correction-box">')
            A('      <div class="zone-label">订正区 ▸ 不看笔记，把这道题重新做一遍，写完给家长检查</div>')
            A('      <div class="correction-space"></div>')
            A('    </div>')
        A('  </div>')
        A('</div>')
    A('<div class="page">')
    A('  <div class="page-title">错因归纳</div>')
    A('  <table class="error-table">')
    A('    <thead><tr><th style="width:52%">错因类型</th><th style="width:32%">题号</th>'
      '<th class="c" style="width:16%">出现次数</th></tr></thead>')
    A('    <tbody>')
    for row in C.get("cause_rows", []):
        A('      <tr><td>%s</td><td>%s</td><td class="c">%s</td></tr>' % (row[0], row[1], row[2]))
    A('    </tbody>')
    A('  </table>')
    A('  <div class="core-issues">')
    A('    <h3>核心问题（不超过 3 条）</h3>')
    A('    <ol>')
    for s in C.get("core_issues", []):
        A('      <li>%s</li>' % inline_html(s))
    A('    </ol>')
    A('  </div>')
    A('  <div class="advice-box">')
    A('    <h3>学习建议</h3>')
    A('    <ol>')
    for s in C.get("advice", []):
        A('      <li>%s</li>' % inline_html(s))
    A('    </ol>')
    A('  </div>')
    A('</div>')
    A('</body>')
    A('</html>')
    return NL.join(H)


def main():
    if len(sys.argv) < 2:
        print("usage: python build_notebook.py <content.json> [output_dir]")
        sys.exit(1)
    src = sys.argv[1]
    with io.open(src, encoding="utf-8") as f:
        C = json.load(f)
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(src))
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    code = C.get("code") or "notebook"
    with io.open(CSS_FILE, encoding="utf-8") as f:
        css = f.read()
    if C.get("correction_box", True):
        h = C.get("correction_box_height", "88mm")
        css += """
  /* 订正区（每题一页底部的空白书写框，默认约占页面 1/3，高度可配） */
  .page.qpage { display: flex; flex-direction: column; }
  .page.qpage .question-block { display: flex; flex-direction: column; flex: 1 1 auto; margin-bottom: 0; }
  .correction-box {
    flex: 0 0 auto; height: %s; margin-top: auto;
    border: 1.5px solid #000; border-radius: 2px; padding: 6px 10px;
  }
  .correction-box .zone-label { margin-bottom: 2px; }
  .correction-box .correction-space { height: calc(100%% - 24px); }
""" % h
    css += """
  /* 题目配图（嵌在「① 原题」下方） */
  .main-column .q-img {
    display: block; max-width: 92%; max-height: 60mm;
    margin: 5px auto 2px; border: 1px solid #bbb;
  }
  /* 出处标注（题头下方灰条 + 索引列） */
  .q-src {
    font-size: 11px; color: #444; background: #f4f4f4;
    border-left: 3px solid #999; padding: 3px 8px; margin: 0 0 7px;
  }
"""
    md_path = os.path.join(outdir, code + ".md")
    html_path = os.path.join(outdir, code + ".html")
    with io.open(md_path, "w", encoding="utf-8") as f:
        f.write(build_md(C))
    with io.open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(C, css))
    print("MD:   " + md_path)
    print("HTML: " + html_path)
    print("questions: %d | review_ok: %d" % (len(C.get("questions", [])), len(C.get("review_ok", []))))


if __name__ == "__main__":
    main()

