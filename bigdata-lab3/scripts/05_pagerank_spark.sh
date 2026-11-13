#!/bin/bash
# ==============================================================
# 实验三 步骤5：PageRank 的 Spark 实现（迭代 10 次）
# 说明：虚拟机内存有限，Spark 以 local[2] 本地模式运行（同一份代码
#       也可用 --master yarn 提交到 YARN，仅提交参数不同），
#       输入/输出仍使用伪分布式 HDFS。
# ==============================================================
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab3"
cd "$LAB"

echo "== 0) 清理上一次的输出目录 =="
hdfs dfs -rm -r -f /user/lfr/lab3/spark_out >/dev/null 2>&1

echo "== 1) 提交 PageRank Spark 作业（local[2] 模式，10 次迭代，输入输出为 HDFS） =="
echo "\$ spark-submit --master local[2] --driver-memory 768m \\"
echo "      code/pagerank.py hdfs://localhost:9000/user/lfr/lab3/pagerank.txt \\"
echo "      hdfs://localhost:9000/user/lfr/lab3/spark_out 10"
spark-submit --master "local[2]" --driver-memory 768m \
    code/pagerank.py hdfs://localhost:9000/user/lfr/lab3/pagerank.txt \
    hdfs://localhost:9000/user/lfr/lab3/spark_out 10 2>&1 \
    | grep -E "^>>>|^====|^\(|PR 值总和|Exception|ERROR"

echo
echo "== 2) 从 HDFS 读取 Spark 输出结果 =="
echo "\$ hdfs dfs -cat /user/lfr/lab3/spark_out/part-*"
hdfs dfs -cat /user/lfr/lab3/spark_out/part-*
