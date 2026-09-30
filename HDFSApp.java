import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataInputStream;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IOUtils;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Scanner;

public class HDFSApp {

    private static FileSystem fs;
    private static final Scanner sc = new Scanner(System.in);

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        fs = FileSystem.get(conf);

        while (true) {
            System.out.println("\n========== HDFS 操作菜单 ==========");
            System.out.println(" 1. 上传文件（存在时选择追加/覆盖）");
            System.out.println(" 2. 下载文件（本地同名自动重命名）");
            System.out.println(" 3. 输出文件内容到终端");
            System.out.println(" 4. 显示文件权限/大小/创建时间/路径");
            System.out.println(" 5. 递归显示目录下所有文件信息");
            System.out.println(" 6. 创建/删除文件（父目录不存在自动创建）");
            System.out.println(" 7. 创建/删除目录（仅空目录可删除）");
            System.out.println(" 8. 向文件开头/结尾追加内容");
            System.out.println(" 9. 删除指定文件");
            System.out.println("10. 移动文件（源路径 -> 目的路径）");
            System.out.println(" 0. 退出");
            System.out.print("请选择: ");
            String choice = sc.nextLine().trim();
            try {
                switch (choice) {
                    case "1":  upload();           break;
                    case "2":  download();         break;
                    case "3":  cat();              break;
                    case "4":  fileInfo();         break;
                    case "5":  listDir();          break;
                    case "6":  createDeleteFile(); break;
                    case "7":  createDeleteDir();  break;
                    case "8":  appendContent();    break;
                    case "9":  deleteFile();       break;
                    case "10": moveFile();         break;
                    case "0":
                        fs.close();
                        System.out.println("已退出。");
                        return;
                    default:
                        System.out.println("无效选项，请重新输入。");
                }
            } catch (Exception e) {
                System.err.println("操作失败: " + e.getMessage());
            }
        }
    }

    /* 1. 上传：目标已存在时由用户选择追加到末尾或覆盖 */
    private static void upload() throws IOException {
        System.out.print("本地文件路径: ");
        String local = sc.nextLine().trim();
        System.out.print("HDFS 目标路径: ");
        String remote = sc.nextLine().trim();

        File localFile = new File(local);
        if (!localFile.exists() || !localFile.isFile()) {
            System.out.println("本地文件不存在: " + local);
            return;
        }
        Path dst = new Path(remote);
        FSDataOutputStream out;
        if (fs.exists(dst)) {
            System.out.print("目标文件已存在，追加(a)还是覆盖(o)? ");
            String c = sc.nextLine().trim().toLowerCase();
            out = c.startsWith("a") ? fs.append(dst) : fs.create(dst, true);
        } else {
            out = fs.create(dst);
        }
        InputStream in = new BufferedInputStream(new FileInputStream(localFile));
        IOUtils.copyBytes(in, out, 4096, true);
        System.out.println("上传完成: " + remote);
    }

    /* 2. 下载：本地存在同名文件时自动重命名 */
    private static void download() throws IOException {
        System.out.print("HDFS 源文件: ");
        String remote = sc.nextLine().trim();
        System.out.print("本地目标路径: ");
        String local = sc.nextLine().trim();

        Path src = new Path(remote);
        Path dst = new Path(local);
        if (new File(local).exists()) {
            dst = new Path(local + ".bak");
            System.out.println("本地已存在同名文件，自动重命名为: " + local + ".bak");
        }
        fs.copyToLocalFile(src, dst);
        System.out.println("下载完成: " + dst);
    }

    /* 3. 输出文件内容到终端 */
    private static void cat() throws IOException {
        System.out.print("HDFS 文件: ");
        String remote = sc.nextLine().trim();
        FSDataInputStream in = fs.open(new Path(remote));
        IOUtils.copyBytes(in, System.out, 4096, false);
        in.close();
        System.out.println();
    }

    /* 4. 显示单个文件信息 */
    private static void fileInfo() throws IOException {
        System.out.print("HDFS 文件: ");
        String remote = sc.nextLine().trim();
        printStatus(fs.getFileStatus(new Path(remote)));
    }

    /* 5. 递归显示目录下所有文件信息 */
    private static void listDir() throws IOException {
        System.out.print("HDFS 目录: ");
        String remote = sc.nextLine().trim();
        listRecursive(new Path(remote));
    }

    private static void listRecursive(Path dir) throws IOException {
        FileStatus[] items = fs.listStatus(dir);
        for (FileStatus st : items) {
            printStatus(st);
            if (st.isDirectory()) {
                listRecursive(st.getPath());
            }
        }
    }

    private static void printStatus(FileStatus st) {
        System.out.println("路径     : " + st.getPath());
        System.out.println("权限     : " + st.getPermission());
        System.out.println("大小     : " + st.getLen() + " 字节");
        System.out.println("修改时间 : " + formatTime(st.getModificationTime()));
        System.out.println("类型     : " + (st.isDirectory() ? "目录" : "文件"));
        System.out.println("----------------------------------------");
    }

    private static String formatTime(long millis) {
        return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date(millis));
    }

    /* 6. 创建/删除文件：父目录不存在时自动创建 */
    private static void createDeleteFile() throws IOException {
        System.out.print("HDFS 文件路径: ");
        String remote = sc.nextLine().trim();
        Path p = new Path(remote);
        System.out.print("创建(c)还是删除(d)? ");
        String c = sc.nextLine().trim().toLowerCase();

        if (c.startsWith("c")) {
            Path parent = p.getParent();
            if (parent != null && !fs.exists(parent)) {
                fs.mkdirs(parent);
                System.out.println("父目录不存在，已自动创建: " + parent);
            }
            FSDataOutputStream out = fs.create(p);
            out.close();
            System.out.println("文件已创建: " + remote);
        } else {
            System.out.println(fs.delete(p, false) ? "删除成功: " + remote : "删除失败(文件不存在)");
        }
    }

    /* 7. 创建/删除目录：创建时自动建父目录；删除时仅删除空目录 */
    private static void createDeleteDir() throws IOException {
        System.out.print("HDFS 目录路径: ");
        String remote = sc.nextLine().trim();
        Path p = new Path(remote);
        System.out.print("创建(c)还是删除(d)? ");
        String c = sc.nextLine().trim().toLowerCase();

        if (c.startsWith("c")) {
            fs.mkdirs(p);
            System.out.println("目录已创建: " + remote);
        } else {
            System.out.println(fs.delete(p, false)
                    ? "空目录已删除: " + remote
                    : "删除失败(目录不存在或非空)");
        }
    }

    /* 8. 追加内容：由用户指定追加到开头或结尾 */
    private static void appendContent() throws IOException {
        System.out.print("HDFS 文件: ");
        String remote = sc.nextLine().trim();
        Path p = new Path(remote);
        System.out.print("要追加的内容: ");
        String content = sc.nextLine();
        System.out.print("追加到开头(b)还是结尾(e)? ");
        String c = sc.nextLine().trim().toLowerCase();

        if (c.startsWith("e")) {
            FSDataOutputStream out = fs.append(p);
            out.write(content.getBytes("UTF-8"));
            out.close();
            System.out.println("已追加到结尾。");
        } else {
            byte[] newBytes = content.getBytes("UTF-8");
            byte[] oldBytes = readAll(p);
            fs.delete(p, false);
            FSDataOutputStream out = fs.create(p);
            out.write(newBytes);
            out.write(oldBytes);
            out.close();
            System.out.println("已追加到开头。");
        }
    }

    private static byte[] readAll(Path p) throws IOException {
        FSDataInputStream in = fs.open(p);
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buf = new byte[4096];
        int n;
        while ((n = in.read(buf)) != -1) {
            bos.write(buf, 0, n);
        }
        in.close();
        return bos.toByteArray();
    }

    /* 9. 删除指定文件 */
    private static void deleteFile() throws IOException {
        System.out.print("HDFS 文件: ");
        String remote = sc.nextLine().trim();
        Path p = new Path(remote);
        System.out.println(fs.delete(p, false) ? "删除成功: " + remote : "删除失败(文件不存在)");
    }

    /* 10. 移动文件 */
    private static void moveFile() throws IOException {
        System.out.print("源路径: ");
        String src = sc.nextLine().trim();
        System.out.print("目的路径: ");
        String dst = sc.nextLine().trim();
        System.out.println(fs.rename(new Path(src), new Path(dst))
                ? "移动成功: " + src + " -> " + dst
                : "移动失败");
    }
}
