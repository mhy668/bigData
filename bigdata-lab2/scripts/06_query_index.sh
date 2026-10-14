#!/bin/bash
# ==============================================================
# 实验二 步骤6：查看倒排索引结果（下载到本地 results/）
# ==============================================================
# 加载 Hadoop 环境变量
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab2"
cd "$LAB"
mkdir -p results

echo "== 1) HDFS 上的输出目录（part-r-00000 即倒排索引结果文件） =="
echo "\$ hdfs dfs -ls /user/lfr/lab2/output"
hdfs dfs -ls /user/lfr/lab2/output

echo
echo "== 2) 把索引结果下载到本地 results/ =="
echo "\$ hdfs dfs -get -f /user/lfr/lab2/output/part-r-00000 results/"
hdfs dfs -get -f /user/lfr/lab2/output/part-r-00000 results/part-r-00000

echo
echo "== 3) 索引规模 =="
echo "\$ wc -l results/part-r-00000"
wc -l results/part-r-00000

echo
echo "== 4) 倒排索引结果（前 12 行，行格式：单词 <文档,词频>;...;<total,总词频>.） =="
echo "\$ head -12 results/part-r-00000"
head -12 results/part-r-00000
