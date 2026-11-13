# -*- coding: utf-8 -*-
"""按《实验报告模板.docx》填充生成实验三报告（HBase 操作 + PageRank）。

直接打开模板，在表格各栏目单元中填入内容（不改动模板结构与格式），
输出 202400390057-李丰润-实验三.docx，再由 _docx2pdf.py 转 PDF。
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
OUT = os.path.join(BASE, '202400390057-李丰润-实验三.docx')

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
r = p.add_run('实验三  PageRank 算法实现（含 HBase 操作）')
style_run(r, size=BODY)

p = table.rows[1].cells[0].paragraphs[0]
r = p.add_run('2026.11.11')
style_run(r, size=BODY)

# ============ 实验目的 ============
cell = table.rows[3].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
for item in [
    '1. 理解 HBase 在 Hadoop 体系结构中的角色，熟练使用 HBase 操作常用的 Shell 命令；',
    '2. 熟悉 HBase 操作常用的 Java API，掌握把关系型数据库表转换为 HBase 存储的设计方法'
    '（行键、列族、列限定符），并编程实现建表、插入、浏览列、修改数据与删除行；',
    '3. 理解 PageRank 网页排名算法的原理，分别用 MapReduce 与 Spark 实现 PageRank 的'
    '迭代计算，在伪分布式环境下测试，并输出每个网页的 PR 值（保留 10 位小数）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 实验软件和硬件环境 ============
cell = table.rows[4].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
remove_hint_paragraphs(cell, '例如')
for item in [
    '硬件环境：x86_64 个人计算机；Oracle VM VirtualBox 7.1.8 虚拟机 lfr6（Ubuntu 64 位，'
    '内存 2.5 GB），实验全程以普通用户 lfr 在虚拟机图形界面的终端中完成。',
    '软件环境：Ubuntu 22.04 LTS（64 位）；OpenJDK 1.8.0_504；Apache Hadoop 3.3.6（伪分布式，'
    'HDFS + YARN）；Apache HBase 2.5.16（伪分布式，hbase.rootdir = hdfs://localhost:9000/hbase，'
    '自带 ZooKeeper）；Apache Spark 3.5.9（bin-hadoop3，local[2] 模式运行，同一份代码可由 --master yarn 提交到 YARN）；Python 3.10（PySpark）。',
    '实验代码与数据位于虚拟机目录 /home/lfr/bigdata-lab3，包含 code/（源代码）、data/（PageRank 图数据）、'
    'scripts/（实验脚本）与 results/（运行输出）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 实验原理和方法 ============
cell = table.rows[5].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)

cell_p(cell, '1. HBase 数据模型与表设计', bold=True, before=2)
cell_p(cell, 'HBase 是面向列的 NoSQL 数据库，数据模型由“表 → 行（行键 RowKey）→ 列族'
             '（ColumnFamily）→ 列限定符（Qualifier）→ 单元格（带时间戳版本）”构成。表中的行按行键'
             '字典序存储，列族在物理上独立存储，同一列族内的数据集中存放，因此非常适合海量、稀疏的'
             '数据。行键是 HBase 中唯一的主键，其设计直接决定查询效率与数据分布。', indent=2)
cell_p(cell, '关系型表到 HBase 的转换设计：Student 表行键为姓名，列族 info 下保存 S_No、S_Sex、'
             'S_Age；Course 表行键为课程名，列族 info 下保存 C_No、C_Credit；SC 表以学生姓名为行键，'
             '列族 Score 下的列限定符为课程名（Math、Computer Science、English），单元格值为成绩。'
             '题目数据中学号 2015003 重复出现（Mary 与 Lisi），若以学号作行键会互相覆盖，因此行键选用'
             '姓名，学号作为普通列保存。', indent=2)

cell_p(cell, '2. PageRank 算法原理', bold=True, before=2)
cell_p(cell, 'PageRank 把网页看作有向图 G=(V,E)，用随机游走模型衡量网页重要度：一个网页被越多'
             '重要网页链接，它的 PR 值越高；PR 值会被平均分摊给它的所有出链。考虑用户以概率 d 继续'
             '点击链接、以概率 1-d 随机跳转，迭代公式为：PR(A) = (1-d) + d·Σ(PR(Ti)/C(Ti))，其中 d=0.85'
             ' 为阻尼系数，Ti 为所有链接到 A 的网页，C(Ti) 为 Ti 的出链数。不断迭代直至收敛。本实验'
             '数据集无悬挂节点（每个网页至少有一条出链），因此所有网页 PR 之和恒等于网页数 N=15。', indent=2)

cell_p(cell, '3. MapReduce 实现思路与关键伪代码', bold=True, before=2)
cell_p(cell, '把图的“结构”和“PR 值”放在同一行中传递：每行保存 网页 \\t PR 值 \\t 出链集合。每轮迭代'
             '一个 MapReduce 作业：Mapper 把当前 PR 值按出链数平均分给每个邻居，并把图结构原样传递；'
             'Reducer 对每个网页累加收到的分量，代入阻尼公式得到新一轮 PR，再连同图结构写出。'
             '初始化作业把 PR 置为 1.0；循环 10 次后由一个格式化作业输出 (网页,PR值)。', indent=2)
cell_code(cell, '''Mapper(page, pr, links):
    emit(page, "G|" + links)                  // 图结构传递下去
    for nb in links:                          // 当前 PR 平均分给出链
        emit(nb, "P|" + pr / len(links))

Reducer(page, values):
    sum = Σ 所有 P| 分量
    newPr = 0.15 + 0.85 * sum                 // 阻尼公式，d = 0.85
    emit(page, newPr + "\\t" + links)          // 进入下一轮迭代
// 初始化：每行 page, 1.0, links；迭代 10 次后格式化输出 (page, "%.10f" % PR)''')

cell_p(cell, '4. Spark 实现思路与关键伪代码', bold=True, before=2)
cell_p(cell, 'Spark 用两个 RDD 迭代计算：links（网页 → 出链集合）与 ranks（网页 → PR 值）。每轮用'
             ' links.join(ranks) 把 PR 值带到出链上，flatMap 拆成（邻居, 分量）后 reduceByKey 汇总，'
             '没有入链的网页补 0，再套阻尼公式更新 ranks；循环结束后按网页名排序并格式化输出。'
             '中间结果常驻内存（cache），不需要每轮读写 HDFS。', indent=2)
cell_code(cell, '''links = sc.textFile(src).map(parse)          // 网页 -> [出链]
ranks = links.keys().map(lambda p: (p, 1.0)) // 初始 PR = 1.0
for i in range(10):
    contribs = links.join(ranks).flatMap(
        lambda kv: [(nb, kv[1][1] / len(kv[1][0])) for nb in kv[1][0]])
    sums = contribs.reduceByKey(add).union(zeros).reduceByKey(add)
    ranks = sums.mapValues(lambda s: 0.15 + 0.85 * s)
result = ranks.sortByKey().map(lambda kv: "(%s,%.10f)" % (kv[0], kv[1]))''')
cell_tail(cell)

# ============ 实验步骤 ============
cell = table.rows[6].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
cell_p(cell, '全部操作在虚拟机 lfr6 的图形界面终端中完成，实验目录为 ~/bigdata-lab3，各步骤整理为 '
             'scripts/ 目录下的脚本。HBase 与 YARN 分时使用（虚拟机内存 2.5 GB，二者同时运行会互相挤占'
             '内存），跑完 HBase 部分后停止 HBase、启动 YARN 运行 PageRank 作业。', indent=2)

cell_p(cell, '（1）安装并启动 HBase（伪分布式）', bold=True, before=2)
cell_p(cell, '从 Apache 镜像下载 hbase-2.5.16-bin.tar.gz 解压到 /usr/local/hbase，配置 '
             'hbase-site.xml（hbase.rootdir=hdfs://localhost:9000/hbase、'
             'hbase.cluster.distributed=true、由 HBase 自带 ZooKeeper）并限制各进程堆内存；用 '
             'start-hbase.sh 启动后，jps 可见 HMaster、HRegionServer、HQuorumPeer 三个进程：',
       indent=2, align=WD_ALIGN_PARAGRAPH.LEFT)
cell_image(cell, 'step1_hbase_start.png', '图 1  步骤 1：启动 HDFS 与 HBase，jps 显示 HMaster / HRegionServer / HQuorumPeer', IMG_W)

cell_p(cell, '（2）HBase Java API：建表、插入、浏览列、修改、删除', bold=True, before=2)
cell_p(cell, '编写 HBaseDemo.java，实现题目要求的 5 个方法：createTable（表存在则先删除再重建）、'
             'addRecord（支持 “列族:列限定符” 写法）、scanColumn（参数为列族时列出该族所有列，'
             '为具体列时逐行输出，缺失该列的行返回 null）、modifyData（修改单元格，返回修改前后的值）、'
             'deleteRow（删除整行）。程序依次创建 Student、Course、SC 三张表并写入题目数据：', indent=2)
cell_image(cell, 'step2_hbase_java1.png', '图 2  步骤 2：Java API 编译运行，创建 Student / Course / SC 三张表', IMG_W)
cell_image(cell, 'step2_hbase_java2.png', '图 3  步骤 2：Java API 浏览列（缺失列输出 null）、修改成绩、删除行', IMG_W)

cell_p(cell, '（3）HBase Shell 完成五项任务', bold=True, before=2)
cell_p(cell, '用 HBase Shell 完成同样的操作：list/describe 列出所有表及其列族信息、scan 显示'
             '指定表的全部记录、alter + put/delete 增删列族与列、truncate 清空指定表、count 统计行数：', indent=2)
cell_image(cell, 'step3_shell_tasks12.png', '图 4  步骤 3：Shell 任务 1~2——list/describe 列出表信息、scan 显示全部记录', IMG_W)
cell_image(cell, 'step3_shell_tasks3.png', '图 5  步骤 3：Shell 任务 3——添加/删除列族 extra、写入/删除列 extra:phone', IMG_W)
cell_image(cell, 'step3_shell_tasks345.png', '图 6  步骤 3：Shell 任务 4~5——truncate 清空 TempTable、count 统计行数', IMG_W)

cell_p(cell, '（4）PageRank 数据集', bold=True, before=2)
cell_p(cell, '自建 15 个网页的链接图（Hadoop 生态、流式计算、NoSQL 三类技术主题），每行格式为'
             '“网页 \\t 出链集合（逗号分隔）”，数据文件为 data/pagerank.txt，共 15 行、无悬挂节点：', indent=2)
cell_code(cell, '''Hadoop\\tHDFS,MapReduce,YARN,Spark
HDFS\\tHadoop,YARN
MapReduce\\tHadoop,Spark,YARN
...
MongoDB\\tCassandra,Redis
Redis\\tCassandra,MongoDB''')

cell_p(cell, '（5）PageRank 的 MapReduce 实现与运行', bold=True, before=2)
cell_p(cell, '程序 PageRankMR 由初始化作业 + 10 轮迭代作业 + 格式化作业组成，在 YARN 上运行，'
             '每轮输出“第 i 次迭代完成”，最后输出 (网页,PR值)（保留 10 位小数）：', indent=2)
cell_image(cell, 'step4_pagerank_mr.png', '图 7  步骤 5：MapReduce 版 PageRank 迭代 10 次并输出结果', IMG_W)

cell_p(cell, '（6）PageRank 的 Spark 实现与运行', bold=True, before=2)
cell_p(cell, '用 PySpark 实现同样的迭代（RDD 的 join / flatMap / reduceByKey，每轮用 count 强制物化），'
             'spark-submit 以 local[2] 模式提交（受虚拟机内存限制；同一份代码可由 --master yarn 提交到 '
             'YARN），输入输出仍为伪分布式 HDFS，输出格式与 MapReduce 版完全一致：', indent=2)
cell_image(cell, 'step5_pagerank_spark.png', '图 8  步骤 6：Spark 版 PageRank 迭代 10 次并输出结果', IMG_W)

cell_p(cell, '（7）两种实现的结果对比', bold=True, before=2)
cell_p(cell, '两种实现 15 个网页的 PR 值保留 10 位小数后逐位一致，且 PR 之和等于网页数 15：', indent=2)
cell_nested_table(cell, [
    ['网页', 'MapReduce 结果', 'Spark 结果'],
    ['Hadoop', '3.2444779138', '3.2444779138'],
    ['YARN', '2.1042202422', '2.1042202422'],
    ['HDFS', '2.1026975732', '2.1026975732'],
    ['Spark', '1.7588632674', '1.7588632674'],
    ['MapReduce', '1.3353648099', '1.3353648099'],
    ['其余 10 个网页', '0.1500000000 ~ 0.7337983902', '0.1500000000 ~ 0.7337983902'],
], widths=[3.6, 5.0, 5.0])
cell_tail(cell)

# ============ 结论分析与体会 ============
cell = table.rows[7].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
for item in [
    '1. HBase 部分：通过 Java API 与 Shell 两种方式完成建表、插入、浏览、增删列族/列、清空与统计'
    '行数，体会到 HBase 以行键为唯一索引、按列族存储的模型与关系型数据库的差异：HBase 不支持跨行'
    '事务与连接，查询只能走行键或全表扫描，因此行键设计（本实验用姓名而非重复的学号）直接决定数据'
    '是否会覆盖以及查询效率；列族数量应尽量少，同一列族的数据在物理上连续存放。',
    '2. PageRank 部分：从公式 PR(A) = (1-d) + d·Σ(PR(Ti)/C(Ti)) 出发，把“按出链分发 PR、按入链'
    '汇总 PR”映射为 Map/Reduce 两阶段，10 次迭代后结果收敛，Hadoop 以 3.2445 的 PR 值排名第一，'
    '符合它在数据集中被链接最多的实际；PR 之和等于网页数 15，验证了算法的正确性。',
    '3. 两种框架的对比：MapReduce 每轮迭代都要启动一个作业、中间结果落 HDFS，10 次迭代共 11 个'
    '作业，耗时较长；Spark 用 RDD 把图数据与 PR 值常驻内存，10 次迭代在一个应用内完成，代码也更'
    '简洁（join + flatMap + reduceByKey）。两者输出逐位一致，说明“同一算法的不同实现可以互相'
    '验证”。此外，在 2.5 GB 内存的虚拟机上 HBase 与 YARN 同时运行会因内存不足导致 RegionServer'
    '被杀，因此按“HBase 部分 / PageRank 部分”分时启停服务，这也是小内存伪分布式环境下的实用经验。',
    '4. 实验代码、数据与结果已整理至 GitHub 公开仓库：https://github.com/mhy668/bigData'
    '（实验三内容位于 bigdata-lab3/ 目录）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 问答题 ============
cell = table.rows[8].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
cell_p(cell, '问题 1：HBase 的行键该如何设计？本实验为什么用姓名而不是学号作行键？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：HBase 中行键是唯一索引，同一行键的写入会覆盖旧数据，且表按行键字典序切分成 Region '
             '分布存储，因此行键设计要保证唯一性、尽量短、并避免热点（如连续自增前缀会导致写热点）。'
             '题目数据中 Mary 与 Lisi 的学号都写成 2015003，若以学号作行键，后写入的记录会覆盖先写入'
             '的记录；改用姓名作行键后三行互不冲突，学号、性别、年龄作为 info 列族的列保存，既保留了'
             '全部数据，也符合“行用 S_Name 表示”的题目要求。', indent=2)
cell_p(cell, '问题 2：PageRank 公式中阻尼系数 d 的作用是什么？为什么迭代结果的 PR 值之和等于网页数？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：d（通常取 0.85）表示用户按链接继续浏览的概率，1-d=0.15 表示用户随机跳转到任意'
             '网页的概率。它的作用是保证随机游走的马尔可夫链不可约且非周期，避免出现“只在自己的'
             '闭环里传递 PR”或 PR 值不收敛的问题；d 越小，随机跳转越多，各网页 PR 越平均。'
             '本实验采用公式 PR = (1-d) + d·Σ(PR/C)，由于每个网页都有出链（无悬挂节点），每轮迭代'
             '中所有网页的 PR 总和保持不变：(1-d)·N + d·N = N，初始 PR 全为 1.0 时总和就是 N=15，'
             '所以迭代 10 次后 15 个网页的 PR 值之和仍为 15。', indent=2)
cell_p(cell, '问题 3：MapReduce 与 Spark 实现 PageRank 的主要差异是什么？各自的适用场景？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：MapReduce 实现把每轮迭代做成一个独立作业，图结构与 PR 值通过 HDFS 在作业之间'
             '传递，每轮都有作业启动、Shuffle 落盘的开销，10 次迭代需要 11 个作业，适合一次性、'
             '超大规模、对时延不敏感的数据处理；Spark 把数据缓存在内存 RDD 中，用 join、flatMap、'
             'reduceByKey 等算子在一个应用里循环 10 次，没有中间落盘，代码更短、迭代速度更快，'
             '适合需要反复迭代的算法（PageRank、K-Means、机器学习训练等）。本实验中两者输出完全'
             '一致，说明算法逻辑正确。', indent=2)

doc.save(OUT)
print('已生成报告（按模板填充）: ' + OUT)
