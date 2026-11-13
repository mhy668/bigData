#!/bin/bash
# ==============================================================
# 实验三 步骤1：查看 Hadoop 与 HBase 运行状态
# ==============================================================
source "$(dirname "$0")/env.sh"

echo "== 1) Hadoop 与 HBase 进程 =="
echo "\$ jps"
jps

echo
echo "== 2) HBase 集群状态与表列表 =="
echo "\$ echo \"status; list\" | hbase shell"
printf 'status\nlist\nexit\n' | hbase shell 2>/dev/null \
  | grep -vE "^(Took|SLF4J)" \
  | grep -vE "^(HBase Shell|Use \"help\"|For Reference|Version [0-9])"
