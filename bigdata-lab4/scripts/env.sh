#!/bin/bash
# Hadoop / HBase / Spark 环境变量（脚本自包含，不依赖 .bashrc）
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export HBASE_HOME=/usr/local/hbase
export PATH=$PATH:$HBASE_HOME/bin
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
