#!/bin/bash
# ==============================================================
# 实验三 步骤3a：HBase Shell 任务 1~2（列出表 / 显示全部记录）
# ==============================================================
source "$(dirname "$0")/env.sh"

{
cat <<'HB'
puts ""
puts "########## 任务1：列出所有表的相关信息（表名、列族） ##########"
list
describe 'Student'
puts ""
puts "########## 任务2：在终端显示指定表的全部记录 ##########"
scan 'Student'
exit
HB
} | hbase shell 2>/dev/null | grep -vE "^(Took|SLF4J)"
