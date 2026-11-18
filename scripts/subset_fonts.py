# -*- coding: utf-8 -*-
"""把两套字体裁成这张海报用得到的字。

  py -3 scripts/subset_fonts.py            # 生成 assets/fonts/*-Subset.ttf
  py -3 scripts/subset_fonts.py --check     # 只核对：现有子集够不够用（clone 里跑这个）

为什么要子集：全量 Noto Serif SC 是 25 MB，随包太重；子集只留用到的字，
verify.py 再断言"缺字 = 0"，改字忘了重跑就会当场 FAIL。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import story as S

SRC = {
    "serif": os.path.join(ROOT, "assets", "fonts", "src", "NotoSerifSC-VF.ttf"),
    "brush": os.path.join(ROOT, "assets", "fonts", "src", "MaShanZheng.ttf"),
}
OUT = {
    "serif": os.path.join(ROOT, "assets", "fonts", "NotoSerifSC-Subset.ttf"),
    "brush": os.path.join(ROOT, "assets", "fonts", "MaShanZheng-Subset.ttf"),
}


def charset():
    s = set()
    s |= set(S.SERIES)
    s |= set(S.FOOT_AI) | set(S.FOOT_SERIES)
    s |= set("引地标方向　｜·，。、（）《》")
    s |= set("0123456789AI")
    for p in S.POSTERS:
        s |= set(p["title"]) | set(p["direction"]) | set(p["landmark"])
        s |= set(p["where"]) | set(p["source"]) | set(p["seal"])
        for col in p["quote"]:
            s |= set(col)
        s |= set(p["no"])
    return "".join(sorted(s))


def main():
    from fontTools import subset
    from fontTools.ttLib import TTFont

    chars = charset()
    print("需要 %d 个字" % len(chars))

    if "--check" in sys.argv:
        for k, path in OUT.items():
            f = TTFont(path)
            cmap = f.getBestCmap()
            miss = [c for c in chars if ord(c) not in cmap]
            print("  %-6s %-46s 缺字 %d %s" % (k, os.path.basename(path), len(miss), "".join(miss)))
        return

    for k, path in SRC.items():
        opts = subset.Options()
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        opts.recalc_bounds = True
        opts.drop_tables += ["DSIG"]
        font = subset.load_font(path, opts)
        sub = subset.Subsetter(options=opts)
        sub.populate(text=chars)
        sub.subset(font)
        subset.save_font(font, OUT[k], opts)
        print("  %-6s %8.1f KB → %8.1f KB  %s" % (
            k, os.path.getsize(path) / 1024, os.path.getsize(OUT[k]) / 1024,
            os.path.basename(OUT[k])))


if __name__ == "__main__":
    main()
