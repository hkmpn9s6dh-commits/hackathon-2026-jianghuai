# -*- coding: utf-8 -*-
"""生成 docs/03-LAYOUT.md（分镜式的版式表），并支持 --check 反向核对。

  py -3 scripts/gen_docs.py           # 重新生成
  py -3 scripts/gen_docs.py --check    # 只核对：文档与 story.py / layout.py 是否还一致
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import story as S
import layout as L

DOC = os.path.join(ROOT, "docs", "03-LAYOUT.md")


def render():
    size = L.global_size()
    out = []
    out.append("# 03 · 版式表（由 `scripts/gen_docs.py` 生成，不要手改）\n")
    out.append("画布 **%d × %d** @%ddpi；水线 **y = %d**（三张逐像素相同）；"
               "引文字号 **%dpx**（三张共用，由最长那一列决定）。\n" % (S.W, S.H, S.DPI, S.WATERLINE, size))
    out.append("| 张 | 单张名 | 方向 | 列数 | 最长列 | 引文字数 | 印 | 地标 |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for p in S.POSTERS:
        gs, marks, cols = L.layout(p)
        n = sum(len([c for c in col if c not in "，。"]) for col in cols)
        out.append("| %s | %s | %s | %d | %d | %d | %s | %s |" % (
            p["no"], p["title"], p["direction"], len(cols),
            max(len(c) for c in cols), n, p["seal"], p["landmark"]))
    out.append("")
    for p in S.POSTERS:
        gs, marks, cols = L.layout(p)
        out.append("## %s · %s（%s）\n" % (p["no"], p["title"], p["direction"]))
        out.append("> %s\n" % p["source"])
        out.append("竖排，右起，每列一句：\n")
        out.append("```")
        for i, col in enumerate(cols):
            out.append("第 %d 列（x=%d）：%s" % (i + 1, L.layout(p)[0][0]["x"] - i * int(size * L.COL_STEP), col))
        out.append("```")
        x0, y0, x1, y1 = p["_seal_box"]
        out.append("")
        out.append("- 落款：`%s`（马善政 %dpx）｜印：`%s` %d×%d @ (%d,%d)" % (
            p["title"], [g["size"] for g in gs if g["font"] == "brush"][0],
            p["seal"], x1 - x0, y1 - y0, x0, y0))
        out.append("- 水线：全幅 %dpx 宽，色 `#%02x%02x%02x`，y=%d" % (S.W, *p["accent"], S.WATERLINE))
        out.append("- 页脚三行：引文出处 / 地标 / 方向与系列；右下角红底白字「AI 生成」标签")
        out.append("")
    out.append("## 一套版式为什么这样定\n")
    out.append("1. **水线**是全系列唯一的硬骨架：三张的水线落在同一行（逐像素），系列才成立。")
    out.append("2. **字号不随图变**：三张共用一个字号（%dpx），由最长的那一列反解出来；" % size)
    out.append("   改字忘了重算，`verify.py` 的 AC-10 会当场 FAIL。")
    out.append("3. **字全部落在墨池里**：水线以下压一层 52%→95% 的墨，"
               "逐字量对比度（AC-27），不靠「看着还行」。")
    out.append("4. **落款压左边距**：名与印贴左，字头在水线下 140px 左右起，"
               "与右侧引文形成「一行一柱」的对照。")
    out.append("")
    return "\n".join(out) + "\n"


def main():
    txt = render()
    if "--check" in sys.argv:
        if not os.path.exists(DOC):
            print("缺 docs/03-LAYOUT.md")
            return 1
        old = open(DOC, encoding="utf-8").read()
        if old != txt:
            print("docs/03-LAYOUT.md 与 story.py 不一致，重跑 gen_docs.py")
            return 1
        print("PASS 分镜表与 story.py 一致")
        return 0
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    open(DOC, "w", encoding="utf-8", newline="\n").write(txt)
    print("写出", DOC)
    return 0


if __name__ == "__main__":
    sys.exit(main())
