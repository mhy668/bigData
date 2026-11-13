# 实验三　HBase 操作与 PageRank 算法实现

《大数据管理与分析》课程实验三，包含两部分：

1. **HBase 操作**：HBase Shell 常用命令（列出表、显示记录、增删列族/列、清空表、统计行数），
   以及 Java API 编程（建表、插入、浏览列、修改、删除），并把关系型数据库中的
   Student / Course / SC 三张表转换为 HBase 存储。
2. **PageRank 算法**：分别用 **MapReduce** 和 **Spark** 实现 PageRank，迭代 10 次，
   输出每个网页的 PR 值（保留 10 位小数）。

## 一、实验环境

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 LTS（VirtualBox 虚拟机 lfr6，2.5 GB 内存，2 vCPU） |
| Java | OpenJDK 1.8.0_504 |
| Hadoop | Apache Hadoop 3.3.6（伪分布式，HDFS + YARN） |
| HBase | Apache HBase 2.5.16（伪分布式，rootdir = hdfs://localhost:9000/hbase，自带 ZooKeeper，WAL provider = filesystem） |
| Spark | Apache Spark 3.5.9（bin-hadoop3，local[2] 模式运行；同一份代码可由 --master yarn 提交到 YARN） |

## 二、目录结构

```
bigdata-lab3/
├── code/
│   ├── HBaseDemo.java        # HBase Java API：5 个方法 + 关系表转 HBase 的演示
│   ├── PageRankMR.java       # PageRank 的 MapReduce 实现（10 次迭代，uber 模式）
│   └── pagerank.py           # PageRank 的 Spark（PySpark）实现（10 次迭代）
├── data/
│   └── pagerank.txt          # 网页链接图（每行：网页 \t 出链集合，逗号分隔，共 15 个网页）
├── scripts/
│   ├── env.sh                # Hadoop/HBase/Spark 环境变量
│   ├── 00_show_status.sh     # 查看 Hadoop 与 HBase 运行状态
│   ├── 01_start_hbase.sh     # 启动 HDFS 与 HBase（含 HBase 就绪等待）
│   ├── 02_hbase_java.sh      # 编译并运行 HBaseDemo
│   ├── 03a_hbase_shell_1.sh  # HBase Shell 任务 1~2（list/describe/scan）
│   ├── 03b_hbase_shell_2.sh  # HBase Shell 任务 3~5（增删列族列/truncate/count）
│   ├── 04_pagerank_mr.sh     # 启动 YARN + 运行 PageRank MapReduce 作业
│   └── 05_pagerank_spark.sh  # 运行 PageRank Spark 作业（local[2]，输入输出为 HDFS）
├── results/
│   ├── hbase_java_output.txt      # HBaseDemo 运行输出
│   ├── hbase_shell_tasks12.txt    # Shell 任务 1~2 输出
│   ├── hbase_shell_tasks345.txt   # Shell 任务 3~5 输出
│   ├── pagerank_mr.txt            # MapReduce 结果（part-m-00000）
│   └── pagerank_spark.txt         # Spark 结果（part-*）
└── report/                   # 实验报告（PDF / Word，按课程模板填写）
```

## 三、HBase 表设计

| 表 | 行键 | 列族 | 列限定符 | 说明 |
| --- | --- | --- | --- | --- |
| Student | 姓名（S_Name） | info | S_No / S_Sex / S_Age | 题目数据中学号 2015003 重复，故用姓名作行键 |
| Course | 课程名（C_Name） | info | C_No / C_Credit | |
| SC | 学生姓名（S_Name） | Score | Math / Computer Science / English | 单元格值为成绩 |

## 四、PageRank 数据集

`data/pagerank.txt` 共 15 个网页（Hadoop 生态、流式计算与 NoSQL 共三类），每行格式：

```
网页<TAB>该网页链接到的网页1,网页2,...
```

例如：`Hadoop<TAB>HDFS,MapReduce,YARN,Spark`。图中每个网页至少有一条出链（无悬挂节点）。

## 五、运行方法

```bash
bash scripts/01_start_hbase.sh       # 启动 HDFS + HBase
bash scripts/00_show_status.sh       # 查看进程与 HBase 集群状态
bash scripts/02_hbase_java.sh        # HBase Java API 演示（建表/插入/浏览/修改/删除）
bash scripts/03a_hbase_shell_1.sh    # HBase Shell 任务 1~2
bash scripts/03b_hbase_shell_2.sh    # HBase Shell 任务 3~5
bash scripts/04_pagerank_mr.sh       # 停止 HBase、启动 YARN，运行 MapReduce 版 PageRank
bash scripts/05_pagerank_spark.sh    # 运行 Spark 版 PageRank（local[2]）
```

## 六、结果示例

PageRank 迭代 10 次后（PR 之和 = 网页数 15，两种实现逐位一致）：

```
(Cassandra,0.3720233411)
(Flink,0.3052467873)
(HBase,0.6057137137)
(HDFS,2.1026975732)
(Hadoop,3.2444779138)
(Hive,0.7119299061)
(Kafka,0.7337983902)
(MapReduce,1.3353648099)
(MongoDB,0.2610116706)
(Pig,0.1500000000)
(Redis,0.2610116706)
(Spark,1.7588632674)
(Storm,0.3609856273)
(YARN,2.1042202422)
(ZooKeeper,0.6926550869)
```
