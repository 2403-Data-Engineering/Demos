from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("warmup")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    .getOrCreate()
)
spark.stop()