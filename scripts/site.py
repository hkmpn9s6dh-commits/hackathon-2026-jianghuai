# -*- coding: utf-8 -*-
"""生成阅稿页 site/index.html + site/img/*.jpg（1200px 宽的预览图）。

  py -3 scripts/site.py
"""
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import story as S

OUT = os.path.join(ROOT, "out")
SITE = os.path.join(ROOT, "site")
IMG = os.path.join(SITE, "img")

HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>江淮之间 · 诗文里的滁州 · 三张海报</title>
<style>
  :root{
    --paper:#f3f0e8; --ink:#242220; --dim:#6b665e; --red:#a33628; --line:#d9d3c6;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);
       font-family:"Noto Serif SC","Songti SC",serif;line-height:1.85}
  .wrap{max-width:1120px;margin:0 auto;padding:72px 28px 96px}
  header{border-bottom:1px solid var(--line);padding-bottom:28px;margin-bottom:56px}
  .kicker{font-size:13px;letter-spacing:.32em;color:var(--red);margin:0 0 18px}
  h1{font-size:clamp(34px,5.4vw,58px);margin:0;letter-spacing:.16em;font-weight:600}
  .sub{margin:14px 0 0;color:var(--dim);font-size:15px;letter-spacing:.06em}
  .lead{margin:44px 0 60px;font-size:17px;max-width:44em}
  .lead b{font-weight:600;box-shadow:inset 0 -0.5em 0 #e6dcc6}
  .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px}
  @media(max-width:900px){.grid{grid-template-columns:1fr;gap:44px}}
  figure{margin:0}
  figure img{width:100%;display:block;border:1px solid #cfc8ba;box-shadow:0 18px 44px -26px rgba(0,0,0,.55)}
  figcaption{margin-top:14px;font-size:13px;color:var(--dim);letter-spacing:.04em}
  figcaption b{color:var(--ink);font-weight:600;letter-spacing:.14em}
  .quote{margin-top:6px;color:var(--dim);font-size:12.5px;line-height:1.7}
  section{margin-top:76px;border-top:1px solid var(--line);padding-top:34px}
  h2{font-size:20px;letter-spacing:.14em;margin:0 0 18px}
  p{max-width:46em}
  dl{display:grid;grid-template-columns:8em 1fr;gap:8px 18px;font-size:14.5px;max-width:54em}
  dt{color:var(--dim)}dd{margin:0}
  .ai{margin-top:44px;padding:18px 20px;border:1px solid var(--red);color:var(--red);
      font-size:13.5px;letter-spacing:.04em;max-width:54em}
  footer{margin-top:56px;color:var(--dim);font-size:12.5px;letter-spacing:.06em}
  a{color:var(--red)}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="kicker">诗文里的滁州 · AI 海报赛道 · 投稿阅稿页</p>
    <h1>江淮之间</h1>
    <p class="sub">三处水 · 一条水线 · 2480×3508 @300dpi · 三张一组</p>
  </header>

  <p class="lead">
    欧阳修在《丰乐亭记》里写滁州：<b>「今滁介于江、淮之间」</b>。这句话是这组海报的起点。
    滁州的三处水——琅琊山的酿泉、城西的西涧、丰山下的幽谷泉——各自被一首诗文钉住过一次。
    三张海报把诗放进水里：水线以上是画，以下是墨池，<b>字沉在水面下，像倒影，也像被水吞掉的句子</b>。
    水线在三张里是同一行像素（y=2245），那是这套东西唯一的硬骨架。
  </p>

  <div class="grid">
__FIGURES__
  </div>

  <section>
    <h2>三张各是什么</h2>
    <dl>
      <dt>一 · 酿泉</dt><dd>山水寻幽　琅琊山 · 酿泉 · 醉翁亭　引欧阳修《醉翁亭记》（1046）</dd>
      <dt>二 · 西涧</dt><dd>人文寻脉　滁州西涧（俗名上马河）　引韦应物《滁州西涧》（唐，约 783）</dd>
      <dt>三 · 丰乐</dt><dd>烟火寻踪　丰山 · 幽谷泉 · 丰乐亭　引欧阳修《丰乐亭记》（1046）</dd>
    </dl>
  </section>

  <section>
    <h2>为什么这样做</h2>
    <p>
      底图是文生图的绢本设色山水；水线、墨池、竖排引文、句读记号、朱印、页脚与「AI 生成」标签
      全部由构建脚本逐字排版生成，不是手工拼的图。三张共用同一个字号（92px，由最长那一列反解），
      同一个印的尺寸（156px），同一行水线（2245）——这三个数被写进 <code>scripts/verify.py</code> 的断言里，
      改字忘了重算就会 FAIL。
    </p>
    <p>
      交付除三张 JPG 外，另附<b>分层 SVG 工程源文件</b>：底图、水线、引文（真文字，不是描边）、句读、印、层名都在，
      可直接在 Illustrator / Figma / Inkscape 里改字改色。
    </p>
  </section>

  <div class="ai">
    本页全部作品由 AI 生成（AIGC）：底图为文生图模型输出，版式与文字由程序生成。
    依据《人工智能生成合成内容标识办法》，每张成品右下角带「AI 生成」显式标识，页脚亦注明。
  </div>

  <footer>
    江淮之间 · 诗文里的滁州 · AI 海报赛道　｜　2026-11　｜　张一
  </footer>
</div>
</body>
</html>
"""


def main():
    os.makedirs(IMG, exist_ok=True)
    figs = []
    for p in S.POSTERS:
        src = os.path.join(OUT, "jianghuai-%s.jpg" % p["key"])
        im = Image.open(src).convert("RGB")
        im.thumbnail((1200, 1700), Image.LANCZOS)
        dst = os.path.join(IMG, "%s.jpg" % p["key"])
        im.save(dst, quality=90, dpi=(150, 150))
        q = "".join(p["quote"][:2]) + "……" if len(p["quote"]) > 2 else "".join(p["quote"])
        figs.append("""    <figure>
      <img src="img/%s.jpg" alt="%s · %s">
      <figcaption><b>%s · %s</b><br>%s<br><span class="quote">%s　—　%s</span></figcaption>
    </figure>""" % (p["key"], p["title"], p["direction"], p["no"], p["title"], p["landmark"], q, p["source"]))
    html = HTML.replace("__FIGURES__", "\n".join(figs))
    open(os.path.join(SITE, "index.html"), "w", encoding="utf-8", newline="\n").write(html)
    print("写出 site/index.html 与 %d 张预览图" % len(S.POSTERS))


if __name__ == "__main__":
    main()
