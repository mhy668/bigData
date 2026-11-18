# 实验四　并行化数据挖掘算法设计（K-Means 聚类）

《大数据管理与分析》课程实验四：自行准备数据集，设计一种数据挖掘算法，并分别用
**非并行化（单机 Python）** 和 **并行化（Hadoop MapReduce）** 两种方式实现，要求两种实现
的数据挖掘结果**完全一致**。

本实验选择 **K-Means 聚类**：

- 数据集：20000 个二维整数点（5 个高斯簇，固定随机种子 42 生成）；
- 算法参数：k = 5，初始质心固定为 5 个角点/中心点，固定迭代 10 次；
- 计算语义：距离用整数坐标的欧氏距离平方比较（平局取簇编号小者），质心 = 各簇坐标和 / 点数，
  簇内平方误差用整数化公式 Σ (x·n − Sx)² + (y·n − Sy)² 计算；
- 两种实现使用完全相同的初始质心、距离、更新与迭代规则，因此结果逐字节一致。

## 一、实验环境

| 项目 | 配置 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 LTS（VirtualBox 虚拟机 lfr6，2.5 GB 内存，2 vCPU） |
| Java | OpenJDK 1.8.0_504 |
| Hadoop | Apache Hadoop 3.3.6（伪分布式，HDFS + YARN） |
| 串行实现 | Python 3.10（单机运行） |
| 并行实现 | Java + Hadoop MapReduce（YARN，uber 模式） |

## 二、目录结构

```
bigdata-lab4/
├── code/
│   ├── kmeans_serial.py      # K-Means 的非并行化（单机 Python）实现
│   └── KMeansMR.java         # K-Means 的并行化（MapReduce）实现
├── data/
│   ├── gen_dataset.py        # 数据集生成脚本（固定随机种子）
│   └── points.csv            # 20000 个点：P00001,x,y
├── scripts/
│   ├── env.sh                # Hadoop 环境变量
│   ├── 01_gen_data.sh        # 生成数据集
│   ├── 02_serial.sh          # 运行串行实现
│   ├── 03_parallel.sh        # 编译、打包并运行 MapReduce 并行实现
│   └── 04_compare.sh         # 对比两种实现的输出（diff + md5）
└── results/
    ├── serial_*.txt          # 串行结果：centroids / sizes / sse / assignments
    ├── parallel_*.txt        # 并行结果：同上
    └── compare.txt           # 对比输出（完全一致）
```

## 三、MapReduce 并行化设计

K-Means 每轮迭代的“分配 + 求各簇坐标和”天然可并行，每轮用一个 MapReduce 作业实现：

- **Mapper**：读取当前质心（从 HDFS 质心文件加载），把每个点分配到最近的簇，输出
  `<簇编号, "x,y">`；同时为每个簇发送一条哨兵记录，保证空簇也能进入 Reduce（质心保持不变）。
- **Reducer**：对每个簇累加坐标和与点数，输出新的质心（sumX, sumY, count）。
- **Driver**：写入初始质心，循环提交 10 轮迭代作业，最后再运行“输出各点簇编号”的作业和
  “计算整数化簇内平方误差”的作业，并把格式化结果写到本地 results/ 目录。
- 局部性优化：单轮中每个 Map 任务只需要质心文件（几个字节），切分后的点数据在本地处理，
  Shuffle 只传输“簇编号 → 坐标”的小记录。

## 四、运行方法

```bash
bash scripts/01_gen_data.sh      # 生成 data/points.csv
bash scripts/02_serial.sh        # 串行实现（单机 Python）
# 启动 Hadoop：start-dfs.sh && start-yarn.sh
bash scripts/03_parallel.sh      # 并行实现（MapReduce）
bash scripts/04_compare.sh       # 对比两种实现的结果
```

## 五、结果

两种实现的 `centroids / sizes / sse / assignments` 四个结果文件 **diff 为空、md5 成对相同**，
即逐字节完全一致。最终 5 个簇（迭代 10 次后收敛）：

| 簇 | 质心（x, y） | 点数 |
| --- | --- | --- |
| C0 | (149.0907500000, 150.7695000000) | 4000 |
| C1 | (849.9639819910, 151.1103051526) | 3998 |
| C2 | (152.2805395953, 850.6899825131) | 4003 |
| C3 | (847.6689172293, 848.8857214304) | 3999 |
| C4 | (500.0882500000, 498.5320000000) | 4000 |

整数化簇内平方误差：3930246940406784。
