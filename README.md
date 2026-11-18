# 江淮之间 · 诗文里的滁州

> 滁州的三处水——酿泉、西涧、幽谷泉——各自被一首诗文钉住过一次。
> 三张海报把诗放进水里：水线以上是画，以下是墨池，**字沉在水面下**。

**2480 × 3508 / 300dpi / RGB / 三张一组**｜「诗文里的滁州」全网 AI 创作挑战赛 · AI 海报赛道

- 成品：`out/jianghuai-shan.jpg`、`out/jianghuai-jian.jpg`、`out/jianghuai-tian.jpg`
- 分层源文件：同目录 `.svg`（底图 / 水线 / 引文 / 句读 / 印 分层，文字是真文字）
- 阅稿页：<https://hkmpn9s6dh-commits.github.io/hackathon-2026-jianghuai/>
- 赛事简报：`docs/00-BRIEF.md`｜史实与引文：`docs/01-STORY.md`｜版式表：`docs/03-LAYOUT.md`

---

## 三张

| 张 | 单张名 | 方向 | 地标 | 引 |
| --- | --- | --- | --- | --- |
| 一 | 酿泉 | 山水寻幽 | 琅琊山 · 酿泉 · 醉翁亭 | 欧阳修《醉翁亭记》1046 |
| 二 | 西涧 | 人文寻脉 | 滁州西涧（俗名上马河） | 韦应物《滁州西涧》约 783 |
| 三 | 丰乐 | 烟火寻踪 | 丰山 · 幽谷泉 · 丰乐亭 | 欧阳修《丰乐亭记》1046 |

系列名取自《丰乐亭记》：「今滁介于江、淮之间」。

## 怎么跑

```bash
pip install -r requirements.txt      # numpy / Pillow / fonttools
bash verify.sh                        # 依赖 → 字体子集核对 → 版式表核对 → 构建 → 113 条断言 → 证据
```

只想出一张：`py -3 scripts/build.py --only shan`

## 三个被写进断言的数

| 数 | 值 | 断言 |
| --- | --- | --- |
| 水线 | y = 2245（三张逐像素相同） | AC-7 / AC-9 |
| 引文字号 | 92px（三张共用，由最长那一列反解） | AC-10 |
| 印 | 156×156（三张同尺寸） | AC-12 |

改字忘了重算，`verify.py` 当场 FAIL —— 这是这套版式唯一的护栏。

## 目录

```
story.py              唯一真相源：三张的引文、色、地标、图版
scripts/build.py      构建：底图裁切 → 墨池 → 水线 → 字 → 印 → 页脚 → JPG/PNG/SVG
scripts/layout.py     版式：把每个字算成坐标（PNG 与 SVG 共用同一份坐标）
scripts/verify.py     113 条断言（规格 / 系列一致 / 文案 / 版面卫生 / 可读性 / 源文件 / 字体 / 文档）
scripts/gen_docs.py   docs/03-LAYOUT.md 的唯一生成器（--check 反向核对）
scripts/proof.py      proof/contact-sheet.jpg 与 proof/report.md
assets/plates/        三张文生图底图（可替换）
assets/fonts/         随包字体与子集（含许可）
```

## AIGC 说明

底图为文生图模型输出；水线、墨池、竖排引文、句读记号、朱印、页脚、AIGC 标识全部由程序生成。
每张右下角带「AI 生成」显式标识。详见 `docs/06-AI-USAGE.md`。
