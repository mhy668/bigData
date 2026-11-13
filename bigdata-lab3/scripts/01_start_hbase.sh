#!/bin/bash
# ==============================================================
# 实验三 步骤1：启动 Hadoop 与 HBase（伪分布式）
# ==============================================================
source "$(dirname "$0")/env.sh"

echo "== 0) 停止 YARN（虚拟机内存 2 GB，HBase 与 YARN 分时使用） =="
echo "\$ stop-yarn.sh"
stop-yarn.sh >/dev/null 2>&1 || true
sleep 2

echo
echo "== 1) 先停止旧进程，保证干净启动 =="
echo "\$ stop-hbase.sh; stop-dfs.sh"
stop-hbase.sh >/dev/null 2>&1 || true
stop-dfs.sh 2>&1 | tail -1
sleep 3

echo
echo "== 2) 启动 HDFS =="
echo "\$ start-dfs.sh"
start-dfs.sh

echo
echo "== 3) 启动 HBase（自带 ZooKeeper，hbase.rootdir 指向 HDFS） =="
echo "\$ start-hbase.sh"
start-hbase.sh

echo
sleep 8
echo "== 4) 等待 HBase 就绪（最多 60 秒），检查 Java 进程 =="
for i in $(seq 1 30); do
    printf 'status
exit
' | hbase shell 2>/dev/null | grep -q "active master" && break
    sleep 2
done
echo "\$ jps"
jps

echo
echo "== 5) HBase 集群状态 =="
printf 'status\nexit\n' | hbase shell 2>/dev/null | sed -n '/active master/,$p' | head -2
