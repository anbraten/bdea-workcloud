from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import re
import sys

basePath = 'file:///poor-hdfs/'

spark = SparkSession.builder \
      .appName("wordcloud") \
      .master("spark://spark:7077") \
      .getOrCreate()
      
sc = spark.sparkContext
sc.setLogLevel("ERROR")

filename=sys.argv[1]

txt = sc.textFile(basePath + 'uploads/' + filename)

# SOURCE: https://towardsdatascience.com/tf-idf-calculation-using-map-reduce-algorithm-in-pyspark-e89b5758e64c

# ['line one', ...] => [('word one', 1), ('word two', 1), ...]
words = txt.flatMap(lambda line: re.split('\W+', line.lower()))

# remove short / stop words
words = words.filter(lambda x: len(x) > 3)

# ['word one', 'word one', ...] => [('word one', 1), ('word one', 1), ...] => [('word one', 2)]
tf = words.map(lambda word: (word, 1)).reduceByKey(lambda a,b:a +b)

print("%i words are in the text file" % (tf.count()))

df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/postgres") \
    .option("dbtable", "df") \
    .option("user", "postgres") \
    .option("password", "passw0rd") \
    .load()

tfidf = tf.join(df.rdd).map(lambda x: (x[0], x[1][0] / x[1][1])) 

# TODO normalize tfidf

for i in tfidf.collect():
    print(i)

# sortedWordCounts = wordCounts.sortBy(lambda x: x[1])

schema = StructType([
        StructField('word', StringType(), False),
        StructField('tfidf', IntegerType(), False),
    ])
tfidf = spark.createDataFrame(tfidf, schema=schema)
tfidf.write \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://postgres:5432/postgres") \
    .option("dbtable", "tfidf") \
    .option("user", "postgres") \
    .option("password", "passw0rd") \
    .option("truncate", True) \
    .save(mode="overwrite")

print("%i words have been saved to database" % (tfidf.count()))

sc.stop()
spark.stop()
