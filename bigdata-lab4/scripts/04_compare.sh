#!/bin/bash
# ==============================================================
# 实验四 步骤4：对比串行与并行两种实现的聚类结果
# ==============================================================
LAB="$HOME/bigdata-lab4"
cd "$LAB"

echo "== 对比两类实现的输出是否完全一致 =="
for f in centroids sizes sse assignments; do
    if diff -q "results/serial_$f.txt" "results/parallel_$f.txt" >/dev/null 2>&1; then
        echo "  $f: 完全一致（$(wc -l < "results/serial_$f.txt") 行）"
    else
        echo "  $f: 不一致！"
        diff "results/serial_$f.txt" "results/parallel_$f.txt" | head -5
    fi
done

echo
echo "== md5 校验（成对相同即逐字节一致） =="
md5sum results/serial_centroids.txt results/parallel_centroids.txt
md5sum results/serial_sizes.txt results/parallel_sizes.txt
md5sum results/serial_sse.txt results/parallel_sse.txt
md5sum results/serial_assignments.txt results/parallel_assignments.txt
