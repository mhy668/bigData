#!/bin/bash
# ==============================================================
# 实验三 步骤4：PageRank 的 MapReduce 实现（迭代 10 次）
# ==============================================================
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab3"
cd "$LAB"

echo "== 0) 停止 HBase 释放内存，启动 YARN（PageRank 作业运行在 YARN 上） =="
echo "\$ stop-hbase.sh   # HBase 未运行则跳过"
jps | grep -q HMaster && stop-hbase.sh >/dev/null 2>&1
echo "\$ start-yarn.sh   # YARN 未运行则启动"
jps | grep -q ResourceManager || start-yarn.sh 2>&1 | tail -1
sleep 3
echo "\$ jps"
jps | grep -E "ResourceManager|NodeManager|NameNode|DataNode"
echo

echo "== 1) 编译并打包 PageRankMR =="
echo "\$ javac -classpath \$(hadoop classpath) -d build/pagerank code/PageRankMR.java"
mkdir -p build/pagerank
javac -classpath "$(hadoop classpath)" -d build/pagerank code/PageRankMR.java
echo "\$ jar cf pagerankmr.jar -C build/pagerank ."
jar cf pagerankmr.jar -C build/pagerank .
echo "compiled & packaged OK"

echo
echo "== 2) 上传图数据到 HDFS =="
echo "\$ hdfs dfs -mkdir -p /user/lfr/lab3"
hdfs dfs -mkdir -p /user/lfr/lab3
echo "\$ hdfs dfs -put -f data/pagerank.txt /user/lfr/lab3/"
hdfs dfs -put -f data/pagerank.txt /user/lfr/lab3/
echo "\$ hdfs dfs -cat /user/lfr/lab3/pagerank.txt"
hdfs dfs -cat /user/lfr/lab3/pagerank.txt

echo
echo "== 3) 提交 PageRank MapReduce 作业（10 次迭代） =="
echo "\$ hadoop jar pagerankmr.jar PageRankMR /user/lfr/lab3/pagerank.txt /user/lfr/lab3/pagerank_out 10"
hadoop jar pagerankmr.jar PageRankMR \
    /user/lfr/lab3/pagerank.txt /user/lfr/lab3/pagerank_out 10 2>&1 | grep -E "^>>>|completed successfully|Job job_"

echo
echo "== 4) MapReduce 迭代 10 次后的 PageRank 结果 =="
echo "\$ hdfs dfs -cat /user/lfr/lab3/pagerank_out/part-*"
hdfs dfs -cat /user/lfr/lab3/pagerank_out/part-*
