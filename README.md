# 康奈尔错题集 Skill（cornell-error-notebook）

把试卷 / 作业的**扫描件或照片**整理成结构化的**康奈尔错题本**（Markdown + HTML，可再导出 PDF / Word）。
覆盖从 OCR 题卷与答卷、判定学生实际作答，到逐题填写康奈尔三栏、汇总错因与学习建议的全流程。
学科不限：语文、数学、英语、科学、历史、地理、社会、生物、化学、物理均可。

成品长这样：封面 + 错题索引（含出处）+ 每题一页（线索栏 / 主笔记区 + 配图 + 总结栏 + **订正区空白书写框**）+ 错因归纳 + 学习建议，一题一页，直接打印给孩子重做。

---

## 功能特性

- **三重交叉验证判定**：涂卡像素采样、手写 OCR（滤掉红笔）、题卷原文比对，三者一致才记「确认」，读不清一律标「待确认」不硬猜。
- **日常作业模式**：无题卷答卷之分时，按「黑笔 = 学生作答、红笔 = 老师批改、蓝笔 = 订正」判定；学生自己划掉重写且老师未标错的，不算错题。
- **订正区书写框**：每题页底部自动生成空白框（默认约 1/3 页高、贴页底），打印后孩子直接重做；可关闭、可调高度。
- **题目配图**：原文带图 / 带表的错题自动嵌入从原扫描件裁出的配图，纸底自动拉成纯白（保留黑 / 红 / 蓝三种笔迹）。
- **出处标注**：每题标注「哪份材料 + 原题号 + 扫描件文件名 + 照片中的栏位」，题目页和错题索引都能看到，随时回原卷人工比对。
- **导出齐全**：HTML → PDF（Playwright）、HTML → Word（真实表格版面），渲染自检脚本齐备。

---

## 环境要求

- Python 3.8+，依赖：`pip install pillow numpy`
- 导出 PDF 需要 Playwright 无头浏览器（首次执行）：
  ```bash
  python -m playwright install chromium-headless-shell
  ```
- 导出 Word 需要 `build_docx.py` 的依赖（见脚本头部说明）；Word 版面校验需要 Windows + PowerShell。
- 该 skill 以 AI 编码代理的 Skill 形式使用（如 ZCode / Claude Code 等，放入 `skills` 目录即可被自动发现）；单独使用时直接照下文调脚本也完全可以。

---

## 快速上手

```
1. 把扫描件 / 照片放进工作目录（见下），确认黑笔 / 红笔 / 蓝笔约定
2. 逐页识读：切半页 → 看图 → 可疑处裁剪放大复核 → 记录每题的「学生答案 / 正确答案 / 红笔判定」
3. 写 content.json（错题的康奈尔三栏 + 出处 + 配图）
4. python scripts/build_notebook.py <目录>/content.json   → 生成 .md + .html
5. python scripts/html_to_pdf.py <编号>.html <编号>.pdf    → 导出 PDF
6. python scripts/render_pages.py <编号>.pdf              → 渲染 PNG 逐页自检
```

## 工作目录约定

每个学科、每次一份材料一个目录：

```
<学科>/<YYYY.MM.DD>/
  IMG_xxx.jpg …             扫描件 / 照片（题卷、答卷或作业页）
  _w/                       分析中间件（半页切分、放大裁剪、脚本输出，不交付）
  figures/                  题目配图（fig_*.jpg，交付时随 HTML 一起拷贝）
  content.json              结构化错题内容（本 skill 的输入）
  <编号>.md / .html / .pdf / .docx   交付物
```

---

## 完整流程

### 0 确认范围
从扫描件读出学科、日期、材料名称与来源、满分与得分、编号。读不出的问用户；不影响判定的可标「待确认」。

### 1 整理扫描件
按页序命名，方向不正先旋转。**注意版式**：练习册页多为**双栏**（可按栏切半页细读）；微卷 / 试卷常为**单栏**（按行左右切会把一行断成两截，应整行通读）。

### 2 识读题面
用 `ocr_region.py` 逐块识别题干与选项；版面拿不准时用 `pixel_map.py` 看密度图定位，或直接以视觉方式逐页细读。目标：拿到每道错题的**完整原文**（题干 + 全部选项 + 材料）。

### 3 判定作答（三重交叉验证）
- **客观题涂卡**：`option_scan.py` 采样各选项灰度，涂黑项灰度最低 → 还原所选，再用红笔标记位置交叉核对。
- **主观题手写**：`ocr_handwriting.py` 只保留黑色笔迹（滤掉红笔）逐格辨认，参考红笔 ✗ 与红字改正。
- **题卷原文**：确认正确答案。

三者一致才写「确认」；不一致或读不清写「待确认」。诚实性规则与像素阈值见 `references/ocr-and-judging.md`。

### 4 写康奈尔内容
逐题填 `content.json`：
- 线索栏 5 项：考点 / 关键词 / 规则 / 易错点 / 自测
- 主笔记区 4 段：① 原题 ② 我的作答 ③ 正确解法 ④ 错因
- 总结栏 3 项：思路归纳 / 方法反思 / 下次提醒
- 每题写 `src` 出处；带图 / 带表的题准备配图（见下）
- 汇总 `cause_rows`（错因归纳）、`core_issues`（核心问题 ≤3 条）、`advice`（学习建议）

字段与完整示例见 [`references/content-schema.md`](references/content-schema.md)，各学科题型用词见 [`references/subjects.md`](references/subjects.md)。

### 4.5 配图裁剪与白底处理（原文带图 / 带表的题必做）

```bash
# 1) 按整张照片的比例坐标裁配图（scale 可放大，供视觉核对）
python scripts/crop_figure.py IMG_xxx.jpg 0.04 0.225 0.55 0.325 figures/fig_q1.jpg

# 2) 把所有裁剪拼成一张带标签的核对表，一次性检查：
#    没裁到隔壁题、没切掉结构序号 / 表格末行等关键内容
# （用 PIL 贴文件名合并缩略图即可）

# 3) 纸底拉白：灰绿照片底 → 纯白，保留黑/红/蓝笔迹
python scripts/whiten_figs.py figures/
```

坐标迭代技巧：比例坐标第一次常偏，用「裁一张 → 看一张 → 调 y 值」逐步修正；核对表确认全部合格后再挂到 `images` 字段。

### 5 生成 Markdown + HTML

```bash
python scripts/build_notebook.py <目录>/content.json
# 同目录生成 <编号>.md 与 <编号>.html
```

### 6 可选导出

```bash
python scripts/html_to_pdf.py <编号>.html <编号>.pdf
python scripts/build_docx.py   <编号>.html <编号>.docx
```

Word 版面自检：`powershell -File scripts/word_to_pdf.ps1 <编号>.docx <校验.pdf>`，再用 `render_pages.py` 看渲染结果。

### 7 自检清单
- HTML 含 `<!DOCTYPE html>`、`.cornell-grid`、`.cue-column`、`.summary-column`；配图题含 `<img class="q-img">`；每题含 `.q-src` 出处条；开了订正框含 `.correction-box`；用了 `review_ok` 时含「复习追踪」。
- 页数 = 1 封面 + 1~N 错题索引 + (复习追踪) + N 题 + 1 错因归纳。
- `render_pages.py` 渲染 PNG 逐页看版面；`shot_html.py` 截封面与单题。
- 新增或改动过的 Python 脚本先 `python -m py_compile` 通过。

---

## content.json 关键字段

顶层（`subject` 与 `questions` 必填，其余可省略）：

| 字段 | 说明 |
|:--|:--|
| `subject` / `date` / `code` | 学科 / 日期 / 编号（编号同时用作输出文件名） |
| `class_name` / `grade_line` / `source` | 班级 / 年级 / 材料名称与来源 |
| `total` / `score` | 满分 / 得分（日常作业可省） |
| `notes` | 封面与索引页的说明（待确认项、忽略项等） |
| `judge_heading` / `judge_note` | 判定依据说明（默认三重交叉验证文案，可替换） |
| `questions` | 错题数组 |
| `review_ok` | `[["题号","我的作答","正确答案"], …]`，填了多一页「复习追踪」 |
| `cause_rows` / `core_issues` / `advice` | 错因归纳 / 核心问题（≤3 条）/ 学习建议 |
| `correction_box` | 默认 `true`；设 `false` 关闭每题的订正区书写框 |
| `correction_box_height` | 订正区高度，默认 `"88mm"`（约 1/3 A4 页高） |

每道错题（`questions` 元素）：

| 字段 | 说明 |
|:--|:--|
| `q` / `sec` / `topic` / `star` | 题号 / 题型 / 考点 / 难度 |
| `src` | **出处**：`材料 + 页码/题号 + 扫描件文件名 + 位置`，如 `"题题清练习册 B12 页 第 1 题 ｜ 扫描件 IMG_20261002_135120.jpg（左栏）"` |
| `images` | **配图**路径数组（相对 HTML，如 `figures/fig_b12_q1.jpg`），嵌在「① 原题」下方；同一张图被多道小题引用时复用同一文件 |
| `cue` | 线索栏 5 项 |
| `body` | 主笔记区 4 段；单独一行 `"————"` 渲染为分隔线（用于把材料与问题分开） |
| `summ` | 总结栏 3 项 |

行内标记：`**加粗**`；`` @@等宽@@ ``（英文、公式、选项字母、规则名）。

---

## 脚本一览

| 脚本 | 用途 |
|:--|:--|
| `scripts/build_notebook.py` | **核心**：`content.json` → `.md` + `.html`（内置订正框 / 配图 / 出处，均可配置） |
| `scripts/crop_figure.py` | 按整张照片的比例坐标裁题目配图（可放大） |
| `scripts/whiten_figs.py` | 配图纸底拉白（flat-field + 白点，保留笔迹颜色） |
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
| `scripts/rotate_image.py` | 图片方向纠正 |

## 参考文档

- [`references/workflow.md`](references/workflow.md)：分阶段操作细节、版面定位、错题取舍、错因归纳写法
- [`references/content-schema.md`](references/content-schema.md)：`content.json` 完整字段与示例、行内标记、输出结构
- [`references/ocr-and-judging.md`](references/ocr-and-judging.md)：像素阈值、红笔分离、涂卡判定、三重交叉验证与诚实性规则
- [`references/subjects.md`](references/subjects.md)：各学科题型用词与线索栏写法

## 常见问题

- **HTML 里配图不显示**：`images` 用的是相对路径，移动 / 发送交付物时请把 `figures/` 文件夹连同 HTML 一起拷。
- **PDF 导出报 Playwright 浏览器缺失**：`python -m playwright install chromium-headless-shell`。
- **导出 PDF 报 PermissionError**：目标 PDF 正被阅读器打开占用；先导到临时文件名再替换，或关闭阅读器后重试。
- **`github.com:443` 连不上但 `api.github.com` 通**（部分网络环境）：`git push` 会失败，可改用 GitHub Contents API 逐文件上传（`gh auth token` + `PUT /repos/{owner}/{repo}/contents/{path}`，文件已存在时需带其 `sha`）。
- **诚实性红线**：判定不出来的题一律「待确认」并列入交付说明，绝不猜；学生自己订正过且老师未标错的，不算错题。

---

## License

MIT
