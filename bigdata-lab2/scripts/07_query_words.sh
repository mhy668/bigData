#!/bin/bash
# ==============================================================
# 实验二 步骤7：单词检索示例（在倒排索引中查单词）
# ==============================================================
LAB="$HOME/bigdata-lab2"
cd "$LAB"

echo "== 查询 data / hadoop / mapreduce / search / index 五个单词 =="
echo "\$ grep -E \"^(data|hadoop|mapreduce|search|index)[[:space:]]\" results/part-r-00000"
grep -E "^(data|hadoop|mapreduce|search|index)[[:space:]]" results/part-r-00000

echo
echo "== 单个单词查询示例：hadoop =="
echo "\$ grep -E \"^hadoop[[:space:]]\" results/part-r-00000"
grep -E "^hadoop[[:space:]]" results/part-r-00000

# 保存查询结果供报告引用
{
    echo "== head -20 =="
    head -20 results/part-r-00000
    echo
    echo "== grep data/hadoop/mapreduce/search/index =="
    grep -E "^(data|hadoop|mapreduce|search|index)[[:space:]]" results/part-r-00000
} > results/queries.txt
echo
echo "查询输出已保存到 results/queries.txt"
