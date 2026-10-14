# -*- coding: utf-8 -*-
"""按《实验报告模板.docx》填充生成实验二报告。

直接打开模板，在表格各栏目单元中填入内容（不改动模板结构与格式），
输出 202400390057-李丰润-实验二.docx，再由 _docx2pdf.py 转 PDF。
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
TEMPLATE = r'E:\大数据管理与分析\实验报告模板.docx'
OUT = os.path.join(BASE, '202400390057-李丰润-实验二.docx')

SONG = '宋体'
BODY = 12          # 小四
IMG_W = float(os.environ.get('IMG_W', '9.4'))

doc = Document(TEMPLATE)
table = doc.tables[0]

# 页边距略收紧（模板默认上下 2.54cm），保证正文不超 8 页
sec = doc.sections[0]
sec.top_margin = Cm(2.15)
sec.bottom_margin = Cm(2.15)

# 表格单元内容可跨页断行（防止出现整行被推到下一页）
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
    """在单元格末尾追加一个段落。indent 为字符数（按 size 折算）。"""
    p = cell_tail(cell)
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
    """命令/伪代码块：浅灰底 + 等宽字体，每个逻辑行一段。"""
    for line in code.split('\n'):
        p = cell_tail(cell)
        run = p.add_run(line if line else ' ')
        style_run(run, size=size, font='Consolas', ascii_font='Consolas')
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.left_indent = Pt(6)
        shade_paragraph(p)
    # 末尾补一个无底纹空段，避免灰底紧贴下一段
    p = cell_tail(cell)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(0)


def cell_image(cell, fname, caption, width_cm):
    p = cell_tail(cell)
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
    # 手动加全框线（模板中没有 Table Grid 样式）
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
    tail = cell_tail(cell)
    tail.paragraph_format.line_spacing = 1.0
    tail.paragraph_format.space_after = Pt(4)
    return t


def clear_empty_paragraphs(cell, keep_tail=1):
    """删除模板中留空的内容段落，仅保留末尾 keep_tail 个空段。"""
    ps = cell.paragraphs
    empties = [p for p in ps[1:] if not p.text.strip()]
    for p in empties[:-keep_tail] if keep_tail else empties:
        p._element.getparent().remove(p._element)


def remove_hint_paragraphs(cell, hint='例如'):
    """删除模板中的示例提示段落（如“例如：”）。"""
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


# ============ 表头字段：实验题目 / 日期 ============
p = table.rows[0].cells[0].paragraphs[0]
r = p.add_run('实验二  文档倒排索引算法实现')
style_run(r, size=BODY)

p = table.rows[1].cells[0].paragraphs[0]
r = p.add_run('2026.10.14')
style_run(r, size=BODY)

# ============ 实验目的 ============
cell = table.rows[3].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
for item in [
    '1. 理解倒排索引（Inverted Index）的概念与结构：以“单词（词项）→ 出现该单词的文档列表'
    '（含词频）”为核心映射，掌握词项词典与倒排记录表两部分及其按文档编号有序存储的意义；',
    '2. 掌握用 MapReduce 构建倒排索引的方法：Map 阶段分词、去停词并输出“单词-文档”对，'
    'Combine 阶段在 Map 端局部聚合，Reduce 阶段按单词汇总各文档词频，体会“分而治之 + '
    '按 key 聚合”的编程思想；',
    '3. 熟练掌握 MapReduce 程序在 Hadoop 集群（伪分布式）上的完整流程：编写、编译、打包、'
    '上传数据到 HDFS、提交作业、查看运行统计（Counters）与结果；',
    '4. 学会从公开网页采集英文文档语料、构建并分发停词表，并对倒排索引结果进行单词检索验证。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 实验软件和硬件环境 ============
cell = table.rows[4].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
remove_hint_paragraphs(cell, '例如')
for item in [
    '硬件环境：x86_64 个人计算机；Oracle VM VirtualBox 7.1.8 虚拟机 lfr6（Ubuntu 64 位，'
    '内存 2 GB），实验全程以普通用户 lfr 在虚拟机图形界面的终端中完成。',
    '软件环境：Ubuntu 22.04 LTS（64 位）；OpenJDK 1.8.0_504；Apache Hadoop 3.3.6（伪分布式，'
    'HDFS + YARN，NameNode 与 ResourceManager 运行于本机）；辅助工具 wget（下载文档）、'
    'Python 3.10（网页 HTML 转纯文本）。',
    '实验代码与数据位于虚拟机目录 /home/lfr/bigdata-lab2，包含 code/（MapReduce 源码）、'
    'data/（12 篇文档与停词表）、scripts/（实验脚本）与 results/（结果与查询输出）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 实验原理和方法 ============
cell = table.rows[5].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)

cell_p(cell, '1. 倒排索引的原理', bold=True, spacing=1.25, before=2)
cell_p(cell, '正排索引以文档为主键，记录“一篇文档包含哪些词”；而全文检索需要的是反向映射：'
             '给定一个查询词，快速找到包含它的全部文档。倒排索引正是为此设计的索引结构：以词项'
             '（term）为主键，为每个词项维护一张“倒排记录表”（posting list），记录该词出现过的'
             '文档及词频，通常按文档编号升序存储，便于压缩和后续多词项归并。本实验要求输出的'
             '格式为：data <document01.txt,6>;<document02.txt,3>;<document05.txt,2>;'
             '<total,11>.，查询某个单词时只需在结果文件中定位该词对应的一行，即可得到它出现'
             '在哪些文档、各出现多少次。', indent=2)

cell_p(cell, '2. 基于 MapReduce 的构建方法', bold=True, spacing=1.25, before=2)
cell_p(cell, '大规模语料的倒排索引构建本质上是“按词项分组求和”的聚合问题，天然适合 '
             'MapReduce 模型，程序由 Mapper、Combiner、Reducer 三部分组成。', indent=2)
for item in [
    '（1）Mapper（分词与过滤）：以“行号—行内容”为输入，通过 FileSplit 取到当前分片的文件名'
    '（即文档名）；行内容统一小写，非字母数字字符替换为空格后分词；过滤长度小于 2、以数字'
    '开头、位于停词表中的词；对保留的每个词项输出 <单词, “文档名:1”>，即一条“该词在该'
    '文档出现 1 次”的部分倒排记录。',
    '（2）Combiner（Map 端局部聚合）：在 Map 端先把同一文档内同一单词的计数合并为'
    '“文档名:次数”，例如 (hadoop, document01.txt:1) 出现多次合并为 (hadoop, '
    'document01.txt:91)。Combiner 本质是“局部的 Reduce”，可把 Shuffle 传输量压缩数倍'
    '（本实验 73623 条 Map 输出记录聚合为 12384 条）。',
    '（3）Reducer（全局汇总）：框架按单词分组后，Reducer 把该单词的全部“文档名:次数”对累加'
    '到 TreeMap（按文档名自动升序）中并累计总词频 total，拼接成 word <文档1,次数>;...;'
    '<total,总数>. 的格式输出。停词表（179 个 a、an、the、and、is 等高频词）上传到 HDFS，'
    '由 Mapper 在 setup() 阶段读入内存（每个 Map 任务只读一次），分词时逐词过滤。',
]:
    cell_p(cell, item, indent=2)

cell_p(cell, '3. 关键伪代码', bold=True, spacing=1.25, before=2)
cell_code(cell, '''Mapper(行号 key, 行内容 value):
    docName <- 当前输入分片的文件名        // FileSplit.getPath().getName()
    tokens  <- 分词(小写化(value), 非字母数字字符 -> 空格)
    for token in tokens:
        if token 是停词 or 长度 < 2 or 首字符是数字: continue
        emit(token, docName + ":1")       // 部分倒排记录：该词在该文档出现 1 次

Combiner(word, ["doc:1", "doc:1", ...]):  // 局部的、可结合的聚合，压缩 Shuffle 数据量
    按文档名累加计数
    emit(word, "doc:cnt")                 // 例："document01.txt:91"

Reducer(word, ["doc1:16", "doc2:75", ...]):
    perDoc <- TreeMap<文档名, 词频>        // 红黑树，自动按文档名升序排列
    total  <- 0
    for "doc:cnt" in values:              // 累加各文档词频
        perDoc[doc] += cnt; total += cnt
    emit(word, "<doc1,c1>;<doc2,c2>;...;<total,total>.")''')
cell_tail(cell)

# ============ 实验步骤 ============
cell = table.rows[6].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
cell_p(cell, '全部操作在虚拟机 lfr6（Ubuntu 22.04）的图形界面终端中完成，实验目录为 '
             '~/bigdata-lab2，各步骤整理为 scripts/ 目录下的脚本，下列截图为实际运行画面。', indent=2)

cell_p(cell, '（1）下载英文文档（12 篇）', bold=True, before=2)
cell_p(cell, '用 wget 从公开网页下载 12 篇英文文档（Apache Hadoop/Spark 技术文档、Python '
             'HOWTO、Git 电子书、MDN 文档、GNU 手册与 RFC 791/1035/2616 标准文本），HTML '
             '网页去标签后保存为 document01.txt ~ document12.txt，文档描述如下表：', indent=2)
cell_nested_table(cell, [
    ['编号', '文件名', '来源（公开网页）', '词数'],
    ['1', 'document01.txt', 'Apache Hadoop - MapReduce Tutorial', '8239'],
    ['2', 'document02.txt', 'Apache Hadoop - HDFS Architecture', '4711'],
    ['3', 'document03.txt', 'Apache Hadoop - YARN', '848'],
    ['4', 'document04.txt', 'Apache Spark - Quick Start', '2313'],
    ['5', 'document05.txt', 'Python - Sorting HOWTO', '2127'],
    ['6', 'document06.txt', 'Python - Regular Expression HOWTO', '8607'],
    ['7', 'document07.txt', 'Git - About Version Control', '1322'],
    ['8', 'document08.txt', 'MDN - What is JavaScript', '5022'],
    ['9', 'document09.txt', 'GNU Coreutils - Introduction', '311'],
    ['10', 'document10.txt', 'RFC 791 Internet Protocol', '11192'],
    ['11', 'document11.txt', 'RFC 1035 Domain Names', '15901'],
    ['12', 'document12.txt', 'RFC 2616 HTTP/1.1', '57897'],
    ['合计', '12 篇', '——', '118490'],
], widths=[1.3, 3.1, 7.6, 1.7])
cell_image(cell, 'step1.png', '图 1  步骤 1：下载 12 篇英文文档、转换为纯文本并统计词数', IMG_W)

cell_p(cell, '（2）建立停词表', bold=True, before=2)
cell_p(cell, '停词表 data/stopwords.txt 共 179 个英文停用词，一行一词（# 开头为注释），'
             '覆盖冠词、介词、代词、常见助动词及缩写形式（the、and、of、is、don’t 等），'
             '运行时上传到 HDFS 供所有 Map 任务共享读取。', indent=2)
cell_image(cell, 'step2.png', '图 2  步骤 2：停词表内容（节选）与词数统计', IMG_W)

cell_p(cell, '（3）编译与打包 MapReduce 程序', bold=True, before=2)
cell_p(cell, '源码 code/InvertedIndex.java（Mapper/Combiner/Reducer 与 Job 装配），用 Hadoop '
             '的 classpath 编译后打包成 jar：', indent=2)
cell_code(cell, '''$ javac -encoding UTF-8 -classpath $(hadoop classpath) \\
        -d build code/InvertedIndex.java
$ jar cf invertedindex.jar -C build .''')
cell_image(cell, 'step3.png', '图 3  步骤 3：程序编译成功并打包成 invertedindex.jar', IMG_W)

cell_p(cell, '（4）启动 Hadoop 伪分布式环境', bold=True, before=2)
cell_p(cell, '启动 HDFS（NameNode、DataNode、SecondaryNameNode）与 YARN（ResourceManager、'
             'NodeManager），用 jps 检查进程：', indent=2)
cell_code(cell, '$ start-dfs.sh          $ start-yarn.sh          $ jps')
cell_image(cell, 'step4.png', '图 4  步骤 4：HDFS 与 YARN 启动成功（jps 显示 5 个守护进程）', IMG_W)

cell_p(cell, '（5）上传数据并运行倒排索引作业', bold=True, before=2)
cell_p(cell, '把 12 篇文档与停词表上传到 HDFS，然后提交 MapReduce 作业（第 3 个参数为 HDFS '
             '上的停词表路径）：', indent=2)
cell_code(cell, '''$ hdfs dfs -mkdir -p /user/lfr/lab2/input
$ hdfs dfs -put -f data/documents/*.txt /user/lfr/lab2/input/
$ hdfs dfs -put -f data/stopwords.txt   /user/lfr/lab2/stopwords.txt
$ hadoop jar invertedindex.jar InvertedIndex \\
      /user/lfr/lab2/input /user/lfr/lab2/output /user/lfr/lab2/stopwords.txt''')
cell_image(cell, 'step5_running.png', '图 5  步骤 5：作业提交成功，12 个 Map 任务并行执行中', IMG_W)
cell_p(cell, '作业约 2 分钟完成：12 个 Map 与 1 个 Reduce 任务全部成功，失败的 Shuffle、错误'
             '记录数均为 0；Combine 把 73623 条 Map 输出记录局部聚合为 12384 条，最终输出 '
             '5869 条倒排索引记录：', indent=2)
cell_image(cell, 'step5_done.png', '图 6  步骤 5：作业运行统计（Counters）', IMG_W)

cell_p(cell, '（6）查看倒排索引结果', bold=True, before=2)
cell_p(cell, '作业输出保存在 HDFS 输出目录的 part-r-00000 文件中（352 KB），下载到本地 '
             'results/：', indent=2)
cell_code(cell, '''$ hdfs dfs -ls /user/lfr/lab2/output
$ hdfs dfs -get -f /user/lfr/lab2/output/part-r-00000 results/
$ wc -l results/part-r-00000      # 5869 条索引记录（去重后的词项数）''')
cell_image(cell, 'step6.png', '图 7  步骤 6：倒排索引结果（前 12 行，每行一个词项的词典与倒排记录表）', IMG_W)

cell_p(cell, '（7）单词检索示例', bold=True, before=2)
cell_p(cell, '在结果文件中查询单词，即得到该词出现在哪些文档、各出现多少次。例如查询 data、'
             'hadoop、mapreduce、search、index 五个单词：', indent=2)
cell_image(cell, 'step7.png', '图 8  步骤 7：单词检索示例（grep 查询倒排索引文件）', IMG_W)
cell_p(cell, '以 hadoop 为例：hadoop <document01.txt,91>;<document02.txt,36>;'
             '<document03.txt,16>;<document04.txt,5>;<total,148>.，说明该词在 4 篇 '
             'Hadoop/Spark 文档中共出现 148 次（MapReduce 教程 91 次、HDFS 文档 36 次），与'
             '文档主题一致；data 出现于全部 12 篇文档、总计 376 次，mapreduce 126 次，'
             'search 56 次，index 20 次。结果与文档语义相符，验证了倒排索引的正确性。', indent=2)
cell_tail(cell)

# ============ 结论分析与体会 ============
cell = table.rows[7].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
for item in [
    '1. 对倒排索引的理解：倒排索引把“文档→词”的正排关系反转为“词→文档列表”，配合词频就'
    '有了加权检索的基础，查询时定位单词即可直接读出文档列表，这正是搜索引擎“毫秒级”响应'
    '的关键数据结构。本实验 12 篇文档共 11.8 万词，去停词后仍有 5869 个不同词项，若进一步'
    '按倒排记录表有序压缩（如差值编码），规模还能更小，为后续索引压缩实验留下空间。',
    '2. 对 MapReduce 编程模型的理解：倒排索引构建被自然分解为“分词打标记（Map）→ 局部'
    '聚合（Combine）→ 按词分组汇总（Reduce）”三段，程序员只需编写 Mapper 与 Reducer 的'
    '业务逻辑，排序、分组、容错、并行调度全部由框架完成；Shuffle 自动把相同单词的记录'
    '汇聚到同一 Reduce 分组，生动体现了“移动计算而不是移动数据”的设计思想。',
    '3. 工程细节上的收获：（1）文档名无法预先获知，必须通过 ctx.getInputSplit() 取 '
    'FileSplit 的文件名，这是“以文件名作为文档编号”的关键；（2）Combiner 与 Reducer '
    '聚合逻辑相似但输出形态不同，不能互换；（3）停词表放在 HDFS、经配置传入路径并在 '
    'setup() 中一次性读入内存，更新停词表无需重新编译程序；（4）过滤单字符与纯数字'
    '（如 RFC 文档中位图串）后，索引噪声明显减少、结果更整洁。总体而言，本实验完整走通了'
    '“语料采集→停词表设计→MapReduce 编程→集群运行→检索验证”的全流程。',
    '4. 实验代码、数据与结果已整理至 GitHub 公开仓库：https://github.com/mhy668/bigData'
    '（实验二内容位于 bigdata-lab2/ 目录）。',
]:
    cell_p(cell, item, indent=2)
cell_tail(cell)

# ============ 问答题 ============
cell = table.rows[8].cells[0]
clear_empty_paragraphs(cell, keep_tail=0)
cell_p(cell, '问题 1：Reducer 汇总某单词的倒排记录表时，为什么用 TreeMap 而不是 HashMap？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：同一单词的各文档词频由多个 Map 任务产生，到达 Reducer 的顺序不确定。若使用'
             'HashMap，输出中 <document01.txt,…>、<document02.txt,…> 的顺序会随运行变化，'
             '结果不稳定也不易阅读。TreeMap 基于红黑树实现，put/merge 复杂度为 O(log n)，'
             '遍历时天然按文档名升序输出，正好满足“倒排记录表按文档编号有序”的要求，'
             '也便于人工核对和后续多词项归并（求交集/并集）。', indent=2)
cell_p(cell, '问题 2：为什么本实验的倒排索引作业要设置 Combiner？它与 Reducer 有何区别和联系？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：Mapper 对每行每个词都输出一条记录，同一单词在同一文档中会被重复输出多次，'
             '若全部直接传给 Reducer，Shuffle 阶段的网络传输与磁盘 IO 开销巨大。Combiner 在 '
             'Map 端先做一次“局部的 Reduce”，把同一文档内同一单词的计数合并——本实验 73623 '
             '条 Map 输出记录被压缩为 12384 条（约 5.9 倍）。二者聚合逻辑相同、都满足结合律与'
             '交换律（本实验为求和）；区别在于 Combiner 输入输出类型须与 Mapper 输出一致、只做'
             '部分聚合，而 Reducer 看到的是一个单词的全部分区数据，负责最终汇总与格式化输出。', indent=2)
cell_p(cell, '问题 3：停词表为什么做成独立文件并在 Mapper.setup() 中读取，而不是写死在程序中？',
       bold=True, indent=0, before=2)
cell_p(cell, '答：写死在程序中有三个缺点：修改停词表必须重新编译打包；内容与程序逻辑耦合、不可复用；'
             '无法按任务切换不同语言的停词表。本实验把停词表做成文本文件并上传到 HDFS，通过 '
             'conf.set("invertedindex.stopwords.path", …) 传入路径，Mapper 在每个 Map 任务开始'
             '时于 setup() 中一次性读入内存集合：更新停词表只需替换 HDFS 上的文件，无需改代码；'
             'setup() 每任务只执行一次，避免了在 map() 中按行反复读文件的巨大 IO 开销。', indent=2)
cell_tail(cell)

doc.save(OUT)
print('已生成报告（按模板填充）: ' + OUT)
