---
name: cornell-error-notebook
description: 把试卷或作业的扫描件、照片整理成「康奈尔错题集」（Markdown + HTML，可再导出 PDF / Word），适用于语文、数学、英语、科学、历史、地理、社会、生物、化学、物理等各学科。覆盖从题卷与答卷 OCR、判定学生实际作答，到逐题填写康奈尔三栏、汇总错因的全流程。当用户提供某学科试卷或作业的扫描件 / 照片，或要求生成、追加、重做康奈尔错题集或错题本时使用。
metadata:
  short-description: 扫描件到康奈尔错题集
---

# 康奈尔错题集

把一份试卷或作业的扫描件整理成结构化的**康奈尔错题集**：OCR 题卷与答卷 → 判定学生实际作答 → 逐题写成「线索栏 / 主笔记区 / 总结栏」→ 汇总错因与学习建议 → 输出 Markdown 与 HTML（可再导出 PDF / Word）。学科不限。

## 硬性规则

1. **学生实际作答一律以答卷（答题卡 / 作业）为准**，题卷上印的、写的答案只作对照。日常作业（练习册上直接作答、无题卷答卷之分）以**黑笔=学生作答、红笔=老师批改、蓝笔=订正**判定。
2. **判不出来就标注，不要猜。** OCR 或像素判定无法确证的内容，写「待确认」，并在交付说明里列出需要用户核对的题号。学生自己在考试中划掉重写的答案，若老师未标错，不算错题。
3. **用户要求忽略的部分（如英语听力）不收录**，并在封面与索引页写明。
4. 编号与文件名沿用 `学科-YYYYMMDD-NNN`（例：`英语-20260923-002`）。同学科同一天多份，序号递增。
5. **每道错题必须写 `src` 出处**：哪份材料（练习册页码 / 微卷几 / 微专题）＋原题号＋扫描件文件名＋照片中的位置（左栏/右栏/单栏通排），出处同时出现在题目页题头下方和错题索引表，方便回到原始试卷人工比对。
6. **错题原文带图 / 带表的必须配图**：用 `crop_figure.py` 按比例坐标从扫描件裁出配图（拼成核对表逐张确认坐标，没切错题、没切掉关键内容再定稿），用 `whiten_figs.py` 把照片纸底处理成纯白（保留三种笔迹颜色），挂到该题 `images` 字段，嵌在「① 原题」下方。多张图用复用同一文件的方式去重（同一张图被多道小题引用时只存一份）。
7. **每题下方默认带「订正区」空白书写框**（构建脚本内置，高约 1/3 页、贴页底；顶层 `"correction_box": false` 可关闭，`"correction_box_height": "60mm"` 可调）。

## 工作目录

每个学科、每次考试一个目录，沿用用户习惯：`D:/哈哈错题集/<学科>/<YYYY.MM.DD>/`。用户另有指定时以用户为准。

```
<学科>/<YYYY.MM.DD>/
  题卷1.jpg 题卷2.jpg …     试卷扫描件（题干、选项）
  答卷1.jpg 答卷2.jpg …     答题卡 / 作业扫描件（学生作答 + 老师红笔批改）
  _w/                       分析中间件（裁剪图、OCR 脚本与输出）
  content.json              结构化错题内容（本 skill 的输入）
  <编号>.md / .html / .pdf / .docx   交付物
```

## 流程

### 0 确认范围
从扫描件读出学科、日期、试卷名称与来源、满分与得分、编号。读不出的问用户；不影响判定的可标「待确认」。

### 1 整理扫描件
题卷与答卷分开、按页序命名，方向不正的先纠正（PIL 旋转）。整页直接 OCR 效果差时，先切块再识别。注意区分版式：**练习册页是双栏**（按栏切半页细读），**微卷 / 试卷常是单栏**（按行左右切半页会导致一行断成两截，切分时按行通读）。

### 2 OCR 题卷
用 `ocr_region.py` 逐块识别题干与选项；版面拿不准时用 `pixel_map.py` 看密度图定位。目标：拿到每道错题的**完整原文**（题干 + 全部选项 + 材料）。

### 3 判定答卷（三重交叉验证）
- **客观题涂卡**：`option_scan.py` 采样每个选项的灰度，涂黑项灰度最低 → 还原所选；再用老师红笔标记位置交叉核对。
- **主观题手写**：`ocr_handwriting.py` 只保留黑色笔迹（滤掉红笔）逐格辨认，并参考红笔 ✗ 与红字改正。
- **题卷原文**：确认正确答案。

三者一致才写「确认」；不一致或读不清写「待确认」。方法细节见 `references/ocr-and-judging.md`。

### 4 写康奈尔内容
逐题填 `content.json`：线索栏 5 项（考点 / 关键词 / 规则 / 易错点 / 自测）、主笔记区 4 段（① 原题 ② 我的作答 ③ 正确解法 ④ 错因）、总结栏 3 项（思路归纳 / 方法反思 / 下次提醒），每题写 `src` 出处（见硬性规则 5），再写 `cause_rows`（错因归纳）、`core_issues`（核心问题 ≤3 条）、`advice`（学习建议）。字段与示例见 `references/content-schema.md`，各学科题型用词见 `references/subjects.md`。

### 4.5 配图裁剪与白底处理
对原文带图 / 带表的错题：
1. 用 `crop_figure.py` 按**整张照片的比例坐标**裁出配图，存 `<目录>/figures/`；
2. 把所有裁剪拼成一张核对表（PIL 贴标签合并）一次性 Read 核对：没裁到隔壁题、没切掉关键标注（如结构序号 ①②③、表格末行）再定稿；
3. 用 `whiten_figs.py figures/` 把照片灰绿纸底拉成纯白（保留黑/红/蓝笔迹）；
4. 把文件路径（`figures/fig_xxx.jpg`）挂到对应题的 `images` 字段。

### 5 生成 Markdown + HTML

```
python scripts/build_notebook.py <目录>/content.json
```

同目录生成 `<编号>.md` 与 `<编号>.html`。

### 6 可选导出

```
python scripts/html_to_pdf.py <编号>.html <编号>.pdf
python scripts/build_docx.py <编号>.html <编号>.docx
```

Word 版面自检：`powershell -File scripts/word_to_pdf.ps1 <编号>.docx <校验.pdf>`，再用 `render_pages.py` 看渲染结果。

### 7 自检
- HTML 含 `<!DOCTYPE html>`、`.cornell-grid`、`.cue-column`、`.summary-column`；用了 `review_ok` 时含「复习追踪」；配图题含 `<img class="q-img">`；每题含 `.q-src` 出处条；开了订正框时含 `.correction-box`。
- 页数 = 1 封面 + 1~N 错题索引 + (复习追踪) + N 题 + 1 错因归纳。
- `render_pages.py` 渲染 PNG 逐页看版面；`shot_html.py` 截封面与单题。
- 新增或改动过的 Python 脚本先 `python -m py_compile` 通过。

## 脚本

| 脚本 | 用途 |
|:--|:--|
| `scripts/build_notebook.py` | **核心**：`content.json` → `.md` + `.html`（内置订正区书写框、配图嵌入、出处标注，均可配置） |
| `scripts/crop_figure.py` | 按整张照片的比例坐标裁题目配图（可放大，供视觉核对） |
| `scripts/whiten_figs.py` | 配图纸底拉白（flat-field + 白点），保留黑/红/蓝笔迹 |
| `scripts/html_to_pdf.py` | HTML → PDF（Playwright 无头 Chromium，A4，走打印样式） |
| `scripts/build_docx.py` | HTML → Word（重建为真实表格，保留康奈尔版面） |
| `scripts/word_to_pdf.ps1` | Word COM 把 `.docx` 导出 PDF（校验 Word 版面） |
| `scripts/render_pages.py` | PDF 逐页 PNG + 每页首行文本（版面自检） |
| `scripts/shot_html.py` | Playwright 截取 `.cover` / 单道题（HTML 自检） |
| `scripts/ocr_region.py` | 裁剪 + 放大后 OCR |
| `scripts/ocr_handwriting.py` | 只保留黑色笔迹再 OCR（读学生手写，滤掉红笔） |
| `scripts/pixel_map.py` | 区域的 ASCII 密度图（深色 / 红笔） |
| `scripts/option_scan.py` | 一行选择题各选项灰度，判断涂黑项 |
| `scripts/solid_blobs.py` | 连通域找实心块（涂黑、印章等） |

## 参考

- `references/workflow.md`：分阶段操作细节、版面定位、错题取舍、错因归纳写法。
- `references/content-schema.md`：`content.json` 完整字段与示例、行内标记、输出结构。
- `references/ocr-and-judging.md`：像素阈值、红笔分离、涂卡判定、三重交叉验证与诚实性规则。
- `references/subjects.md`：各学科题型用词与线索栏写法。

