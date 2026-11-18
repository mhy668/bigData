# -*- coding: utf-8 -*-
"""生成 K-Means 实验数据集（固定随机种子，可重复生成）。

数据为 20000 个二维整数点，分布在 5 个高斯簇附近（中心 ± 噪声），
坐标裁剪到 [0, 1000]，输出 data/points.csv，格式：P00001,x,y
"""
import csv
import os
import random

N = 20000                      # 点数（每簇 4000）
SEED = 42
CENTERS = [(150, 150), (850, 150), (150, 850), (850, 850), (500, 500)]
SIGMA = 80                     # 噪声标准差

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'data', 'points.csv')


def main():
    random.seed(SEED)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        idx = 0
        for cx, cy in CENTERS:
            for _ in range(N // len(CENTERS)):
                idx += 1
                x = min(1000, max(0, round(random.gauss(cx, SIGMA))))
                y = min(1000, max(0, round(random.gauss(cy, SIGMA))))
                w.writerow(['P%05d' % idx, x, y])
    print('已生成 %d 个点 -> %s' % (idx, OUT))


if __name__ == '__main__':
    main()
