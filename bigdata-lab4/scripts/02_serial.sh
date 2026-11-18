#!/bin/bash
# ==============================================================
# 实验四 步骤2：K-Means 的非并行化（单机 Python）实现
# ==============================================================
LAB="$HOME/bigdata-lab4"
cd "$LAB"

echo "== 串行 K-Means：5 个簇，固定 10 次迭代 =="
echo "\$ python3 code/kmeans_serial.py"
python3 code/kmeans_serial.py

echo
echo "== 串行结果 =="
echo "\$ cat results/serial_centroids.txt"
cat results/serial_centroids.txt
echo "\$ cat results/serial_sizes.txt"
cat results/serial_sizes.txt
echo "\$ cat results/serial_sse.txt"
cat results/serial_sse.txt
echo "\$ head -3 results/serial_assignments.txt（共 $(wc -l < results/serial_assignments.txt) 行）"
head -3 results/serial_assignments.txt
