import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.URI;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * 实验四：K-Means 聚类的 MapReduce（并行）实现。
 *
 * 与串行版（kmeans_serial.py）使用完全相同的初始质心、距离计算（整数坐标的
 * 欧氏距离平方、平局取小编号）、质心更新（坐标和/点数）与固定迭代次数，
 * 因此两种实现的聚类结果逐位一致。
 *
 * 质心文件格式：C<idx>\t<sumX>\t<sumY>\t<count>（均为整数，质心 = sum/count）
 *
 * 用法：KMeansMR <input> <outBase> <iterations> <localResultsDir>
 */
public class KMeansMR {

    static final int K = 5;
    static final int ITER = 10;
    // 初始质心：(sumX, sumY, count) —— 与串行版一致
    static final long[][] INIT = {
            {0, 0, 1}, {1000, 0, 1}, {0, 1000, 1}, {1000, 1000, 1}, {500, 500, 1}
    };

    /** 从 HDFS 读取质心文件。 */
    static long[][] readCentroids(Configuration conf, String path) throws IOException {
        long[][] c = new long[K][3];
        FileSystem fs = FileSystem.get(URI.create(path), conf);
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(fs.open(new Path(path)), "UTF-8"))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) {
                    continue;
                }
                String[] p = line.split("\t");
                int idx = Integer.parseInt(p[0].substring(1));
                c[idx][0] = Long.parseLong(p[1]);
                c[idx][1] = Long.parseLong(p[2]);
                c[idx][2] = Long.parseLong(p[3]);
            }
        }
        return c;
    }

    static int nearest(double x, double y, long[][] cents) {
        int best = 0;
        double bestD = Double.MAX_VALUE;
        for (int k = 0; k < K; k++) {
            long n = cents[k][2];
            double cx = n == 0 ? 0.0 : cents[k][0] / (double) n;
            double cy = n == 0 ? 0.0 : cents[k][1] / (double) n;
            double dx = x - cx, dy = y - cy;
            double d = dx * dx + dy * dy;
            if (d < bestD) {   // 平局取簇编号小者
                bestD = d;
                best = k;
            }
        }
        return best;
    }

    /** 迭代 Mapper：把每个点分配到最近的簇。 */
    public static class IterMapper extends Mapper<LongWritable, Text, IntWritable, Text> {
        private long[][] cents;

        @Override
        protected void setup(Context context) throws IOException, InterruptedException {
            cents = readCentroids(context.getConfiguration(),
                    context.getConfiguration().get("kmeans.centroids.path"));
            // 每个簇都发一条哨兵记录，保证空簇也能进入 Reduce 保持质心不变
            for (int k = 0; k < K; k++) {
                context.write(new IntWritable(k), new Text("S"));
            }
        }

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty()) {
                return;
            }
            String[] p = line.split(",");
            double x = Double.parseDouble(p[1]);
            double y = Double.parseDouble(p[2]);
            int k = nearest(x, y, cents);
            context.write(new IntWritable(k), new Text(p[1] + "," + p[2]));
        }
    }

    /** 迭代 Reducer：累加坐标和与点数，得到新的质心（sum, count）。 */
    public static class IterReducer extends Reducer<IntWritable, Text, Text, Text> {
        private long[][] old;

        @Override
        protected void setup(Context context) throws IOException {
            old = readCentroids(context.getConfiguration(),
                    context.getConfiguration().get("kmeans.centroids.path"));
        }

        @Override
        protected void reduce(IntWritable key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            long sx = 0, sy = 0, n = 0;
            for (Text v : values) {
                String s = v.toString();
                if (s.equals("S")) {
                    continue;
                }
                String[] p = s.split(",");
                sx += Long.parseLong(p[0]);
                sy += Long.parseLong(p[1]);
                n++;
            }
            if (n == 0) {          // 空簇：沿用原来的质心
                sx = old[key.get()][0];
                sy = old[key.get()][1];
                n = old[key.get()][2];
            }
            context.write(new Text("C" + key.get()),
                    new Text(sx + "\t" + sy + "\t" + n));
        }
    }

    /** 输出每个点最终所属的簇：P00001 \t <簇编号> */
    public static class AssignMapper extends Mapper<LongWritable, Text, Text, Text> {
        private long[][] cents;

        @Override
        protected void setup(Context context) throws IOException {
            cents = readCentroids(context.getConfiguration(),
                    context.getConfiguration().get("kmeans.centroids.path"));
        }

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty()) {
                return;
            }
            String[] p = line.split(",");
            double x = Double.parseDouble(p[1]);
            double y = Double.parseDouble(p[2]);
            context.write(new Text(p[0]), new Text(String.valueOf(nearest(x, y, cents))));
        }
    }

    /** 计算整数化簇内平方误差：Σ (x·n - Sx)² + (y·n - Sy)² */
    public static class SseMapper extends Mapper<LongWritable, Text, IntWritable, LongWritable> {
        private long[][] cents;

        @Override
        protected void setup(Context context) throws IOException {
            cents = readCentroids(context.getConfiguration(),
                    context.getConfiguration().get("kmeans.centroids.path"));
        }

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty()) {
                return;
            }
            String[] p = line.split(",");
            long x = Long.parseLong(p[1]);
            long y = Long.parseLong(p[2]);
            int k = nearest(x, y, cents);
            long n = cents[k][2];
            long dx = x * n - cents[k][0];
            long dy = y * n - cents[k][1];
            context.write(new IntWritable(k), new LongWritable(dx * dx + dy * dy));
        }
    }

    public static class SseReducer extends Reducer<IntWritable, LongWritable, Text, LongWritable> {
        @Override
        protected void reduce(IntWritable key, Iterable<LongWritable> values, Context context)
                throws IOException, InterruptedException {
            long sum = 0;
            for (LongWritable v : values) {
                sum += v.get();
            }
            context.write(new Text("C" + key.get()), new LongWritable(sum));
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("Usage: KMeansMR <input> <outBase> <iterations> <localResultsDir>");
            System.exit(2);
        }
        String input = args[0];
        String outBase = args[1];
        int iterations = Integer.parseInt(args[2]);
        String localDir = args[3];

        Configuration conf = new Configuration();
        FileSystem fs = FileSystem.get(conf);
        Path stage = new Path(outBase + "_stage");
        fs.delete(stage, true);
        fs.delete(new Path(outBase + "_assignments"), true);
        fs.delete(new Path(outBase + "_sse"), true);

        // 1) 写入初始质心
        String centsPath = new Path(stage, "centroids_0.txt").toString();
        try (FSDataOutputStream out = fs.create(new Path(centsPath), true)) {
            for (int k = 0; k < K; k++) {
                out.write(("C" + k + "\t" + INIT[k][0] + "\t" + INIT[k][1] + "\t" + INIT[k][2] + "\n")
                        .getBytes("UTF-8"));
            }
        }
        System.out.println("点数输入: " + input + "，簇数: " + K + "，迭代次数: " + iterations);

        // 2) 迭代
        for (int i = 1; i <= iterations; i++) {
            Job job = Job.getInstance(conf, "KMeans-Iter-" + i);
            job.setJarByClass(KMeansMR.class);
            job.setMapperClass(IterMapper.class);
            job.setReducerClass(IterReducer.class);
            job.setNumReduceTasks(1);
            job.setMapOutputKeyClass(IntWritable.class);
            job.setMapOutputValueClass(Text.class);
            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(Text.class);
            job.getConfiguration().set("kmeans.centroids.path", centsPath);
            FileInputFormat.addInputPath(job, new Path(input));
            Path out = new Path(stage, "iter_" + i);
            FileOutputFormat.setOutputPath(job, out);
            if (!job.waitForCompletion(true)) {
                System.exit(1);
            }
            centsPath = new Path(out, "part-r-00000").toString();
            long[][] cents = readCentroids(conf, centsPath);
            StringBuilder sb = new StringBuilder(">>> 第 " + i + " 次迭代: ");
            for (int k = 0; k < K; k++) {
                long n = cents[k][2];
                sb.append(String.format("C%d=(%.4f,%.4f)[%d] ", k,
                        cents[k][0] / (double) n, cents[k][1] / (double) n, n));
            }
            System.out.println(sb.toString());
        }

        // 3) 最终结果：各点所属簇
        long[][] finalC = readCentroids(conf, centsPath);
        Job aj = Job.getInstance(conf, "KMeans-Assignments");
        aj.setJarByClass(KMeansMR.class);
        aj.setMapperClass(AssignMapper.class);
        aj.setNumReduceTasks(0);
        aj.setOutputKeyClass(Text.class);
        aj.setOutputValueClass(Text.class);
        aj.getConfiguration().set("kmeans.centroids.path", centsPath);
        FileInputFormat.addInputPath(aj, new Path(input));
        FileOutputFormat.setOutputPath(aj, new Path(outBase + "_assignments"));
        if (!aj.waitForCompletion(true)) {
            System.exit(1);
        }

        // 4) 最终结果：整数化簇内平方误差
        Job sj = Job.getInstance(conf, "KMeans-SSE");
        sj.setJarByClass(KMeansMR.class);
        sj.setMapperClass(SseMapper.class);
        sj.setReducerClass(SseReducer.class);
        sj.setNumReduceTasks(1);
        sj.setMapOutputKeyClass(IntWritable.class);
        sj.setMapOutputValueClass(LongWritable.class);
        sj.setOutputKeyClass(Text.class);
        sj.setOutputValueClass(LongWritable.class);
        sj.getConfiguration().set("kmeans.centroids.path", centsPath);
        FileInputFormat.addInputPath(sj, new Path(input));
        FileOutputFormat.setOutputPath(sj, new Path(outBase + "_sse"));
        if (!sj.waitForCompletion(true)) {
            System.exit(1);
        }

        // 5) 写本地结果文件（与串行版格式一致，便于 diff 比较）
        PrintWriter cw = new PrintWriter(localDir + "/parallel_centroids.txt", "UTF-8");
        PrintWriter zw = new PrintWriter(localDir + "/parallel_sizes.txt", "UTF-8");
        for (int k = 0; k < K; k++) {
            long n = finalC[k][2];
            cw.printf("C%d\t%.10f\t%.10f%n", k, finalC[k][0] / (double) n, finalC[k][1] / (double) n);
            zw.printf("C%d\t%d%n", k, n);
        }
        cw.close();
        zw.close();

        long total = 0;
        FileSystem lfs = FileSystem.get(conf);
        Path ssePart = new Path(outBase + "_sse", "part-r-00000");
        try (BufferedReader br = new BufferedReader(
                new InputStreamReader(lfs.open(ssePart), "UTF-8"))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    total += Long.parseLong(line.split("\t")[1]);
                }
            }
        }
        PrintWriter sw = new PrintWriter(localDir + "/parallel_sse.txt", "UTF-8");
        sw.printf("%d%n", total);
        sw.close();
        System.out.println("并行结果已写入 " + localDir);
    }
}
