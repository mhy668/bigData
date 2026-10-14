#!/bin/bash
# ==============================================================
# 实验二 步骤3：编译倒排索引 MapReduce 程序并打包成 jar
# ==============================================================
# 加载 Hadoop 环境变量
source "$(dirname "$0")/env.sh"

LAB="$HOME/bigdata-lab2"
cd "$LAB"
mkdir -p build

echo "== 1) 编译（把 Hadoop 依赖加入 classpath） =="
echo "\$ javac -encoding UTF-8 -classpath \$(hadoop classpath) -d build code/InvertedIndex.java"
javac -encoding UTF-8 -classpath "$(hadoop classpath)" -d build code/InvertedIndex.java
echo "compiled OK"

echo
echo "== 2) 打包成 jar =="
echo "\$ jar cf invertedindex.jar -C build ."
jar cf invertedindex.jar -C build .
ls -lh invertedindex.jar
echo
echo "== 3) 查看 jar 中的类文件 =="
jar tf invertedindex.jar | grep class
