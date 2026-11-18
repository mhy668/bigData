#!/bin/bash
# ==============================================================
# 实验四 步骤1：生成 K-Means 实验数据集（固定随机种子）
# ==============================================================
LAB="$HOME/bigdata-lab4"
cd "$LAB"

echo "== 1) 生成 20000 个二维整数点（5 个高斯簇，随机种子 42） =="
echo "\$ python3 data/gen_dataset.py"
python3 data/gen_dataset.py

echo
echo "== 2) 数据集预览（前 5 行） =="
echo "\$ head -5 data/points.csv"
head -5 data/points.csv

echo
echo "== 3) 数据规模 =="
echo "\$ wc -l data/points.csv"
wc -l data/points.csv
echo "每行格式：点编号,x坐标,y坐标"
