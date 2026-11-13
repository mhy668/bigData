#!/bin/bash
# ==============================================================
# 实验三 步骤3b：HBase Shell 任务 3~5（增删列族/列、清空表、统计行数）
# ==============================================================
source "$(dirname "$0")/env.sh"

{
cat <<'HB'
puts ""
puts "########## 任务3：向已有表添加 / 删除列族或列 ##########"
puts "--- 添加列族 extra 并写入一列 ---"
alter 'Student', {NAME => 'extra'}
put 'Student', 'Zhangsan', 'extra:phone', '13800001111'
get 'Student', 'Zhangsan', {COLUMNS => 'extra:phone'}
puts "--- 删除列 extra:phone ---"
delete 'Student', 'Zhangsan', 'extra:phone'
scan 'Student', {COLUMNS => 'extra'}
puts "--- 删除列族 extra ---"
alter 'Student', {NAME => 'extra', METHOD => 'delete'}
puts "列族 extra 已删除"
puts ""
puts "########## 任务4：清空指定表的所有记录数据 ##########"
if exists 'TempTable'
  disable 'TempTable'
  drop 'TempTable'
end
create 'TempTable', {NAME => 'info'}
put 'TempTable', 'r1', 'info:c1', 'v1'
put 'TempTable', 'r2', 'info:c1', 'v2'
puts "--- 清空前 ---"
count 'TempTable'
truncate 'TempTable'
puts "--- 清空后 ---"
count 'TempTable'
puts ""
puts "########## 任务5：统计表的行数 ##########"
count 'Student'
exit
HB
} | hbase shell 2>/dev/null | grep -vE "^(Took|SLF4J)"
