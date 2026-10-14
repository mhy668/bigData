# 实验一　大数据系统基本实验

本目录为《大数据管理与分析》课程实验一的代码与报告，包含 Linux/Hadoop 基本操作、HDFS 操作
（Shell 命令 + Java API 十项任务）和 MapReduce 初级编程三部分。

## 一、实验环境

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 LTS |
| Java | OpenJDK 1.8 |
| Hadoop | Apache Hadoop 3.3.6（伪分布式，HDFS + YARN） |

## 二、目录结构

```
bigdata-lab1/
├── HDFSApp.java                # 菜单式 Java 程序，实现 10 个 HDFS 功能（Shell + Java API 对照）
├── MergeDedup.java             # MapReduce 任务1：文件合并与去重
├── Sort.java                   # MapReduce 任务2：对输入文件排序（带位次）
├── STJoin.java                 # MapReduce 任务3：挖掘祖孙辈关系（单表自连接）
├── A.txt  B.txt                # 任务1输入
├── file1.txt file2.txt file3.txt   # 任务2输入
├── child-parent.txt            # 任务3输入
└── report/                     # 实验报告（PDF / Word）
```

## 三、实验内容

### 第一部分　Linux 与 Hadoop 基本操作
常用 Linux 命令（cd、ls、mkdir、rmdir、cp、mv、rm、cat、tac、more、head、tail、touch、chown、
find、tar、grep 等）练习，以及启动 Hadoop、在 HDFS 中创建用户目录并上传/下载文件。命令清单见实验报告。

### 第二部分　HDFS 操作（Shell + Java API）
用 Shell 命令和 Java API 两种方式实现以下 10 个功能：

1. 上传文件（已存在时由用户选择追加或覆盖）
2. 下载文件（本地同名时自动重命名）
3. 输出文件内容到终端
4. 显示文件的读写权限、大小、时间、路径
5. 递归显示目录下所有文件信息
6. 创建/删除文件（目录不存在则自动创建）
7. 创建/删除目录（仅空目录可删除）
8. 向文件开头或结尾追加内容
9. 删除指定文件
10. 移动文件（源路径 → 目的路径）

### 第三部分　MapReduce 初级编程
1. **文件的合并与去重**：以整行为 key，利用 shuffle 的排序与去重特性完成。
2. **对输入文件排序**：以整数为 key，设置单个 Reducer 保证全局有序，用计数器生成位次。
3. **祖孙辈关系挖掘**：单表自连接，对每条记录按 child、parent 分别输出带标记的数据，在 reduce 中做笛卡尔积。

## 四、编译与运行

> 运行前请先启动 Hadoop：`start-dfs.sh && start-yarn.sh`

### 第二部分：HDFS 程序

```bash
javac -classpath "$(hadoop classpath)" HDFSApp.java
java  -classpath ".:$(hadoop classpath)" HDFSApp
```

### 第三部分：MapReduce 程序

```bash
# 编译
javac -classpath "$(hadoop classpath)" -d . MergeDedup.java Sort.java STJoin.java

# 打包
jar cf MergeDedup.jar MergeDedup*.class
jar cf Sort.jar Sort*.class
jar cf STJoin.jar STJoin*.class

# 任务1：合并去重
hdfs dfs -mkdir -p /input/merge
hdfs dfs -put A.txt B.txt /input/merge/
hadoop jar MergeDedup.jar MergeDedup /input/merge /output/merge
hdfs dfs -cat /output/merge/*

# 任务2：排序
hdfs dfs -mkdir -p /input/sort
hdfs dfs -put file1.txt file2.txt file3.txt /input/sort/
hadoop jar Sort.jar Sort /input/sort /output/sort
hdfs dfs -cat /output/sort/*

# 任务3：祖孙关系挖掘
hdfs dfs -mkdir -p /input/join
hdfs dfs -put child-parent.txt /input/join/
hadoop jar STJoin.jar STJoin /input/join /output/join
hdfs dfs -cat /output/join/*
```

> 注意：MapReduce 要求输出目录事先不存在，重跑前先 `hdfs dfs -rm -r -f /output/<名字>`。

## 五、实验报告

见 `report/202400390057-李丰润-实验一.pdf`（`report/` 目录下同时提供 Word 源文件）。

## 作者

- 学号：202400390057
- 姓名：李丰润
- 班级：2班
