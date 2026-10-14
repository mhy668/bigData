#!/bin/bash
# ==============================================================
# 实验二 步骤4：上传数据到 HDFS 并运行倒排索引作业
# ==============================================================
# 加载 Hadoop 环境变量
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab2"
cd "$LAB"

echo "== 1) 建立 HDFS 工作目录 =="
echo "\$ hdfs dfs -mkdir -p /user/lfr/lab2/input"
hdfs dfs -mkdir -p /user/lfr/lab2/input

echo
echo "== 2) 上传 12 篇文档与停词表到 HDFS =="
echo "\$ hdfs dfs -put -f data/documents/*.txt /user/lfr/lab2/input/"
hdfs dfs -put -f data/documents/*.txt /user/lfr/lab2/input/
echo "\$ hdfs dfs -put -f data/stopwords.txt /user/lfr/lab2/stopwords.txt"
hdfs dfs -put -f data/stopwords.txt /user/lfr/lab2/stopwords.txt

echo
echo "== 3) 查看 HDFS 上的输入文件 =="
echo "\$ hdfs dfs -ls /user/lfr/lab2/input"
hdfs dfs -ls /user/lfr/lab2/input

echo
echo "== 4) 删除旧的输出目录（若存在） =="
echo "\$ hdfs dfs -rm -r -f /user/lfr/lab2/output"
hdfs dfs -rm -r -f /user/lfr/lab2/output

echo
echo "== 5) 提交 MapReduce 作业 =="
echo "\$ hadoop jar invertedindex.jar InvertedIndex /user/lfr/lab2/input /user/lfr/lab2/output /user/lfr/lab2/stopwords.txt"
hadoop jar invertedindex.jar InvertedIndex \
    /user/lfr/lab2/input /user/lfr/lab2/output /user/lfr/lab2/stopwords.txt
