# -*- coding: utf-8 -*-
"""按《实验报告模板.docx》填充生成实验四报告（并行化 K-Means 聚类）。

直接打开模板，在表格各栏目单元中填入内容（不改动模板结构与格式），
输出 202400390057-李丰润-实验四.docx，再由 _docx2pdf.py 转 PDF。
"""
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, 'images')
TEMPLATE = os.path.join(BASE, '模板.docx')
OUT = os.path.join(BASE, '202400390057-李丰润-实验四.docx')

SONG = '宋体'
BODY = 12          # 小四
IMG_W = float(os.environ.get('IMG_W', '9.8'))

doc = Document(TEMPLATE)
table = doc.tables[0]

for row in table.rows:
    trPr = row._tr.trPr
    if trPr is not None:
        for cs in trPr.findall(qn('w:cantSplit')):
            trPr.remove(cs)


def style_run(run, size=BODY, bold=False, font=SONG, ascii_font=None):
    run.font.size = Pt(size)
    run.bold = bold
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.insert(0, rf)
    west = ascii_font or font
    rf.set(qn('w:ascii'), west)
    rf.set(qn('w:hAnsi'), west)
    rf.set(qn('w:eastAsia'), font)


def cell_p(cell, text, indent=0.0, size=BODY, bold=False, spacing=1.25,
           align=None, font=SONG, ascii_font=None, before=0, after=0):
    p = cell.add_paragraph()
    run = p.add_run(text)
    style_run(run, size=size, bold=bold, font=font, ascii_font=ascii_font)
    pf = p.paragraph_format
    pf.line_spacing = spacing
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if indent:
        pf.first_line_indent = Pt(size * indent)
    if align is not None:
        p.alignment = align
    return p


def shade_paragraph(p, fill='F5F5F5'):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), fill)
    pPr.append(shd)


def cell_code(cell, code, size=8.5):
    for line in code.split('\n'):
        p = cell.add_paragraph()
        run = p.add_run(line if line else ' ')
        style_run(run, size=size, font='Consolas', ascii_font='Consolas')
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.left_indent = Pt(6)
        shade_paragraph(p)
    p = cell.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(0)


def cell_image(cell, fname, caption, width_cm):
    p = cell.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(os.path.join(IMG, fname), width=Cm(width_cm))
    cell_p(cell, caption, size=9, align=WD_ALIGN_PARAGRAPH.CENTER,
           spacing=1.0, after=3)


def cell_nested_table(cell, rows, widths, size=9):
    t = cell.add_table(rows=len(rows), cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + edge)
        e.set(qn('w:val'), 'single')
        e.set(qn('w:sz'), '4')
        e.set(qn('w:space'), '0')
        e.set(qn('w:color'), 'auto')
        borders.append(e)
    t._tbl.tblPr.append(borders)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ''
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(val))
            style_run(run, size=size, bold=(i == 0))
    for j, w in enumerate(widths):
        for i in range(len(rows)):
            t.cell(i, j).width = Cm(w)
    tail = cell.add_paragraph()
    tail.paragraph_format.line_spacing = 1.0
    tail.paragraph_format.space_after = Pt(4)
    return t


def clear_empty_paragraphs(cell, keep_tail=1):
    ps = cell.paragraphs
    empties = [p for p in ps[1:] if not p.text.strip()]
    for p in empties[:-keep_tail] if keep_tail else empties:
        p._element.getparent().remove(p._element)


def remove_hint_paragraphs(cell, hint='例如'):
    for p in cell.paragraphs[1:]:
        if hint in p.text:
            p._element.getparent().remove(p._element)


def cell_tail(cell):
    p = cell.add_paragraph()
    run = p.add_run('')
    style_run(run, size=6)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(0)
    return p


# ============ 表头字段 ============
p = table.rows[0].cells[0].paragraphs[0]
r = p.add_run('实验四  并行化数据挖掘算法设计（K-Means 聚类）')
style_run(r, size=BODY)

p = table.rows[1].cells[0].paragraphs[0]
r = p.add_run('2026.11.18')
style_run(r, size=BODY)

# ============ 实验目的 ============
cell = table.rows[3].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
for item in [
    '1. 理解数据挖掘算法并行化的必要性：数据规模不断扩大时，单机串行算法难以在可接受的时间内'
    '完成计算，需要利用分布式框架把计算拆分到多台机器/多个任务上并行执行；',
    '2. 掌握 K-Means 聚类算法的原理与实现，能够自行准备数据集，编写非并行化（单机）版本；',
    '3. 掌握用 MapReduce 实现迭代型数据挖掘算法的设计方法，并通过整数化计算等手段保证并行实现'
    '与串行实现的数据挖掘结果完全一致。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 实验软件和硬件环境 ============
cell = table.rows[4].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
remove_hint_paragraphs(cell, '例如')
for item in [
    '硬件环境：x86_64 个人计算机；Oracle VM VirtualBox 7.1.8 虚拟机 lfr6（Ubuntu 64 位，'
    '内存 2.5 GB，2 vCPU），实验全程以普通用户 lfr 在虚拟机图形界面的终端中完成。',
    '软件环境：Ubuntu 22.04 LTS（64 位）；OpenJDK 1.8.0_504；Apache Hadoop 3.3.6（伪分布式，'
    'HDFS + YARN，并行实现以 MapReduce 作业提交到 YARN，uber 模式运行）；Python 3.10（串行实现，单机运行）。',
    '实验代码与数据位于虚拟机目录 /home/lfr/bigdata-lab4，包含 code/（源代码）、data/（数据集与生成脚本）、'
    'scripts/（实验脚本）与 results/（两种实现的运行结果）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 实验原理和方法 ============
cell = table.rows[5].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)

cell_p(cell, '1. K-Means 聚类算法原理', bold=True, before=2)
cell_p(cell, 'K-Means 把 n 个数据点划分为 k 个簇，使簇内点尽量紧凑。算法迭代执行两步：'
             '（1）分配：计算每个点到各质心的欧氏距离平方，把它归入距离最近的簇（距离相同时取簇编号'
             '较小者）；（2）更新：把每个簇的质心更新为该簇所有点的坐标均值。重复直到分配不再变化或'
             '达到迭代次数，其目标函数为簇内平方误差 SSE = Σ Σ ||x − c_i||²。本实验取 k=5、'
             '固定迭代 10 次，数据为 20000 个二维整数点（由 5 个高斯簇生成）。', indent=2)

cell_p(cell, '2. 并行化设计：每轮迭代一个 MapReduce 作业', bold=True, before=2)
cell_p(cell, 'K-Means 每轮的两步计算都适合并行：分配阶段各点相互独立，可以拆给多个 Map 任务；'
             '更新阶段是"按簇求和"，正好由 Reduce 按簇编号聚合完成。因此把每轮迭代实现为一个'
             'MapReduce 作业：Mapper 读取质心文件（只有 5 行），为每个点求出最近簇，输出 '
             '<簇编号, “x,y”>；Reducer 对每个簇累加坐标和与点数，输出新的质心（sumX, sumY, count）；'
             'Driver 循环提交 10 轮迭代作业，最后再运行两个作业输出"每个点的簇编号"和"各簇内平方误差"。'
             '质心文件在 HDFS 上随每轮作业的输出更新，是各轮之间的状态。', indent=2)
cell_p(cell, '这一"每轮一个作业"的模式是 MapReduce 实现迭代型算法的典型做法：作业之间的中间结果'
             '落在 HDFS 上，由框架保证容错；Mapper 端只做本地计算，Shuffle 的数据量很小（每个点一条'
             '“簇编号→坐标”记录，可用 Combiner 进一步压缩）。', indent=2)

cell_p(cell, '3. 并行与串行结果一致性的保证', bold=True, before=2)
cell_p(cell, '并行与串行的浮点求和顺序不同（Map 输出顺序、Shuffle 顺序），直接累加浮点数容易在末位'
             '产生差异。本实验从三方面保证两种实现逐位一致：（1）数据为整数坐标，各簇坐标和用长整数'
             '累加——整数加法满足结合律，与求和顺序无关；（2）两种实现使用完全相同的初始质心、同样的'
             '距离比较（整数平方距离，平局取小编号）和同样的质心公式（sum/count），空簇沿用原质心；'
             '（3）簇内平方误差用整数化公式 Σ[(x·n − Sx)² + (y·n − Sy)²] 计算（等价于 SSE × n²），'
             '避免浮点求和。这样两种实现的质心、簇规模、SSE 和每个点的簇编号都应逐字节相同。', indent=2)

cell_p(cell, '4. 并行实现的关键伪代码', bold=True, before=2)
cell_code(cell, '''// 质心文件格式：C<idx>\\t<sumX>\\t<sumY>\\t<count>
// 初始质心：C0(0,0)  C1(1000,0)  C2(0,1000)  C3(1000,1000)  C4(500,500)
Mapper(setup):  读取质心文件 -> cents[K]；每个簇发一条哨兵记录
Mapper(map):    解析点 (x, y)
                k <- argmin_k  (x - cents[k].x)^2 + (y - cents[k].y)^2   // 平局取小编号
                emit(k, "x,y")
Reducer(key=k): sx <- Σx; sy <- Σy; n <- 点数    // 整数累加，与顺序无关
                if n = 0: 沿用原来的 (sx, sy, n)                     // 空簇
                emit("C<k>", sx + "\\t" + sy + "\\t" + n)
Driver:         写初始质心；循环 10 次提交迭代作业；再运行"输出簇编号"与"计算整数化 SSE"作业''')
cell_tail(cell)

# ============ 实验步骤 ============
cell = table.rows[6].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
cell_p(cell, '全部操作在虚拟机 lfr6 的图形界面终端中完成，实验目录为 ~/bigdata-lab4，各步骤整理为 '
             'scripts/ 目录下的脚本。串行实现用 Python 在单机运行；并行实现编译成 jar 后以 MapReduce '
             '作业提交到 YARN（Hadoop 伪分布式）。', indent=2)

cell_p(cell, '（1）生成数据集', bold=True, before=2)
cell_p(cell, '用固定随机种子 42 生成 20000 个二维整数点：5 个高斯簇（中心 (150,150)、(850,150)、'
             '(150,850)、(850,850)、(500,500)，标准差 80），坐标裁剪到 [0,1000]，每行格式为 '
             '“点编号,x,y”：', indent=2)
cell_image(cell, 'step1_gen_data.png', '图 1  步骤 1：生成 20000 个点的数据集并查看规模', IMG_W)

cell_p(cell, '（2）非并行化实现（单机 Python）', bold=True, before=2)
cell_p(cell, 'kmeans_serial.py 按上述原理逐点分配、按簇求和更新质心，迭代 10 次，输出质心、'
             '簇规模、整数化 SSE 和每个点的簇编号到 results/serial_*.txt：', indent=2)
cell_image(cell, 'step2_serial.png', '图 2  步骤 2：串行 K-Means 运行（10 次迭代后收敛）与结果', IMG_W)

cell_p(cell, '（3）并行化实现（Hadoop MapReduce）', bold=True, before=2)
cell_p(cell, 'KMeansMR.java 把每轮迭代实现为一个 MapReduce 作业（Mapper 分配、Reducer 按簇求和），'
             'Driver 依次提交 10 轮迭代作业和 2 个结果作业；质心文件在 HDFS 上随迭代更新：', indent=2)
cell_image(cell, 'step3_parallel.png', '图 3  步骤 3：并行 K-Means 的 MapReduce 作业运行与结果', IMG_W)

cell_p(cell, '（4）结果对比', bold=True, before=2)
cell_p(cell, '用 diff 与 md5sum 比较两种实现的四个结果文件（质心、簇规模、SSE、每个点的簇编号）：', indent=2)
cell_image(cell, 'step4_compare.png', '图 4  步骤 4：串行与并行结果对比（diff 为空、md5 成对相同）', IMG_W)
cell_p(cell, '两种实现的四个结果文件全部逐字节一致。最终 5 个簇的质心与规模如下（迭代 10 次，'
             '实际在第 4 次后已收敛）：', indent=2)
cell_nested_table(cell, [
    ['簇', '质心（x, y）', '点数'],
    ['C0', '(149.0907500000, 150.7695000000)', '4000'],
    ['C1', '(849.9639819910, 151.1103051526)', '3998'],
    ['C2', '(152.2805395953, 850.6899825131)', '4003'],
    ['C3', '(847.6689172293, 848.8857214304)', '3999'],
    ['C4', '(500.0882500000, 498.5320000000)', '4000'],
], widths=[1.6, 9.0, 2.6])
cell_p(cell, '整数化簇内平方误差：3930246940406784（两种实现相同）。从质心位置和簇规模可以看出，'
             '聚类结果与数据生成时的 5 个高斯簇一致，说明算法正确提取了数据中的簇结构。', indent=2)
cell_tail(cell)

# ============ 结论分析与体会 ============
cell = table.rows[7].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
for item in [
    '1. 算法与并行化设计的契合点：K-Means 的"分配"各点独立，"更新"是按簇求和，正好对应 MapReduce '
    '的 Map 与 Reduce 两个阶段；每轮迭代一个作业、质心文件作为轮间状态，是迭代型算法在 MapReduce '
    '上的通用实现模式。由于数据量小（20000 个点、约 12 个 MapReduce 作业），作业的启动与调度开销'
    '远大于实际计算：串行 Python 约 1 秒完成，并行版约 5 分钟——这说明 MapReduce 的优势在于'
    '数据量大、计算密集的场景，小数据上用分布式框架并不划算，选择技术栈要结合数据规模。',
    '2. 结果一致性的实现：并行与串行在浮点求和顺序上天然不同，本实验通过"整数坐标 + 整数求和 + '
    '相同的初始质心/距离/平局规则 + 整数化 SSE"消除了非确定性来源，最终四个结果文件 diff 为空、'
    'md5 成对相同，严格证明了并行化没有改变算法语义。这也提示我们：在分布式环境下，要重视中间'
    '结果的确定性与可验证性，尽量把聚合运算设计成与顺序无关的形式。',
    '3. 总体体会：本次实验走通了"数据准备 → 算法设计 → 串行实现 → 并行实现 → 结果对比"的完整'
    '流程，加深了对并行化算法分析方法（识别独立计算、设计聚合方式、控制轮间状态、处理边界情况'
    '如空簇）的理解，也巩固了 MapReduce 的编译打包、作业提交与运行日志分析能力。',
    '4. 实验代码、数据与结果已整理至 GitHub 公开仓库：https://github.com/mhy668/bigData'
    '（实验四内容位于 bigdata-lab4/ 目录）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 问答题 ============
cell = table.rows[8].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
cell_p(cell, '问题 1：为什么并行实现与串行实现的结果能够完全一致？如果改用浮点坐标或浮点求和会出现什么问题？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：本实验的坐标是整数，各簇的坐标和用长整数累加——整数加法满足结合律，与 Map 输出、'
             'Shuffle 的求和顺序无关；质心 = 整数和 / 点数，两种实现执行同样的除法；距离比较用整数'
             '平方距离，簇内误差也用整数化公式计算，因此并行与串行得到完全相同的结果。若改用浮点'
             '坐标与浮点求和，并行和串行的累加顺序不同，浮点加法不满足结合律，和的末位可能出现差异；'
             '质心末位不同又会改变边界点的归属，进而"放大"成不同的聚类结果（迭代过程会把微小差异'
             '逐步放大）。因此对结果一致性要求高的场景，应尽量把求和整数化，或固定归约顺序、使用'
             '更高精度/可补偿求和的算法。', indent=2)
cell_p(cell, '问题 2：MapReduce 实现 K-Means“每轮一个作业”有什么优缺点？可以怎样优化？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：优点是思路简单、与算法的迭代结构一一对应，作业间的中间结果由 HDFS 持久化，容错与'
             '调度由框架保证，适合"数据大、迭代次数不多"的场景；缺点是每一轮都要启动新的作业'
             '（ApplicationMaster 与容器启动、任务调度、输出落盘），迭代次数一多，固定开销就很可观'
             '——本实验数据只有 20000 个点，10 轮迭代共 12 个作业，作业开销占主导（约 5 分钟），而'
             '串行只需约 1 秒。优化方向：使用 Spark 等内存计算框架把点数据与质心缓存在内存中反复'
             '迭代；在 Map 端加 Combiner 预聚合各簇的局部和，减少 Shuffle 数据量；把质心通过'
             'DistributedCache/广播变量分发；数据量大时增加切分数量以提高并行度。', indent=2)
cell_p(cell, '问题 3：k 值与初始质心如何选择？它们对聚类结果有什么影响？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：k 值一般根据业务先验或"肘部法"（SSE 随 k 增大的下降曲线出现拐点处）、轮廓系数等'
             '指标确定；本实验数据集由 5 个高斯簇生成，取 k=5 与数据生成过程一致，聚类结果也验证了'
             '这一点。K-Means 对初始质心敏感，不同的初始质心可能收敛到不同的局部最优，常用'
             'k-means++（按距离平方的概率选初始质心）或多次随机初始化取 SSE 最小的方案；本实验为了'
             '保证并行与串行结果可复现，固定了 5 个初始质心（4 个角点 + 中心点），两种实现从同一起点'
             '出发、使用相同的规则，最终收敛到同一组质心。', indent=2)

doc.save(OUT)
print('已生成报告（按模板填充）: ' + OUT)
