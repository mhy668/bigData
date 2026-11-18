#!/bin/bash
# ==============================================================
# 实验四 步骤3：K-Means 的并行化（Hadoop MapReduce）实现
# ==============================================================
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab4"
cd "$LAB"

echo "== 0) 检查 Hadoop 运行状态 =="
echo "\$ jps | grep -E \"NameNode|ResourceManager\""
jps | grep -E "NameNode|ResourceManager" || { echo "Hadoop 未启动，请先执行 start-dfs.sh && start-yarn.sh"; exit 1; }

echo
echo "== 1) 上传数据集到 HDFS =="
echo "\$ hdfs dfs -mkdir -p /user/lfr/lab4"
hdfs dfs -mkdir -p /user/lfr/lab4
echo "\$ hdfs dfs -put -f data/points.csv /user/lfr/lab4/"
hdfs dfs -put -f data/points.csv /user/lfr/lab4/

echo
echo "== 2) 编译并打包 MapReduce 程序 =="
mkdir -p build/kmeans
echo "\$ javac -classpath \$(hadoop classpath) -d build/kmeans code/KMeansMR.java"
javac -classpath "$(hadoop classpath)" -d build/kmeans code/KMeansMR.java
echo "\$ jar cf kmeansmr.jar -C build/kmeans ."
jar cf kmeansmr.jar -C build/kmeans .
echo "compiled & packaged OK"

echo
echo "== 3) 提交 K-Means 作业（10 次迭代，每次迭代一个 MapReduce 作业） =="
echo "\$ hadoop jar kmeansmr.jar KMeansMR /user/lfr/lab4/points.csv /user/lfr/lab4/kmeans_out 10 results"
hadoop jar kmeansmr.jar KMeansMR \
    /user/lfr/lab4/points.csv /user/lfr/lab4/kmeans_out 10 results \
    2>&1 | grep -E "^>>>|^点数输入|^并行结果|completed successfully" | tail -16

echo
echo "== 4) 从 HDFS 取回每个点的聚类结果 =="
echo "\$ hdfs dfs -get -f /user/lfr/lab4/kmeans_out_assignments/part-m-00000 results/parallel_assignments.txt"
hdfs dfs -get -f /user/lfr/lab4/kmeans_out_assignments/part-m-00000 results/parallel_assignments.txt

echo
echo "== 并行结果 =="
echo "\$ cat results/parallel_centroids.txt"
cat results/parallel_centroids.txt
echo "\$ cat results/parallel_sizes.txt"
cat results/parallel_sizes.txt
echo "\$ cat results/parallel_sse.txt"
cat results/parallel_sse.txt
echo "\$ head -3 results/parallel_assignments.txt（共 $(wc -l < results/parallel_assignments.txt) 行）"
head -3 results/parallel_assignments.txt
