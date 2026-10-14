#!/bin/bash
# ==============================================================
# 实验二 步骤1：从公开网页下载 12 篇英文文档并转换为纯文本
# ==============================================================
LAB="$HOME/bigdata-lab2"
DOC="$LAB/data/documents"
WORK="$HOME/bigdata-lab2/.download"
mkdir -p "$DOC" "$WORK"
cd "$WORK"

# 文档编号 | 来源URL | 来源说明
LIST="
document01|https://hadoop.apache.org/docs/r3.3.6/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html|Apache Hadoop MapReduce Tutorial
document02|https://hadoop.apache.org/docs/r3.3.6/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html|Apache Hadoop HDFS Architecture
document03|https://hadoop.apache.org/docs/r3.3.6/hadoop-yarn/hadoop-yarn-site/YARN.html|Apache Hadoop YARN
document04|https://spark.apache.org/docs/latest/quick-start.html|Apache Spark Quick Start
document05|https://docs.python.org/3/howto/sorting.html|Python Sorting HOWTO
document06|https://docs.python.org/3/howto/regex.html|Python Regular Expression HOWTO
document07|https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control|Git - About Version Control
document08|https://developer.mozilla.org/en-US/docs/Learn/JavaScript/First_steps/What_is_JavaScript|MDN - What is JavaScript
document09|https://www.gnu.org/software/coreutils/manual/html_node/Introduction.html|GNU Coreutils Introduction
document10|https://www.rfc-editor.org/rfc/rfc791.txt|RFC 791 Internet Protocol
document11|https://www.rfc-editor.org/rfc/rfc1035.txt|RFC 1035 Domain Names
document12|https://www.rfc-editor.org/rfc/rfc2616.txt|RFC 2616 HTTP/1.1
"

echo "== 1) 下载文档（wget，共 12 篇） =="
echo "$LIST" | while IFS='|' read -r name url desc; do
    [ -z "$name" ] && continue
    echo "\$ wget -L -q -T 30 -O $name.raw \"$url\"       # $desc"
    wget -L -q -T 30 -O "$name.raw" "$url" || echo "!! download failed: $url"
done

echo
echo "== 2) 转换为纯文本（去掉 HTML 标签） =="
for f in "$WORK"/document*.raw; do
    name=$(basename "$f" .raw)
    python3 "$LAB/scripts/prepare_text.py" "$f" "$DOC/$name.txt" >/dev/null
done

echo
echo "== 3) 文档清单 =="
ls -l "$DOC"
echo
echo "== 4) 文档规模统计 =="
echo "\$ wc -w data/documents/*.txt > results/document_stats.txt; tail -1 results/document_stats.txt"
mkdir -p "$LAB/results"
wc -w "$DOC"/*.txt > "$LAB/results/document_stats.txt"
tail -1 "$LAB/results/document_stats.txt"
