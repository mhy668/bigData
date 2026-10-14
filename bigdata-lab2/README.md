# 实验二　文档倒排索引算法实现

《大数据管理与分析》课程实验二的代码与报告：从公开网页下载 12 篇英文文档，建立停词表，
用 MapReduce（Hadoop 3.3.6，伪分布式）构建文档倒排索引，并演示按单词检索。

## 一、实验环境

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 LTS（VirtualBox 虚拟机 lfr6，2 GB 内存） |
| Java | OpenJDK 1.8.0_504 |
| Hadoop | Apache Hadoop 3.3.6（伪分布式，HDFS + YARN） |

## 二、目录结构

```
bigdata-lab2/
├── code/
│   └── InvertedIndex.java        # 倒排索引 MapReduce 程序（Mapper/Combiner/Reducer）
├── data/
│   ├── documents/                # 12 篇英文文档 document01.txt ~ document12.txt
│   └── stopwords.txt             # 停词表（179 个英文停用词）
├── scripts/
│   ├── env.sh                    # Hadoop 环境变量（脚本自包含，不依赖 .bashrc）
│   ├── prepare_text.py           # 网页 HTML -> 纯文本转换
│   ├── 01_download_documents.sh  # 下载文档并转换
│   ├── 02_show_stopwords.sh      # 查看停词表
│   ├── 03_compile.sh             # 编译并打包 jar
│   ├── 04_start_hadoop.sh        # 启动 HDFS 与 YARN
│   ├── 05_build_index.sh         # 上传数据并提交 MapReduce 作业
│   ├── 06_query_index.sh         # 查看索引结果
│   └── 07_query_words.sh         # 单词检索示例
├── results/
│   ├── part-r-00000              # 倒排索引完整输出（5869 条词项记录）
│   ├── queries.txt               # 检索示例输出（data/hadoop/mapreduce/search/index）
│   └── document_stats.txt        # 12 篇文档词数统计
└── report/                       # 实验报告（PDF / Word，按课程模板填写）
```

## 三、程序流程

1. **Mapper**：按输入分片取得文档名；把行内容统一小写，用非字母数字字符切分；
   过滤单字符、以数字开头的片段与停词表中的词；输出 `<单词, "文档名:1">`。
2. **Combiner**：把同一文档内同一单词的计数先合并（`document01.txt:91`），
   减少 Shuffle 阶段的网络传输量（本实验 73623 条 Map 输出聚合为 12384 条）。
3. **Reducer**：把同一单词在各文档中的词频按文档名升序汇总到 TreeMap，
   求和得到 `total`，输出 `word <document01.txt,6>;<document02.txt,3>;<total,11>.`。

## 四、运行方法

```bash
bash scripts/04_start_hadoop.sh       # 启动 Hadoop（若未启动）
bash scripts/03_compile.sh            # 编译打包
bash scripts/05_build_index.sh        # 上传数据并运行作业
bash scripts/06_query_index.sh        # 查看结果（结果保存到 results/）
bash scripts/07_query_words.sh        # 单词检索示例
```

## 五、结果示例

```
data      <document01.txt,16>;<document02.txt,75>;<document03.txt,2>;...;<document12.txt,53>;<total,376>.
hadoop    <document01.txt,91>;<document02.txt,36>;<document03.txt,16>;<document04.txt,5>;<total,148>.
mapreduce <document01.txt,115>;<document02.txt,3>;<document03.txt,4>;<document04.txt,4>;<total,126>.
search    <document01.txt,2>;<document02.txt,1>;<document06.txt,42>;...;<total,56>.
```

查询某个单词在哪些文档中出现、各出现多少次，只需在 `part-r-00000` 中查找该单词对应的行
（`grep '^hadoop[[:space:]]' results/part-r-00000`）。
