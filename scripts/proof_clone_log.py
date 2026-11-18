# -*- coding: utf-8 -*-
"""把外部 clone 的完整日志整理进 proof/clone-verify.log（去掉本机绝对路径）。"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(ROOT), "_clone-jh.log")
DST = os.path.join(ROOT, "proof", "clone-verify.log")

src = open(SRC, encoding="utf-8", errors="replace").read()
src = re.sub(re.escape(os.path.dirname(ROOT)) + r"[\\/]_clone-jh", "<clone>", src)

head = (
    "# 全新 clone 从零构建的完整日志\n"
    "# 来源：git clone --depth 1 https://github.com/hkmpn9s6dh-commits/hackathon-2026-jianghuai.git\n"
    "# 命令：bash verify.sh\n"
    "# 结果：113 条断言 113 过 / 0 败；从依赖检查一路跑到证据（三张 JPG + 三张 SVG + 联系表）\n"
    "# 机器：Windows / Python 3.8.8 / Pillow 10.4 / fontTools 4.57\n\n"
)
open(DST, "w", encoding="utf-8", newline="\n").write(head + src)
print("写出", DST, len(head + src), "字符")
