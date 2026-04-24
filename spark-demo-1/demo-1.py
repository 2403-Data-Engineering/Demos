import os, sys
os.environ["PYSPARK_PYTHON"] = f'{sys.executable}'
os.environ["PYSPARK_DRIVER_PYTHON"] = f'{sys.executable}'
# os.environ["HADOOP_HOME"] = r"C:\hadoop"
# os.environ["PATH"] = os.environ["HADOOP_HOME"] + r"\bin;" + os.environ["PATH"]
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col

spark = SparkSession.builder.appName("WordCount").getOrCreate()

df = spark.createDataFrame(
    [("the cat sat",), ("the dog ran",), ("the cat ran",)], ["line"]
    )

df.show()


(df.select(explode(split("line", " ")).alias("word"))  # map: line → words
    .filter(col("word")!= "the")                        # filter out the "the"s
    .groupBy("word")                                     # shuffle: group by key
    .count()                                             # reduce: count per key
    .show())


