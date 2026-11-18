# -*- coding: utf-8 -*-
"""证据：三张联系表（含尺标）、整体预览、量测报告 proof/report.md。

  py -3 scripts/proof.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import story as S
import layout as L

OUT = os.path.join(ROOT, "out")
PROOF = os.path.join(ROOT, "proof")


def sheet():
    """三张并排，带 10cm 比例尺与每张的水线位置标注。"""
    tw = 620
    ims = []
    for p in S.POSTERS:
        im = Image.open(os.path.join(OUT, "jianghuai-%s.jpg" % p["key"])).convert("RGB")
        im = im.resize((tw, int(tw * S.H / S.W)), Image.LANCZOS)
        ims.append((p, im))
    h = ims[0][1].height
    gap = 40
    W = tw * 3 + gap * 4
    canvas = Image.new("RGB", (W, h + 110), (238, 235, 228))
    d = ImageDraw.Draw(canvas)
    for i, (p, im) in enumerate(ims):
        x = gap + i * (tw + gap)
        canvas.paste(im, (x, 60))
        d.text((x, 20), "%s · %s（%s）" % (p["no"], p["title"], p["direction"]), fill=(40, 40, 40))
        y = 60 + int(S.WATERLINE * tw / S.W)
        d.line([(x, y), (x + tw, y)], fill=(200, 60, 40), width=2)
    # 比例尺：10cm @300dpi = 1181px → 缩到 tw/2480
    scale_px = int(1181 * tw / S.W)
    x0 = W - gap - scale_px
    y0 = h + 78
    d.line([(x0, y0), (x0 + scale_px, y0)], fill=(30, 30, 30), width=4)
    d.text((x0 - 6, y0 - 26), "10 cm（按 300dpi 折算）", fill=(30, 30, 30))
    canvas.save(os.path.join(PROOF, "contact-sheet.jpg"), quality=88)


def measures():
    rows = []
    for p in S.POSTERS:
        j = Image.open(os.path.join(OUT, "jianghuai-%s.jpg" % p["key"]))
        a = np.asarray(j.convert("RGB")).astype(float)
        lay = json.load(open(os.path.join(ROOT, "build", "layout-%s.json" % p["key"]), encoding="utf-8"))
        rows.append(dict(
            key=p["key"], title=p["title"],
            size="%dx%d" % j.size, dpi="%d" % j.info.get("dpi", (0,))[0],
            mb="%.2f" % (os.path.getsize(os.path.join(OUT, "jianghuai-%s.jpg" % p["key"])) / 1048576),
            chars=len(lay["glyphs"]), cols=len(lay["cols"]),
            pool="%.1f" % a[S.WATERLINE + 60:].mean(),
        ))
    return rows


def report():
    rows = measures()
    log = open(os.path.join(PROOF, "verify.log"), encoding="utf-8").read()
    total = [l for l in log.splitlines() if l.startswith("合计")]
    out = ["# proof · 《江淮之间》三张海报\n"]
    out.append("| 张 | 单张名 | 像素 | dpi | 体积 | 字数 | 列数 | 墨池亮度 |")
    out.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        out.append("| %s | %s | %s | %s | %s MB | %d | %d | %s |" % (
            r["key"], r["title"], r["size"], r["dpi"], r["mb"], r["chars"], r["cols"], r["pool"]))
    out.append("")
    out.append("断言：**%s**（全文见 `proof/verify.log`）" % (total[0] if total else "见日志"))
    out.append("")
    out.append("联系表：`proof/contact-sheet.jpg`（三张并排 + 水线标注 + 10cm 尺标）")
    open(os.path.join(PROOF, "report.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    os.makedirs(PROOF, exist_ok=True)
    sheet()
    report()
    print("  联系表 → proof/contact-sheet.jpg")
    print("  量测报告 → proof/report.md")
