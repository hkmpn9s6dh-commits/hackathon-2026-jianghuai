#!/usr/bin/env bash
# 一条命令从零到可交：《江淮之间》三张海报
#   bash verify.sh
set -e
cd "$(dirname "$0")"
PY=${PY:-py -3}

echo "== 0. 依赖 =="
$PY -c "import PIL, numpy, fontTools; print('依赖齐')"

echo "== 1. 图版与字体 =="
$PY - <<'EOF'
import os, sys
sys.path.insert(0, '.')
import story as S
miss = [p["plate"] for p in S.POSTERS if not os.path.exists(p["plate"])]
print("图版 %d 张%s" % (len(S.POSTERS), "" if not miss else "，缺：" + str(miss)))
sys.exit(1 if miss else 0)
EOF
$PY scripts/subset_fonts.py --check

echo "== 2. 版式表与单源是否一致 =="
$PY scripts/gen_docs.py --check

echo "== 3. 构建 =="
$PY scripts/build.py

echo "== 4. 闸 C 逐条 =="
$PY scripts/verify.py

echo "== 5. 证据 =="
$PY scripts/proof.py
echo "全部通过。"
