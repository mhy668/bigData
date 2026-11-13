#!/bin/bash
# ==============================================================
# 实验三 步骤2：HBase Java API 程序（建表/插入/浏览/修改/删除）
# ==============================================================
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab3"
cd "$LAB"
mkdir -p build/hbase

echo "== 1) 编译 HBaseDemo.java =="
echo "\$ javac -classpath \$(hbase classpath) -d build/hbase code/HBaseDemo.java"
javac -classpath "$(hbase classpath)" -d build/hbase code/HBaseDemo.java
echo "compiled OK"

echo
echo "== 2) 运行：创建 Student / Course / SC 表并插入题目数据 =="
echo "\$ java -classpath \".:build/hbase:\$(hbase classpath)\" HBaseDemo"
java -classpath ".:build/hbase:$(hbase classpath)" HBaseDemo 2>/dev/null
