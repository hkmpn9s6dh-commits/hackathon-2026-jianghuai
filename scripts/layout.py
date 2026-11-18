# -*- coding: utf-8 -*-
"""版式：把一张海报的所有字算成"逐个字的坐标"。

PNG 与 SVG 都从这一份坐标画出来，所以两者永远不会不一致。
字号由三张里最长的那一列统一决定 —— 系列共用一套字。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import story as S

DOT = "，"
RING = "。"

W, H = S.W, S.H
POEM_TOP = 2352
POEM_BOTTOM = 3276
GLYPH_STEP = 1.06          # 行内字距
COL_STEP = 1.62            # 列距


def _maxchars(cols):
    return max(len([c for c in col if c not in DOT + RING]) for col in cols)


def global_size():
    """三张共用同一字号：取最长那列能放下的最大字号。"""
    mc = max(_maxchars(p["quote"]) for p in S.POSTERS)
    avail = POEM_BOTTOM - POEM_TOP
    return min(100, int(avail / (mc * GLYPH_STEP)))


def layout(p, size=None):
    """返回 (glyphs, marks, cols)。"""
    cols = p["quote"]
    size = size or global_size()
    step = int(size * GLYPH_STEP)
    colgap = int(size * COL_STEP)
    x_right = W - 230

    glyphs, marks = [], []
    for i, col in enumerate(cols):
        x = x_right - i * colgap
        y = POEM_TOP
        for ch in col:
            if ch in DOT + RING:
                marks.append(dict(kind="dot" if ch == DOT else "ring",
                                  cx=x + int(size * 0.66), cy=y + int(size * 0.28),
                                  r=max(7, int(size * 0.075)), color=p["ink"]))
                continue
            glyphs.append(dict(ch=ch, x=x, y=y + size, size=size, font="serif", color=p["ink"]))
            y += step

    # 落款：单张名（马善政）压到左边距，字头越过水线；印在名字底下
    name_size = 340
    nstep = int(name_size * 1.02)
    name_x = S.MARGIN_X - 8
    n = len(p["title"])
    seal_size = 156
    gap = 34
    block_h = n * nstep + gap + seal_size
    top = 3270 - block_h
    ny = top
    for ch in p["title"]:
        glyphs.append(dict(ch=ch, x=name_x, y=ny + name_size, size=name_size,
                           font="brush", color=p["ink"]))
        ny += nstep
    sx0 = name_x + (name_size - seal_size) // 2
    sy0 = top + n * nstep + gap
    p["_seal_box"] = (sx0, sy0, sx0 + seal_size, sy0 + seal_size)

    # 页脚三行（系列号 / 引文出处 / 地标 / 方向与 AI 标识）
    fy = 3318
    lines = [
        "引　%s" % p["source"],
        "地标　%s（%s）" % (p["landmark"], p["where"]),
        "%s · %s　｜　方向 %s　｜　%s" % (S.SERIES, p["no"], p["direction"], S.FOOT_SERIES),
    ]
    for ln in lines:
        fx = S.MARGIN_X
        fsize = 32
        for ch in ln:
            if ch == "　":
                fx += fsize
                continue
            if ch == " ":
                fx += int(fsize * 0.5)
                continue
            color = p["ink_dim"]
            glyphs.append(dict(ch=ch, x=fx, y=fy + fsize, size=fsize, font="serif", color=color))
            fx += int(fsize * (1.02 if ord(ch) > 0x2E80 else 0.52))
        fy += 54
    p["_foot_rule"] = (S.MARGIN_X, 3300, W - S.MARGIN_X, 3302)

    # 右下角 AIGC 显式标识（红底白字，合规标识也是版面上的一个重音）
    tag_w, tag_h = 176, 56
    tx0, ty0 = W - S.MARGIN_X - tag_w, 3306
    p["_aigc_box"] = (tx0, ty0, tx0 + tag_w, ty0 + tag_h)
    label = "AI 生成"
    fs = 30
    total = sum(int(fs * (1.0 if ord(c) > 0x2E80 else 0.5)) for c in label)
    cx = tx0 + (tag_w - total) // 2
    for ch in label:
        glyphs.append(dict(ch=ch, x=cx, y=ty0 + 40, size=fs, font="serif", color=(252, 250, 244)))
        cx += int(fs * (1.0 if ord(ch) > 0x2E80 else 0.5))

    return glyphs, marks, cols


def ink_extent(glyphs):
    return (min(g["x"] for g in glyphs),
            min(g["y"] - g["size"] for g in glyphs),
            max(g["x"] + g["size"] for g in glyphs),
            max(g["y"] for g in glyphs))
