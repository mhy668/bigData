import java.io.IOException;
import java.util.Arrays;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * 实验三（第二部分）：PageRank 的 MapReduce 实现。
 *
 * 输入文件每行：网页 \t 该网页链接到的网页集合（英文逗号分隔）
 * 共迭代 10 次，输出格式：(网页,PR值)，PR 值保留 10 位小数。
 *
 * 迭代公式（与经典教材一致，所有网页 PR 之和 = 网页数 N）：
 *      PR(A) = (1 - d) + d * Σ ( PR(Ti) / C(Ti) )
 * 其中 d = 0.85 为阻尼系数，C(Ti) 为网页 Ti 的出链数。
 */
public class PageRankMR {

    private static final double DAMPING = 0.85;

    /** 初始化：page \t links ——> page \t 1.0 \t links */
    public static class InitMapper extends Mapper<LongWritable, Text, Text, Text> {
        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty()) {
                return;
            }
            String[] parts = line.split("\t", -1);
            String page = parts[0].trim();
            String links = parts.length > 1 ? parts[1].trim() : "";
            context.write(new Text(page), new Text("1.0\t" + links));
        }
    }

    /** 迭代 Mapper：把当前 PR 平均分给出链，同时把图结构传递下去 */
    public static class IterMapper extends Mapper<LongWritable, Text, Text, Text> {
        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String[] parts = value.toString().split("\t", -1);
            if (parts.length < 2) {
                return;
            }
            String page = parts[0];
            double pr = Double.parseDouble(parts[1]);
            String links = parts.length > 2 ? parts[2].trim() : "";

            context.write(new Text(page), new Text("G|" + links));   // 图结构原样传递
            if (!links.isEmpty()) {
                String[] neighbors = links.split(",");
                double share = pr / neighbors.length;                // 每个出链分到的 PR
                for (String nb : neighbors) {
                    context.write(new Text(nb.trim()), new Text("P|" + share));
                }
            }
        }
    }

    /** 迭代 Reducer：累加各网页分到的 PR，代入阻尼公式得到新一轮 PR */
    public static class IterReducer extends Reducer<Text, Text, Text, Text> {
        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            double sum = 0.0;
            String links = "";
            for (Text v : values) {
                String s = v.toString();
                if (s.startsWith("P|")) {
                    sum += Double.parseDouble(s.substring(2));
                } else {
                    links = s.substring(2);
                }
            }
            double pr = (1 - DAMPING) + DAMPING * sum;
            context.write(key, new Text(String.valueOf(pr) + "\t" + links));
        }
    }

    /** 输出格式：page \t pr \t links ——> (page,0.1234567890) */
    public static class FormatMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String[] parts = value.toString().split("\t", -1);
            if (parts.length < 2) {
                return;
            }
            double pr = Double.parseDouble(parts[1]);
            context.write(new Text(String.format("(%s,%.10f)", parts[0], pr)),
                    NullWritable.get());
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: PageRankMR <input> <output> [iterations]");
            System.exit(2);
        }
        String input = args[0];
        String output = args[1];
        int iterations = args.length > 2 ? Integer.parseInt(args[2]) : 10;

        Configuration conf = new Configuration();
        // 可选的第 4 个参数：local —— 使用 Hadoop 本地运行器执行（不提交到 YARN），
        // 便于在内存较小的虚拟机/单机上快速验证同一套 MapReduce 代码
        if (args.length > 3 && "local".equalsIgnoreCase(args[3])) {
            conf.set("mapreduce.framework.name", "local");
            System.out.println(">>> 使用 Hadoop 本地运行器（local runner）");
        }
        FileSystem fs = FileSystem.get(conf);
        Path stage = new Path(output + "_stage");
        fs.delete(stage, true);
        fs.delete(new Path(output), true);

        // 1) 初始化：每个网页 PR = 1.0
        Job init = Job.getInstance(conf, "PageRank-Init");
        init.setJarByClass(PageRankMR.class);
        init.setMapperClass(InitMapper.class);
        init.setNumReduceTasks(0);
        init.setOutputKeyClass(Text.class);
        init.setOutputValueClass(Text.class);
        FileInputFormat.addInputPath(init, new Path(input));
        FileOutputFormat.setOutputPath(init, new Path(stage, "iter0"));
        if (!init.waitForCompletion(true)) {
            System.exit(1);
        }

        // 2) 迭代 10 次
        for (int i = 1; i <= iterations; i++) {
            Job job = Job.getInstance(conf, "PageRank-Iter-" + i);
            job.setJarByClass(PageRankMR.class);
            job.setMapperClass(IterMapper.class);
            job.setReducerClass(IterReducer.class);
            job.setNumReduceTasks(1);
            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(Text.class);
            FileInputFormat.addInputPath(job, new Path(stage, "iter" + (i - 1)));
            FileOutputFormat.setOutputPath(job, new Path(stage, "iter" + i));
            if (!job.waitForCompletion(true)) {
                System.exit(1);
            }
            System.out.println(">>> 第 " + i + " 次迭代完成");
        }

        // 3) 格式化输出：(网页,PR值)，PR 保留 10 位小数
        Job fmt = Job.getInstance(conf, "PageRank-Format");
        fmt.setJarByClass(PageRankMR.class);
        fmt.setMapperClass(FormatMapper.class);
        fmt.setNumReduceTasks(0);
        fmt.setOutputKeyClass(Text.class);
        fmt.setOutputValueClass(NullWritable.class);
        FileInputFormat.addInputPath(fmt, new Path(stage, "iter" + iterations));
        FileOutputFormat.setOutputPath(fmt, new Path(output));
        System.exit(fmt.waitForCompletion(true) ? 0 : 1);
    }
}
