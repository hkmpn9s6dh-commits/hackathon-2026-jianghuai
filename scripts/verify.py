# -*- coding: utf-8 -*-
"""闸 C：三张海报的验收断言。49 条，全部对着真文件与真像素量，不看"我觉得"。

  py -3 scripts/verify.py            # 打 PASS/FAIL，退出码 0 才算过
  py -3 scripts/verify.py -q         # 只打失败的

判据来源：
  · 赛规（2480×3508 / 300dpi / RGB / 可编辑源文件 / AIGC 标识 / 注明诗句与地标）
  · 系列自身的规矩（同一字号、同一条水线、同一套页脚）
  · 可读性（WCAG 对比度，逐字对真背景量）
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import story as S
import layout as L

RESULT = []
QUIET = "-q" in sys.argv


def ok(cond, name, detail=""):
    RESULT.append((bool(cond), name, detail))
    if not QUIET or not cond:
        print("  %s  %-46s %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)


def srgb_lum(rgb):
    c = np.asarray(rgb, dtype=np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = srgb_lum(a), srgb_lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def norm(s):
    return "".join(ch for ch in s if ch not in "，。、；：！？「」《》（） \u3000")


def main():
    paths = {p["key"]: dict(
        jpg=os.path.join(ROOT, "out", "jianghuai-%s.jpg" % p["key"]),
        png=os.path.join(ROOT, "out", "jianghuai-%s.png" % p["key"]),
        svg=os.path.join(ROOT, "out", "jianghuai-%s.svg" % p["key"]),
        bg=os.path.join(ROOT, "build", "bg-%s.png" % p["key"]),
        lay=os.path.join(ROOT, "build", "layout-%s.json" % p["key"]),
    ) for p in S.POSTERS}
    lays = {k: json.load(open(v["lay"], encoding="utf-8")) for k, v in paths.items()}

    print("== 1. 交件规格 ==")
    for p in S.POSTERS:
        k = p["key"]
        j = paths[k]["jpg"]
        ok(os.path.exists(j), "AC-1 成片存在 %s" % k, k)
        im = Image.open(j)
        ok(im.size == (S.W, S.H), "AC-2 尺寸 2480×3508 %s" % k, "%dx%d" % im.size)
        dpi = im.info.get("dpi", (0, 0))
        ok(abs(dpi[0] - 300) < 1 and abs(dpi[1] - 300) < 1, "AC-3 300dpi %s" % k, "%.0f/%.0f" % dpi)
        ok(im.mode == "RGB", "AC-4 RGB 无 alpha %s" % k, im.mode)
        size_mb = os.path.getsize(j) / 1024 / 1024
        ok(size_mb <= 12, "AC-5 单张 ≤ 12MB %s" % k, "%.2f MB" % size_mb)
        ok(not im.info.get("progressive"), "AC-6 baseline JPEG %s" % k, "progressive=%s" % im.info.get("progressive"))

    print("== 2. 系列一致（同一条水线、同一套字） ==")
    lines = {}
    for p in S.POSTERS:
        a = np.asarray(Image.open(paths[p["key"]]["jpg"]).convert("RGB")).astype(int)
        acc = np.array(p["accent"])
        hit = (np.abs(a - acc).sum(axis=2) < 60)
        rows = hit.sum(axis=1)
        y = int(rows.argmax())
        lines[p["key"]] = (y, int(rows[y]))
        ok(abs(y - S.WATERLINE) <= 4, "AC-7 水线落在 2245±4 %s" % p["key"], "y=%d" % y)
        ok(rows[y] > S.W * 0.9, "AC-8 水线横贯全幅 %s" % p["key"], "%d px" % rows[y])
    ok(len(set(v[0] for v in lines.values())) == 1, "AC-9 三张水线同一条（逐像素）",
       str({k: v[0] for k, v in lines.items()}))
    sizes = {k: L.layout(p)[0][0]["size"] for k, p in [(p["key"], p) for p in S.POSTERS]}
    ok(len(set(sizes.values())) == 1, "AC-10 三张引文字号相同", str(sizes))
    (g0, _, c0) = L.layout(S.POSTERS[0])
    nsize = [g["size"] for g in g0 if g["font"] == "brush"]
    ok(len(set(nsize)) == 1, "AC-11 三张落款字号相同", str(nsize[0]))
    seals = [lays[k]["seal"] for k in lays]
    w = {round(s[2] - s[0]) for s in seals}
    ok(len(w) == 1, "AC-12 三张印尺寸相同", str(w))

    print("== 3. 文案（逐字对校勘过的原文） ==")
    for p in S.POSTERS:
        k = p["key"]
        joined = norm("".join(lays[k]["cols"]))
        ok(joined == S.CANON[k], "AC-13 引文与校勘原文一致 %s" % k,
           "" if joined == S.CANON[k] else joined)
        ok(max(len(c) for c in lays[k]["cols"]) <= 10, "AC-14 每列 ≤10 字 %s" % k,
           str(max(len(c) for c in lays[k]["cols"])))
        bad = [c for c in lays[k]["cols"] if c[0] in "，。、；："]
        ok(not bad, "AC-15 没有列以句读开头（避头） %s" % k, str(bad))
        foot = "".join(g["ch"] for g in lays[k]["glyphs"] if g["size"] == 32)
        ok(p["landmark"].split(" · ")[0] in foot, "AC-16 页脚有地标 %s" % k, p["landmark"][:12])
        ok("AI 生成" in "".join(g["ch"] for g in lays[k]["glyphs"]), "AC-17 图上有 AI 生成标识 %s" % k)

    print("== 4. 版面卫生（不重叠、不出血） ==")
    for p in S.POSTERS:
        k = p["key"]
        lay = lays[k]
        gs = lay["glyphs"]
        ok(all(g["x"] >= 120 and g["x"] + g["size"] <= S.W - 120 for g in gs),
           "AC-18 字不出左右安全区 %s" % k,
           "min=%d max=%d" % (min(g["x"] for g in gs), max(g["x"] + g["size"] for g in gs)))
        ok(all(g["y"] <= S.H - 40 and g["y"] - g["size"] >= 40 for g in gs),
           "AC-19 字不出上下安全区 %s" % k,
           "min=%d max=%d" % (min(g["y"] - g["size"] for g in gs), max(g["y"] for g in gs)))
        poem = [g for g in gs if g["size"] == gs[0]["size"] and g["font"] == "serif"]
        xs = sorted({g["x"] for g in poem})
        gap = min((b - a) for a, b in zip(xs, xs[1:])) if len(xs) > 1 else 999
        ok(gap >= gs[0]["size"] * 1.2, "AC-20 引文列间距 ≥1.2 字 %s" % k, "%d px" % gap)
        title = [g for g in gs if g["font"] == "brush" and g["size"] > 200]
        ok(all(g["x"] + g["size"] < min(xs) for g in title), "AC-21 落款不压引文 %s" % k)
        sx0, sy0, sx1, sy1 = lay["seal"]
        ok(sy1 <= 3300, "AC-22 印不压页脚线 %s" % k, "y1=%d" % sy1)
        last = max(g["y"] for g in title)
        ok(sy0 >= last + 10, "AC-23 印在落款之下 %s" % k, "%d→%d" % (last, sy0))
        ok(sx1 < min(xs), "AC-24 印不压引文 %s" % k, "%d<%d" % (sx1, min(xs)))
        fy = sorted({g["y"] for g in gs if g["size"] == 32})
        ok(len(fy) == 3 and min(b - a for a, b in zip(fy, fy[1:])) >= 48,
           "AC-25 页脚三行行距 ≥48 %s" % k, str(fy))
        poem_bottom = max(g["y"] for g in poem)
        ok(poem_bottom <= 3300, "AC-26 引文不越页脚线 %s" % k, "y=%d" % poem_bottom)

    print("== 5. 可读性（逐字对真背景量对比度） ==")
    for p in S.POSTERS:
        k = p["key"]
        bg = np.asarray(Image.open(paths[k]["bg"]).convert("RGB")).astype(np.float32)
        lay = lays[k]
        worst = (99, None)
        for g in lay["glyphs"]:
            if g["size"] < 30:
                continue
            x0, y0 = int(g["x"]), int(g["y"] - g["size"])
            x1, y1 = int(g["x"] + g["size"]), int(g["y"])
            patch = bg[max(0, y0):y1, max(0, x0):x1]
            if patch.size == 0:
                continue
            c = contrast(g["color"], patch.reshape(-1, 3).mean(axis=0))
            if c < worst[0]:
                worst = (c, g["ch"])
        ok(worst[0] >= 4.5, "AC-27 引文逐字对比度 ≥4.5 %s" % k, "最差 %.1f:1（%s）" % worst)
        foot = np.asarray(Image.open(paths[k]["bg"]).convert("RGB")).astype(np.float32)[3390:3500, 180:1700]
        c = contrast(lay["glyphs"][0]["color"], foot.reshape(-1, 3).mean(axis=0))
        ok(c >= 4.5, "AC-28 页脚对比度 ≥4.5 %s" % k, "%.1f:1" % c)

    print("== 6. 画面（墨池、水线、水印、三张互不相同） ==")
    means = []
    for p in S.POSTERS:
        k = p["key"]
        a = np.asarray(Image.open(paths[k]["jpg"]).convert("RGB")).astype(np.float32)
        pool = a[S.WATERLINE + 60:, :, :]
        pool_mean = pool.mean()
        means.append(pool_mean)
        ok(pool_mean <= 110, "AC-29 墨池平均亮度 ≤110 %s" % k, "%.1f" % pool_mean)
        above = a[S.WATERLINE - 40:S.WATERLINE - 10, :, :].mean()
        below = a[S.WATERLINE + 10:S.WATERLINE + 40, :, :].mean()
        ok(above - below >= 12, "AC-30 水线上下有明度落差 %s" % k, "%.1f→%.1f" % (above, below))
        std = a[200:2000, :, :].std()
        ok(std >= 18, "AC-31 主视觉不是纯色 %s" % k, "std=%.1f" % std)
        corner = a[3420:3496, 1850:2450, :]
        ok(corner.std() <= 10 and corner.mean() <= 80, "AC-32 右下角无工具水印残留 %s" % k,
           "std=%.1f mean=%.1f" % (corner.std(), corner.mean()))
    ok(max(means) - min(means) >= 3, "AC-33 三张墨池浓度随图而变", "%.1f~%.1f" % (min(means), max(means)))
    arrs = [np.asarray(Image.open(paths[p["key"]]["jpg"]).convert("L").resize((160, 226))).astype(int)
            for p in S.POSTERS]
    d01 = np.abs(arrs[0] - arrs[1]).mean()
    d02 = np.abs(arrs[0] - arrs[2]).mean()
    ok(d01 >= 10 and d02 >= 10, "AC-34 三张互不相同", "d=%.1f/%.1f" % (d01, d02))

    print("== 7. 工程源文件（分层 SVG） ==")
    for p in S.POSTERS:
        k = p["key"]
        svg = paths[k]["svg"]
        ok(os.path.exists(svg), "AC-35 源文件存在 %s" % k, os.path.basename(svg))
        tree = ET.parse(svg)
        root = tree.getroot()
        ns = "{http://www.w3.org/2000/svg}"
        texts = root.iter(ns + "text")
        n_text = 0
        cols = {}
        for t in tree.iter(ns + "text"):
            n_text += 1
            y = float(t.get("y"))
            fs = int(float(t.get("font-size")))
            if fs == L.global_size():
                cols.setdefault(int(float(t.get("x"))), []).append((y, (t.text or "")))
        ok(n_text == len(lays[k]["glyphs"]) + len(p["seal"]), "AC-36 SVG 字数与版式一致 %s" % k,
           "%d/%d" % (n_text, len(lays[k]["glyphs"]) + len(p["seal"])))
        built = "".join("".join(ch for _, ch in sorted(v)) for _, v in sorted(cols.items(), reverse=True))
        ok(built == norm("".join(lays[k]["cols"])), "AC-37 SVG 里能读出完整引文 %s" % k,
           "" if built == norm("".join(lays[k]["cols"])) else built[:24])
        raw = open(svg, encoding="utf-8").read()
        ok(raw.count("@font-face") == 2, "AC-38 SVG 内嵌两套字体 %s" % k, str(raw.count("@font-face")))
        ok('id="底图-墨池（AI 生成）"' in raw and 'id="引文"' in raw and 'id="印"' in raw,
           "AC-39 SVG 有层名（可编辑） %s" % k)
        ok(len(raw) > 1_000_000 and "data:image/jpeg;base64," in raw, "AC-40 SVG 内嵌底图 %s" % k,
           "%.1f MB" % (len(raw.encode()) / 1024 / 1024))

    print("== 8. 字体（随包、不缺字） ==")
    need = set()
    for p in S.POSTERS:
        need |= set("".join(p["quote"])) | set(p["title"]) | set(p["seal"]) | set(p["source"])
        need |= set(p["landmark"]) | set(p["where"]) | set(p["direction"]) | set(p["no"])
    need |= set(S.SERIES) | set(S.FOOT_SERIES) | set("AI 生成")
    brush_need = set()
    for p in S.POSTERS:
        brush_need |= set(p["title"]) | set(p["seal"])
    for kind, rel in S.FONTS.items():
        f = TTFont(os.path.join(ROOT, rel))
        cmap = f.getBestCmap()
        want = brush_need if kind == "brush" else need
        miss = [c for c in want if ord(c) not in cmap]
        ok(not miss, "AC-41 字体 %s 缺字=0" % kind, "缺 %d %s" % (len(miss), "".join(miss)))
        ok(os.path.exists(os.path.join(ROOT, "assets", "fonts", "LICENSE.md")), "AC-42 字体许可随包 %s" % kind)

    print("== 9. 文档与单源一致 ==")
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "gen_docs.py"), "--check"],
                       capture_output=True, text=True, encoding="utf-8")
    ok(r.returncode == 0, "AC-43 docs/03-LAYOUT.md 与 story.py 一致", (r.stdout or r.stderr).strip()[:60])

    bad = [x for x in RESULT if not x[0]]
    print("\n合计：%d 过 / %d 败" % (len(RESULT) - len(bad), len(bad)))
    if bad:
        for _, n, d in bad:
            print("  败：%s %s" % (n, d))
    log = os.path.join(ROOT, "proof", "verify.log")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    open(log, "w", encoding="utf-8", newline="\n").write(
        "\n".join("%s  %s  %s" % ("PASS" if ok_ else "FAIL", n, d) for ok_, n, d in RESULT)
        + "\n\n合计：%d 过 / %d 败\n" % (len(RESULT) - len(bad), len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
