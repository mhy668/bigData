#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""K-Means 聚类的串行（单机）实现。

与并行版（MapReduce 实现 KMeansMR.java）使用完全相同的：
  - 初始质心（5 个固定点）
  - 距离计算（整数坐标的欧氏距离平方，平局取簇编号小者）
  - 质心更新（各簇坐标和 / 点数）
  - 迭代次数（固定 10 次）
因此两者的聚类结果逐位一致。

输出（results/ 目录）：
  serial_centroids.txt    每个簇的质心（保留 10 位小数）
  serial_sizes.txt        每个簇的点数
  serial_sse.txt          簇内平方误差（整数化：Σ (x·n - Sx)² + (y·n - Sy)²）
  serial_assignments.txt  每个点所属的簇
"""
import os
import sys

K = 5
ITER = 10
# 初始质心（5 个子区域的角点，与并行版一致）
INIT = [(0, 0, 1), (1000, 0, 1), (0, 1000, 1), (1000, 1000, 1), (500, 500, 1)]

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data', 'points.csv')
OUTDIR = os.path.join(BASE, 'results')


def load_points(path):
    pts = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            pid, x, y = line.split(',')
            pts.append((pid, int(x), int(y)))
    return pts


def centroid(c):
    """(sumX, sumY, count) -> (cx, cy)；空簇沿用原质心。"""
    sx, sy, n = c
    if n == 0:
        return 0.0, 0.0
    return sx / float(n), sy / float(n)


def main():
    if not os.path.exists(DATA):
        print('数据文件不存在，请先运行 scripts/01_gen_data.sh')
        sys.exit(1)
    pts = load_points(DATA)
    print('点数: %d，簇数: %d，迭代次数: %d' % (len(pts), K, ITER))

    cents = [(float(x), float(y), 1) for (x, y, _) in INIT]  # 初始质心（sum, count 形式）
    sums = [[float(c[0]), float(c[1]), float(c[2])] for c in cents]

    assign = [0] * len(pts)
    for it in range(1, ITER + 1):
        # 1) 分配：每个点归入距离最近的簇（平方距离整数比较，平局取小编号）
        cx = []
        cy = []
        for sx, sy, n in sums:
            if n == 0:
                cx.append(0.0)
                cy.append(0.0)
            else:
                cx.append(sx / n)
                cy.append(sy / n)
        new_sums = [[0.0, 0.0, 0.0] for _ in range(K)]
        for i, (pid, x, y) in enumerate(pts):
            best = 0
            best_d = None
            for k in range(K):
                dx = x - cx[k]
                dy = y - cy[k]
                d = dx * dx + dy * dy
                if best_d is None or d < best_d:
                    best_d = d
                    best = k
            assign[i] = best
            new_sums[best][0] += x
            new_sums[best][1] += y
            new_sums[best][2] += 1
        # 2) 更新：空簇沿用原来的和与计数（保持质心不变）
        for k in range(K):
            if new_sums[k][2] == 0:
                new_sums[k] = sums[k]
        sums = new_sums
        line = '第 %2d 次迭代: ' % it + '  '.join(
            'C%d=(%.4f,%.4f)[%d]' % (k, sums[k][0] / sums[k][2], sums[k][1] / sums[k][2], int(sums[k][2]))
            for k in range(K))
        print(line)

    # 3) 输出结果
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, 'serial_centroids.txt'), 'w', encoding='utf-8') as f:
        for k in range(K):
            f.write('C%d\t%.10f\t%.10f\n' % (k, sums[k][0] / sums[k][2], sums[k][1] / sums[k][2]))
    with open(os.path.join(OUTDIR, 'serial_sizes.txt'), 'w', encoding='utf-8') as f:
        for k in range(K):
            f.write('C%d\t%d\n' % (k, int(sums[k][2])))
    sse = 0
    for k in range(K):
        sx, sy, n = sums[k]
        for i, (pid, x, y) in enumerate(pts):
            if assign[i] == k:
                dx = x * n - sx
                dy = y * n - sy
                sse += int(dx * dx + dy * dy)
    with open(os.path.join(OUTDIR, 'serial_sse.txt'), 'w', encoding='utf-8') as f:
        f.write('%d\n' % sse)
    with open(os.path.join(OUTDIR, 'serial_assignments.txt'), 'w', encoding='utf-8') as f:
        for i, (pid, x, y) in enumerate(pts):
            f.write('%s\t%d\n' % (pid, assign[i]))
    print('结果已写入 %s' % OUTDIR)


if __name__ == '__main__':
    main()
