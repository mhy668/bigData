import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hbase.Cell;
import org.apache.hadoop.hbase.CellUtil;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.Admin;
import org.apache.hadoop.hbase.client.ColumnFamilyDescriptorBuilder;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Delete;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.client.Table;
import org.apache.hadoop.hbase.client.TableDescriptorBuilder;
import org.apache.hadoop.hbase.util.Bytes;

/**
 * 实验三（第一部分）：HBase 数据操作 Java API 示例。
 *
 * 实现题目要求的 5 个方法，并把关系型数据库中的 Student、Course、SC 三张表
 * 转换为 HBase 存储（行键用名称，列族 info / Score，列限定符为具体字段）。
 */
public class HBaseDemo {

    private static Connection conn;

    /**
     * 创建表：tableName 为表名，fields 为列族名称数组。
     * 若表已存在则先删除再重建。
     */
    public static void createTable(String tableName, String[] fields) throws IOException {
        Admin admin = conn.getAdmin();
        TableName tn = TableName.valueOf(tableName);
        if (admin.tableExists(tn)) {
            admin.disableTable(tn);
            admin.deleteTable(tn);
            System.out.println("[createTable] 表 " + tableName + " 已存在，先删除");
        }
        TableDescriptorBuilder builder = TableDescriptorBuilder.newBuilder(tn);
        for (String f : fields) {
            builder.setColumnFamily(
                    ColumnFamilyDescriptorBuilder.newBuilder(Bytes.toBytes(f)).build());
        }
        admin.createTable(builder.build());
        admin.close();
        System.out.println("[createTable] 创建表 " + tableName + "，列族: " + String.join(",", fields));
    }

    /**
     * 添加（或覆盖）一行数据：fields 支持 "列族" 或 "列族:列限定符" 两种写法。
     */
    public static void addRecord(String tableName, String row,
                                 String[] fields, String[] values) throws IOException {
        Table table = conn.getTable(TableName.valueOf(tableName));
        Put put = new Put(Bytes.toBytes(row));
        for (int i = 0; i < fields.length; i++) {
            String[] cf = fields[i].split(":");
            byte[] family = Bytes.toBytes(cf[0]);
            byte[] qualifier = cf.length > 1 ? Bytes.toBytes(cf[1]) : Bytes.toBytes("");
            put.addColumn(family, qualifier, Bytes.toBytes(values[i]));
        }
        table.put(put);
        table.close();
        System.out.println("[addRecord] 表 " + tableName + " 行 " + row
                + " 写入 " + fields.length + " 个字段: " + String.join(",", fields));
    }

    /**
     * 浏览某一列：column 为列族名时列出该列族下所有列限定符的数据，
     * 为 "列族:列限定符" 时只列出该列的数据；某行没有该列时输出 null。
     */
    public static void scanColumn(String tableName, String column) throws IOException {
        Table table = conn.getTable(TableName.valueOf(tableName));
        String[] cf = column.split(":");
        Scan scan = new Scan();
        if (cf.length == 2) {
            // 浏览具体列：扫描全部行，缺失该列的行输出 null
            ResultScanner scanner = table.getScanner(scan);
            System.out.println("---- 浏览表 " + tableName + " 的列 [" + column + "] ----");
            for (Result r : scanner) {
                byte[] v = r.getValue(Bytes.toBytes(cf[0]), Bytes.toBytes(cf[1]));
                System.out.println("  " + Bytes.toString(r.getRow()) + " -> "
                        + (v == null ? "null" : Bytes.toString(v)));
            }
            scanner.close();
        } else {
            // 浏览列族：列出该列族下所有列限定符的数据
            scan.addFamily(Bytes.toBytes(cf[0]));
            ResultScanner scanner = table.getScanner(scan);
            System.out.println("---- 浏览表 " + tableName + " 的列 [" + column + "] ----");
            for (Result r : scanner) {
                List<String> cells = new ArrayList<String>();
                for (Cell cell : r.listCells()) {
                    cells.add(Bytes.toString(CellUtil.cloneQualifier(cell)) + "="
                            + Bytes.toString(CellUtil.cloneValue(cell)));
                }
                System.out.println("  " + Bytes.toString(r.getRow()) + " -> {"
                        + String.join(", ", cells) + "}");
            }
            scanner.close();
        }
        table.close();
    }

    /**
     * 修改指定单元格的数据（在题目 3 个参数的基础上增加 newValue：新的值）。
     */
    public static void modifyData(String tableName, String row, String column,
                                  String newValue) throws IOException {
        Table table = conn.getTable(TableName.valueOf(tableName));
        String[] cf = column.split(":");
        Get get = new Get(Bytes.toBytes(row));
        get.addColumn(Bytes.toBytes(cf[0]), Bytes.toBytes(cf[1]));
        Result old = table.get(get);
        byte[] oldV = old.getValue(Bytes.toBytes(cf[0]), Bytes.toBytes(cf[1]));
        Put put = new Put(Bytes.toBytes(row));
        put.addColumn(Bytes.toBytes(cf[0]), Bytes.toBytes(cf[1]), Bytes.toBytes(newValue));
        table.put(put);
        table.close();
        System.out.println("[modifyData] 表 " + tableName + " 行 " + row + " 列 " + column
                + ": " + (oldV == null ? "null" : Bytes.toString(oldV)) + " -> " + newValue);
    }

    /** 删除指定行的记录。 */
    public static void deleteRow(String tableName, String row) throws IOException {
        Table table = conn.getTable(TableName.valueOf(tableName));
        table.delete(new Delete(Bytes.toBytes(row)));
        table.close();
        System.out.println("[deleteRow] 已删除表 " + tableName + " 中的行 " + row);
    }

    /** 打印表名与全部记录（用于验证）。 */
    private static void dumpTable(String tableName) throws IOException {
        Table table = conn.getTable(TableName.valueOf(tableName));
        ResultScanner scanner = table.getScanner(new Scan());
        System.out.println("---- 表 " + tableName + " 的全部记录 ----");
        for (Result r : scanner) {
            List<String> cells = new ArrayList<String>();
            for (Cell cell : r.listCells()) {
                cells.add(Bytes.toString(CellUtil.cloneFamily(cell)) + ":"
                        + Bytes.toString(CellUtil.cloneQualifier(cell)) + "="
                        + Bytes.toString(CellUtil.cloneValue(cell)));
            }
            System.out.println("  " + Bytes.toString(r.getRow()) + " -> {" + String.join(", ", cells) + "}");
        }
        scanner.close();
        table.close();
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = HBaseConfiguration.create();
        conn = ConnectionFactory.createConnection(conf);

        System.out.println("========== 1. 创建表 ==========");
        createTable("Student", new String[]{"info"});
        createTable("Course", new String[]{"info"});
        createTable("SC", new String[]{"Score"});

        System.out.println();
        System.out.println("========== 2. 插入学生表 / 课程表 / 选课表数据 ==========");
        // 学生表：行键 = 姓名；学号、性别、年龄作为 info 列族下的列
        addRecord("Student", "Zhangsan",
                new String[]{"info:S_No", "info:S_Sex", "info:S_Age"},
                new String[]{"2015001", "male", "23"});
        addRecord("Student", "Mary",
                new String[]{"info:S_No", "info:S_Sex", "info:S_Age"},
                new String[]{"2015002", "female", "22"});
        addRecord("Student", "Lisi",
                new String[]{"info:S_No", "info:S_Sex", "info:S_Age"},
                new String[]{"2015003", "male", "24"});
        // 课程表：行键 = 课程名；课程号、学分作为 info 列族下的列
        addRecord("Course", "Math",
                new String[]{"info:C_No", "info:C_Credit"},
                new String[]{"123001", "2.0"});
        addRecord("Course", "Computer Science",
                new String[]{"info:C_No", "info:C_Credit"},
                new String[]{"123002", "5.0"});
        addRecord("Course", "English",
                new String[]{"info:C_No", "info:C_Credit"},
                new String[]{"123003", "3.0"});
        // 选课表：行键 = 学生姓名；列族 Score 下的列限定符为课程名，值为成绩
        addRecord("SC", "Zhangsan",
                new String[]{"Score:Math", "Score:English"},
                new String[]{"86", "69"});
        addRecord("SC", "Mary",
                new String[]{"Score:Computer Science", "Score:English"},
                new String[]{"77", "99"});
        addRecord("SC", "Lisi",
                new String[]{"Score:Math", "Score:Computer Science"},
                new String[]{"98", "95"});

        System.out.println();
        System.out.println("========== 3. 三张表的全部数据 ==========");
        dumpTable("Student");
        dumpTable("Course");
        dumpTable("SC");

        System.out.println();
        System.out.println("========== 4. 浏览列 ==========");
        scanColumn("Student", "info");            // 列族：列出全部列
        scanColumn("SC", "Score:Math");           // 具体列：Mary 没有该列，输出 null

        System.out.println();
        System.out.println("========== 5. 修改数据 ==========");
        modifyData("SC", "Zhangsan", "Score:Math", "90");
        scanColumn("SC", "Score:Math");

        System.out.println();
        System.out.println("========== 6. 删除行（先插入一条临时记录再删除） ==========");
        addRecord("Student", "Wangwu",
                new String[]{"info:S_No", "info:S_Sex", "info:S_Age"},
                new String[]{"2015004", "male", "25"});
        deleteRow("Student", "Wangwu");
        dumpTable("Student");

        conn.close();
    }
}
