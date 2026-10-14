# 大数据管理与分析　课程实验仓库

《大数据管理与分析》课程实验代码与报告仓库（山东大学，李丰润 / 学号 202400390057 / 2班）。

## 仓库结构

```
.
├── bigdata-lab1/                 # 实验一：大数据系统基本实验
│   ├── HDFSApp.java              # HDFS 十项操作的 Java API 实现
│   ├── MergeDedup.java           # MapReduce 任务1：文件合并与去重
│   ├── Sort.java                 # MapReduce 任务2：输入文件排序（带位次）
│   ├── STJoin.java               # MapReduce 任务3：挖掘祖孙辈关系（自连接）
│   ├── A.txt / B.txt             # 任务1输入数据
│   ├── file1.txt ~ file3.txt     # 任务2输入数据
│   ├── child-parent.txt          # 任务3输入数据
│   ├── report/                   # 实验一报告（PDF / Word）
│   └── README.md                 # 实验一说明
│
├── bigdata-lab2/                 # 实验二：文档倒排索引算法实现
│   ├── code/InvertedIndex.java   # 倒排索引 MapReduce 程序（Mapper/Combiner/Reducer）
│   ├── data/                     # 12 篇英文文档 + 停词表（179 词）
│   ├── scripts/                  # 下载文档、编译、启动 Hadoop、构建索引、查询等脚本
│   ├── results/                  # 倒排索引结果 part-r-00000、检索示例、文档统计
│   ├── report/                   # 实验二报告（PDF / Word）
│   └── README.md                 # 实验二说明
│
└── README.md                     # 本文件：两次实验的索引
```

## 实验环境（两次实验共用）

| 项目 | 配置 |
| --- | --- |
| 虚拟机 | Oracle VM VirtualBox 7.1.8（Ubuntu 22.04 LTS 64 位，用户 lfr） |
| Java | OpenJDK 1.8 |
| Hadoop | Apache Hadoop 3.3.6（伪分布式，HDFS + YARN） |

## 各实验内容速览

- **实验一（bigdata-lab1/）**：Linux/Hadoop 基本操作、HDFS 操作（Shell 命令 + Java API 十项任务）、
  MapReduce 初级编程（合并去重、排序、祖孙关系挖掘）。
- **实验二（bigdata-lab2/）**：从公开网页下载 12 篇英文文档并建立停词表，用 MapReduce 构建文档
  倒排索引，输出形如 `word <document01.txt,6>;<document02.txt,3>;<total,11>.`，并演示按单词检索。

各实验的详细说明、运行方法见对应目录下的 README.md。
