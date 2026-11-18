# -*- coding: utf-8 -*-
"""构建《江淮之间》三张海报：底图 → 墨池 → 水线 → 字 → 印 → 页脚。

  py -3 scripts/build.py            # 三张全做（约 20 秒）
  py -3 scripts/build.py --only shan

产物（都在 out/）：
  jianghuai-<key>.png   无损母版
  jianghuai-<key>.jpg   交件用（300dpi / RGB / q95 / 4:4:4）
  jianghuai-<key>.svg   分层矢量工程源文件（字是真字，不是描边）
"""
import base64
import io
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import story as S
import layout as L

OUT = os.path.join(ROOT, "out")
BUILD = os.path.join(ROOT, "build")


def font(kind, size):
    return ImageFont.truetype(os.path.join(ROOT, S.FONTS[kind]), size)


def dewatermark(img, box=(0.74, 0.925, 1.0, 1.0), k=15):
    """抹掉源图右下角文生图工具的水印。

    不裁掉——那一角是画（西涧的船、丰乐的溪口都在附近）。做法是把水印框里
    换成中值滤波后的颜色：水印是细白字，压在深色水上，中值一过就没了，
    而这一块成品里又在 90% 墨池下，看不出补过。
    """
    iw, ih = img.size
    x0, y0, x1, y1 = int(box[0] * iw), int(box[1] * ih), int(box[2] * iw), int(box[3] * ih)
    patch = img.crop((x0, y0, x1, y1)).filter(ImageFilter.MedianFilter(size=k))
    img = img.copy()
    img.paste(patch, (x0, y0))
    return img


def cover(img, w, h, vpos):
    """等比放大到铺满，再按 vpos 取垂直位置（0=留上，1=留下）。"""
    iw, ih = img.size
    s = max(w / iw, h / ih)
    nw, nh = int(round(iw * s)), int(round(ih * s))
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = int(round((nh - h) * vpos))
    return img.crop((x, y, x + w, y + h))


def pool_color(img):
    """墨池的颜色：取画面最底部一条的中位色，再压暗，保证白字压得住。"""
    a = np.asarray(img).astype(np.float32)
    band = a[int(S.H * 0.94):, :, :]
    med = np.median(band.reshape(-1, 3), axis=0)
    return tuple(int(v * 0.55) for v in med)


def clarity(img, k=0.25, radius=2.0):
    """只对水线以上做一点微对比：雾不是"死灰"，绢纹与树影要立起来。

    做法是反锐化掩膜（unsharp），k 很小，不制造光晕；水线以下的字区一点不动。
    """
    a = np.asarray(img).astype(np.float32)
    blur = np.asarray(img.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32)
    sharp = a + k * (a - blur)
    top = sharp[:S.WATERLINE]
    out = a.copy()
    out[:S.WATERLINE] = top
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def lift_subject(img, focus):
    """给题眼留一口气：主体处一层椭圆形的柔和提亮（不改构图、不改颜色关系）。"""
    if not focus:
        return img
    cx, cy, rx, ry, amt = focus
    a = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
    d = ((xx - cx * S.W) / (rx * S.W)) ** 2 + ((yy - cy * S.H) / (ry * S.H)) ** 2
    w = np.clip(1 - d, 0, 1) ** 1.6
    gain = (1 + amt * w)[:, :, None]
    return Image.fromarray(np.clip(a * gain, 0, 255).astype(np.uint8))


def draw_pool(img, color):
    """从水线往下压一层墨：alpha 0.52 → 0.95，让字有地方落，也让"水"真的深下去。"""
    a = np.asarray(img).astype(np.float32)
    y = np.arange(S.H, dtype=np.float32)
    t = np.clip((y - S.WATERLINE) / float(S.H - S.WATERLINE), 0, 1)
    ramp = 0.72 + 0.24 * t ** 0.9
    ramp = np.where(y >= S.WATERLINE, ramp, 0.0)   # 水线以上一点都不压
    alpha = ramp[:, None, None]
    overlay = np.array(color, dtype=np.float32)[None, None, :]
    a = a * (1 - alpha) + overlay * alpha
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def draw_rules(img, p):
    d = ImageDraw.Draw(img, "RGBA")
    for key, color, h in (("_rule", p["accent"], 3), ("_foot_rule", p["ink_dim"], 2)):
        if key not in p:
            continue
        x0, y0, x1, y1 = p[key]
        d.rectangle([x0, y0, x1, y0 + h], fill=tuple(color) + (170,))
    if "_aigc_box" in p:
        x0, y0, x1, y1 = p["_aigc_box"]
        d.rectangle([x0, y0, x1, y1], fill=tuple(p["accent"]) + (238,))
    return img



def draw_waterline(img, accent):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, S.WATERLINE - 3, S.W, S.WATERLINE + 3], fill=accent + (235,))
    # 水线下 14px 的一道淡影，让线"压"在画面上
    d.rectangle([0, S.WATERLINE + 4, S.W, S.WATERLINE + 18], fill=accent + (26,))
    return img


def draw_glyphs(img, glyphs):
    d = ImageDraw.Draw(img)
    cache = {}
    for g in glyphs:
        k = (g["font"], g["size"])
        if k not in cache:
            cache[k] = font(g["font"], g["size"])
        d.text((g["x"], g["y"]), g["ch"], font=cache[k], fill=tuple(g["color"]), anchor="ls")
    return img


def draw_marks(img, marks):
    d = ImageDraw.Draw(img, "RGBA")
    for m in marks:
        box = [m["cx"] - m["r"], m["cy"] - m["r"], m["cx"] + m["r"], m["cy"] + m["r"]]
        if m["kind"] == "dot":
            d.ellipse(box, fill=tuple(m["color"]) + (255,))
        else:
            d.ellipse(box, outline=tuple(m["color"]) + (255,), width=max(3, m["r"] // 3))
    return img


def draw_seal(img, p):
    x0, y0, x1, y1 = p["_seal_box"]
    accent = tuple(p["accent"])
    paper = tuple(p["ink"])
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0, y0, x1, y1], fill=accent + (242,))
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=paper + (215,), width=4)
    chars = p["seal"]
    fsize = int((y1 - y0) * 0.42)
    f = font("brush", fsize)
    n = len(chars)
    step = int(fsize * 1.06)
    total = step * n
    cy = y0 + (y1 - y0 - total) // 2 + fsize
    cx = (x0 + x1) // 2
    for ch in chars:
        d.text((cx, cy), ch, font=f, fill=paper + (255,), anchor="ms")
        cy += step
    return img


def to_jpg(img):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=95, subsampling=0, dpi=(S.DPI, S.DPI),
                            optimize=True, progressive=False)
    return buf.getvalue()


def to_svg(p, glyphs, marks, bg_jpg):
    b64 = base64.b64encode(bg_jpg).decode("ascii")
    serif = base64.b64encode(open(os.path.join(ROOT, S.FONTS["serif"]), "rb").read()).decode()
    brush = base64.b64encode(open(os.path.join(ROOT, S.FONTS["brush"]), "rb").read()).decode()
    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               'width="%d" height="%d" viewBox="0 0 %d %d">' % (S.W, S.H, S.W, S.H))
    out.append('<defs><style type="text/css"><![CDATA[')
    out.append('@font-face{font-family:"JHSerif";src:url(data:font/ttf;base64,%s);}' % serif)
    out.append('@font-face{font-family:"JHBrush";src:url(data:font/ttf;base64,%s);}' % brush)
    out.append('.s{font-family:"JHSerif";}.b{font-family:"JHBrush";}')
    out.append(']]></style></defs>')
    out.append('<g id="底图-墨池（AI 生成）">')
    out.append('<image x="0" y="0" width="%d" height="%d" xlink:href="data:image/jpeg;base64,%s"/>'
               % (S.W, S.H, b64))
    out.append('</g>')
    out.append('<g id="水线">')
    out.append('<rect x="0" y="%d" width="%d" height="6" fill="#%02x%02x%02x" opacity="0.92"/>'
               % (S.WATERLINE - 3, S.W, *p["accent"]))
    out.append('</g>')
    out.append('<g id="引文">')
    for g in glyphs:
        cls = "b" if g["font"] == "brush" else "s"
        out.append('<text class="%s" x="%d" y="%d" font-size="%d" fill="#%02x%02x%02x">%s</text>'
                   % (cls, g["x"], g["y"], g["size"], *g["color"], g["ch"]))
    out.append('</g>')
    out.append('<g id="句读">')
    for m in marks:
        fill = "#%02x%02x%02x" % tuple(m["color"])
        if m["kind"] == "dot":
            out.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (m["cx"], m["cy"], m["r"], fill))
        else:
            out.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="%d"/>'
                       % (m["cx"], m["cy"], m["r"], fill, max(3, m["r"] // 3)))
    out.append('</g>')
    x0, y0, x1, y1 = p["_seal_box"]
    out.append('<g id="印">')
    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="#%02x%02x%02x" opacity="0.95"/>'
               % (x0, y0, x1 - x0, y1 - y0, *p["accent"]))
    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#%02x%02x%02x" '
               'stroke-width="4" opacity="0.85"/>'
               % (x0 + 9, y0 + 9, x1 - x0 - 18, y1 - y0 - 18, *p["ink"]))
    n = len(p["seal"])
    fsize = int((y1 - y0) * 0.42)
    step = int(fsize * 1.06)
    cy = y0 + (y1 - y0 - step * n) // 2 + fsize
    for ch in p["seal"]:
        out.append('<text class="b" x="%d" y="%d" font-size="%d" fill="#%02x%02x%02x" '
                   'text-anchor="middle">%s</text>' % ((x0 + x1) // 2, cy, fsize, *p["ink"], ch))
        cy += step
    out.append('</g>')
    out.append('</svg>')
    return "\n".join(out)


def build_one(p, write_svg=True):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    src = dewatermark(Image.open(os.path.join(ROOT, p["plate"])).convert("RGB"))
    img = cover(src, S.W, S.H, p["vpos"])
    img = clarity(img, k=p.get("clarity", 0.25))
    img = draw_pool(img, pool_color(img))
    img = lift_subject(img, p.get("focus"))
    img = draw_waterline(img, p["accent"])
    img.save(os.path.join(BUILD, "bg-%s.png" % p["key"]), dpi=(S.DPI, S.DPI))

    glyphs, marks, cols = L.layout(p)
    img = draw_rules(img, p)
    img = draw_glyphs(img, glyphs)
    img = draw_marks(img, marks)
    img = draw_seal(img, p)

    png = os.path.join(OUT, "jianghuai-%s.png" % p["key"])
    img.save(png, dpi=(S.DPI, S.DPI))
    jpg_bytes = to_jpg(img)
    jpg = os.path.join(OUT, "jianghuai-%s.jpg" % p["key"])
    open(jpg, "wb").write(jpg_bytes)
    if write_svg:
        svg = to_svg(p, glyphs, marks, jpg_bytes)
        open(os.path.join(OUT, "jianghuai-%s.svg" % p["key"]), "w",
             encoding="utf-8", newline="\n").write(svg)

    json.dump(dict(key=p["key"], glyphs=glyphs, marks=marks, cols=cols,
                   seal=p["_seal_box"], waterline=S.WATERLINE,
                   pool=pool_color(Image.open(png).convert("RGB"))),
              open(os.path.join(BUILD, "layout-%s.json" % p["key"]), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("  %-5s %s  %d 字  %d 句读  %.2f MB" % (
        p["key"], os.path.basename(jpg), len(glyphs), len(marks),
        os.path.getsize(jpg) / 1024 / 1024))


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    for p in S.POSTERS:
        if only and p["key"] != only:
            continue
        build_one(p)


if __name__ == "__main__":
    main()
