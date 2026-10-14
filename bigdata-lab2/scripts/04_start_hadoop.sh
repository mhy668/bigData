#!/bin/bash
# ==============================================================
# 实验二 步骤4：启动 Hadoop 伪分布式环境（HDFS + YARN）
# ==============================================================
source "$(dirname "$0")/env.sh"

echo "== 1) 为保证干净启动，先停止可能残留的进程 =="
echo "\$ stop-dfs.sh; stop-yarn.sh"
stop-dfs.sh 2>&1 | tail -2
stop-yarn.sh 2>&1 | tail -2
sleep 3

echo
echo "== 2) 启动 HDFS =="
echo "\$ start-dfs.sh"
start-dfs.sh

echo
echo "== 3) 启动 YARN =="
echo "\$ start-yarn.sh"
start-yarn.sh

echo
sleep 5
echo "== 4) 检查 Java 进程 =="
echo "\$ jps"
jps
