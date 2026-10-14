#!/bin/bash
# ==============================================================
# 实验二 步骤2：查看停词表 data/stopwords.txt
# ==============================================================
LAB="$HOME/bigdata-lab2"
cd "$LAB"

echo "== 停词表内容（节选前 20 行，# 开头为注释） =="
echo "\$ head -20 data/stopwords.txt"
head -20 data/stopwords.txt

echo
echo "== 停词表规模 =="
echo "\$ grep -v '^#' data/stopwords.txt | wc -l"
grep -v '^#' data/stopwords.txt | wc -l
