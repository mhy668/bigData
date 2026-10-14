import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.HashSet;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * 实验二：文档倒排索引算法实现（MapReduce）
 *
 * 输入：若干英文文本文档 + 停词表
 * 输出：word <document01.txt,6>;<document02.txt,3>;<total,11>.
 *
 * 三个阶段的职责：
 *   Mapper   —— 对每个文档分词，过滤停词，输出 <word, "文档名:1">
 *   Combiner —— 在 Map 端先把同一文档内同一单词的计数合并，减小网络传输
 *   Reducer  —— 按单词汇总各文档词频，并按文档名升序拼接输出
 */
public class InvertedIndex {

    /** Mapper：输出 <单词, "文档名:1"> 形式的部分倒排记录 */
    public static class IndexMapper extends Mapper<LongWritable, Text, Text, Text> {

        private final Text outKey = new Text();
        private final Text outValue = new Text();
        private final Set<String> stopwords = new HashSet<String>();

        @Override
        protected void setup(Context context) throws IOException {
            // 停词表放在 HDFS 上，作业启动时读入内存；文件由命令行第三个参数指定
            Configuration conf = context.getConfiguration();
            String p = conf.get("invertedindex.stopwords.path", "");
            if (!p.isEmpty()) {
                FileSystem fs = FileSystem.get(URI.create(p), conf);
                BufferedReader reader = new BufferedReader(
                        new InputStreamReader(fs.open(new Path(p)), "UTF-8"));
                try {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        line = line.trim().toLowerCase();
                        if (!line.isEmpty() && !line.startsWith("#")) {
                            stopwords.add(line);
                        }
                    }
                } finally {
                    reader.close();
                }
            }
            System.out.println("[InvertedIndex] loaded " + stopwords.size() + " stopwords");
        }

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            // 通过输入分片取得当前文档的文件名，即 documentXX.txt
            FileSplit split = (FileSplit) context.getInputSplit();
            String docName = split.getPath().getName();

            // 统一小写，把非字母数字字符替换为空格后按空白分词
            String line = value.toString().toLowerCase();
            String[] tokens = line.replaceAll("[^a-z0-9]+", " ").split("\\s+");

            for (String token : tokens) {
                if (token.isEmpty() || token.length() < 2) {
                    continue;                       // 过滤空串和单字符片段
                }
                char first = token.charAt(0);
                if (first < 'a' || first > 'z') {
                    continue;                       // 过滤以数字开头的片段（如协议文本中的位图）
                }
                if (stopwords.contains(token)) {
                    continue;                       // 过滤停词
                }
                outKey.set(token);
                outValue.set(docName + ":1");
                context.write(outKey, outValue);
            }
        }
    }

    /** Combiner：合并同一文档内同一单词的计数，如 "document01.txt:3" */
    public static class IndexCombiner extends Reducer<Text, Text, Text, Text> {

        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            Map<String, Integer> perDoc = new TreeMap<String, Integer>();
            for (Text v : values) {
                String[] kv = v.toString().split(":");
                String doc = kv[0];
                int cnt = Integer.parseInt(kv[1]);
                Integer old = perDoc.get(doc);
                perDoc.put(doc, old == null ? cnt : old + cnt);
            }
            for (Map.Entry<String, Integer> e : perDoc.entrySet()) {
                context.write(key, new Text(e.getKey() + ":" + e.getValue()));
            }
        }
    }

    /** Reducer：按文档名升序汇总，输出 <document01.txt,6>;...;<total,11>. */
    public static class IndexReducer extends Reducer<Text, Text, Text, Text> {

        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            Map<String, Integer> perDoc = new TreeMap<String, Integer>();
            int total = 0;
            for (Text v : values) {
                String[] kv = v.toString().split(":");
                String doc = kv[0];
                int cnt = Integer.parseInt(kv[1]);
                Integer old = perDoc.get(doc);
                perDoc.put(doc, old == null ? cnt : old + cnt);
                total += cnt;
            }

            StringBuilder sb = new StringBuilder();
            for (Map.Entry<String, Integer> e : perDoc.entrySet()) {
                sb.append('<').append(e.getKey()).append(',').append(e.getValue()).append(">;");
            }
            sb.append("<total,").append(total).append(">.");

            context.write(key, new Text(sb.toString()));
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage: InvertedIndex <input> <output> <stopwords-hdfs-path>");
            System.exit(2);
        }

        Configuration conf = new Configuration();
        conf.set("invertedindex.stopwords.path", args[2]);

        Job job = Job.getInstance(conf, "Document Inverted Index");
        job.setJarByClass(InvertedIndex.class);

        job.setMapperClass(IndexMapper.class);
        job.setCombinerClass(IndexCombiner.class);
        job.setReducerClass(IndexReducer.class);

        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(Text.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
