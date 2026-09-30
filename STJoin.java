import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * 实验三-3：挖掘祖孙辈关系（单表自连接）
 * 输入：每行 "child parent"；输出：每行 "grandchild grandparent"。
 * 原理：一张表当两张表用。
 *       对每条 (child, parent)：
 *         - 以 child 为 key，value="1"+parent（左表：key 的父辈 -> 祖辈候选）
 *         - 以 parent 为 key，value="2"+child（右表：key 的子辈 -> 孙辈候选）
 *       reduce 中，同一 key（中间人）聚合：把 "2" 组（孙辈）与 "1" 组（祖辈）做笛卡尔积，
 *       即得到 孙辈-祖辈 关系。
 */
public class STJoin {

    public static class Map extends Mapper<Object, Text, Text, Text> {
        @Override
        public void map(Object key, Text value, Context context)
                throws IOException, InterruptedException {
            String[] tokens = value.toString().trim().split("\\s+");
            if (tokens.length < 2) {
                return;
            }
            if ("child".equals(tokens[0])) { // 跳过表头行
                return;
            }
            String child = tokens[0];
            String parent = tokens[1];
            context.write(new Text(child), new Text("1" + parent));
            context.write(new Text(parent), new Text("2" + child));
        }
    }

    public static class Reduce extends Reducer<Text, Text, Text, Text> {
        @Override
        public void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            List<String> grandchild = new ArrayList<>();
            List<String> grandparent = new ArrayList<>();
            for (Text v : values) {
                String s = v.toString();
                if (s.startsWith("1")) {
                    grandparent.add(s.substring(1)); // key 的父辈
                } else if (s.startsWith("2")) {
                    grandchild.add(s.substring(1));  // key 的子辈
                }
            }
            for (String gc : grandchild) {
                for (String gp : grandparent) {
                    context.write(new Text(gc), new Text(gp));
                }
            }
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
        if (otherArgs.length < 2) {
            System.err.println("Usage: STJoin <in> <out>");
            System.exit(2);
        }
        Job job = Job.getInstance(conf, "single table join");
        job.setJarByClass(STJoin.class);
        job.setMapperClass(Map.class);
        job.setReducerClass(Reduce.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);
        FileInputFormat.addInputPath(job, new Path(otherArgs[0]));
        FileOutputFormat.setOutputPath(job, new Path(otherArgs[1]));
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
