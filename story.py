# -*- coding: utf-8 -*-
"""《江淮之间》——三张海报的唯一真相源。

改字、改色、改引文，只改这个文件；版式、PNG、SVG、文档、阅稿页都由它生成。
每句引文都在 docs/01-STORY.md 里核过出处；verify.py 会拿 CANON 逐字比对——
不是肉眼比，是去标点后的字符串相等。
"""

SERIES = "江淮之间"
W, H = 2480, 3508          # A4 竖版 @300dpi
DPI = 300
WATERLINE = 2245           # 水线 y：三张逐像素相同，是系列唯一的硬骨架
MARGIN_X = 180
TOP = 210

FONTS = {
    "serif": "assets/fonts/NotoSerifSC-Subset.ttf",
    "brush": "assets/fonts/MaShanZheng-Subset.ttf",
}

POSTERS = [
    dict(
        key="shan", no="一", title="酿泉",
        direction="山水寻幽",
        landmark="琅琊山 · 酿泉 · 醉翁亭",
        where="安徽滁州 · 城西南",
        quote=[
            "环滁皆山也",
            "其西南诸峰",
            "林壑尤美",
            "望之蔚然而深秀者",
            "琅琊也",
            "山行六七里",
            "渐闻水声潺潺",
            "而泻出于两峰之间者",
            "酿泉也",
        ],
        source="欧阳修《醉翁亭记》　庆历六年（1046）",
        seal="酿泉",
        plate="assets/plates/shan.png",
        vpos=0.42,
        ink=(247, 245, 238), ink_dim=(226, 224, 214), top_ink=(60, 62, 56),
        accent=(168, 54, 40),
    ),
    dict(
        key="jian", no="二", title="西涧",
        direction="人文寻脉",
        landmark="滁州西涧 · 俗名上马河",
        where="安徽滁州 · 城西",
        quote=[
            "独怜幽草涧边生",
            "上有黄鹂深树鸣",
            "春潮带雨晚来急",
            "野渡无人舟自横",
        ],
        source="韦应物《滁州西涧》　唐 · 刺滁时（约 783）",
        seal="西涧",
        plate="assets/plates/jian.png",
        vpos=0.55,
        ink=(243, 246, 246), ink_dim=(214, 222, 224), top_ink=(226, 232, 234),
        accent=(170, 58, 44),
    ),
    dict(
        key="tian", no="三", title="丰乐",
        direction="烟火寻踪",
        landmark="丰山 · 幽谷泉 · 丰乐亭",
        where="安徽滁州 · 城西",
        quote=[
            "修既治滁之明年",
            "夏，始饮滁水而甘",
            "其上丰山耸然而特立",
            "下则幽谷窈然而深藏",
            "中有清泉",
            "滃然而仰出",
            "民生不见外事",
            "而安于畎亩衣食",
        ],
        source="欧阳修《丰乐亭记》　庆历丙戌六月（1046）",
        seal="丰乐",
        plate="assets/plates/tian.png",
        vpos=0.5,
        ink=(250, 246, 235), ink_dim=(228, 222, 206), top_ink=(64, 52, 38),
        accent=(158, 50, 34),
    ),
]

# 校勘：去标点后的原文，与 docs/01-STORY.md 的引文逐字对齐
CANON = {
    "shan": "环滁皆山也其西南诸峰林壑尤美望之蔚然而深秀者琅琊也山行六七里渐闻水声潺潺而泻出于两峰之间者酿泉也",
    "jian": "独怜幽草涧边生上有黄鹂深树鸣春潮带雨晚来急野渡无人舟自横",
    "tian": "修既治滁之明年夏始饮滁水而甘其上丰山耸然而特立下则幽谷窈然而深藏中有清泉滃然而仰出民生不见外事而安于畎亩衣食",
}

FOOT_AI = "本作品由 AI 生成 · AIGC"
FOOT_SERIES = "诗文里的滁州 · AI 海报赛道"
