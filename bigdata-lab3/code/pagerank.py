# -*- coding: utf-8 -*-
"""实验三（第二部分）：PageRank 的 Spark 实现（PySpark）。

输入文件每行：网页 \t 该网页链接到的网页集合（英文逗号分隔）
迭代 10 次，输出 (网页,PR值)，PR 值保留 10 位小数。

用法: spark-submit pagerank.py <input> <output> [iterations]
"""
import sys

from pyspark import SparkConf, SparkContext

DAMPING = 0.85


def parse_line(line):
    """把一行 'page \\t a,b,c' 解析为 (page, [a, b, c])。"""
    parts = line.strip().split('\t')
    page = parts[0].strip()
    links = []
    if len(parts) > 1 and parts[1].strip():
        links = [x.strip() for x in parts[1].split(',') if x.strip()]
    return page, links


def main():
    if len(sys.argv) < 3:
        print("Usage: pagerank.py <input> <output> [iterations]")
        sys.exit(2)
    src, dst = sys.argv[1], sys.argv[2]
    iterations = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    sc = SparkContext(conf=SparkConf().setAppName("PageRank-Spark"))
    sc.setLogLevel("WARN")

    links = sc.textFile(src).map(parse_line).cache()
    pages = links.keys().cache()

    # 每个网页初始 PR = 1.0
    ranks = pages.map(lambda p: (p, 1.0))

    for i in range(1, iterations + 1):
        # 每个网页把 PR 平均分给出链
        contribs = links.join(ranks).flatMap(
            lambda kv: [(nb, kv[1][1] / len(kv[1][0])) for nb in kv[1][0]])
        # 汇总各网页分到的 PR；没有入链的网页补 0，保证每轮所有网页都在
        sums = contribs.reduceByKey(lambda a, b: a + b)
        zeros = pages.map(lambda p: (p, 0.0))
        sums = sums.union(zeros).reduceByKey(lambda a, b: a + b)
        # 阻尼公式：PR = (1-d) + d * Σ
        ranks = sums.mapValues(lambda s: (1 - DAMPING) + DAMPING * s).cache()
        ranks.count()   # 触发本轮计算（RDD 惰性求值），使每轮结果物化到内存
        print(">>> 第 %d 次迭代完成" % i)

    result = ranks.sortByKey().map(
        lambda kv: "(%s,%.10f)" % (kv[0], kv[1])).cache()

    lines = result.collect()
    print("========== 迭代 %d 次后的 PageRank 结果 ==========" % iterations)
    for line in lines:
        print(line)
    print("PR 值总和 = %.10f" % sum(float(x.split(',')[1].rstrip(')')) for x in lines))

    result.saveAsTextFile(dst)
    sc.stop()


if __name__ == "__main__":
    main()
