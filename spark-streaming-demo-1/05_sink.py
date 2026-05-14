from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, avg
from pyspark.sql.types import DoubleType, StructType, StructField, IntegerType, StringType, TimestampType

spark = (
    SparkSession.builder
    .appName("demo-05-parquet")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

event_schema = StructType([
    StructField("id", IntegerType()),
    StructField("room", StringType()),
    StructField("temp", DoubleType()),
    StructField("event_time", TimestampType()),
])

raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "sensors")
    .option("startingOffsets", "latest")
    .load()
)

parsed = (
    raw
    .selectExpr("CAST(value AS STRING) AS json_str")
    .select(from_json(col("json_str"), event_schema).alias("event"))
    .select("event.*")
)

windowed = (
    parsed
    .withWatermark("event_time", "2 minutes")
    .groupBy(
        window(col("event_time"), "1 minute"),
        col("room"),
    )
    .agg(avg("temp").alias("avg_temp"))
)

# Parquet sink requires append mode. Append works here because the
# watermark guarantees closed windows won't be revisited.
query = (
    windowed.writeStream
    .format("parquet")
    .option("path", "output/windowed_avgs")
    .option("checkpointLocation", "output/checkpoints")
    .outputMode("append")
    .start()
)


console = (
    windowed.writeStream
    .format("console")
    .outputMode("append")
    .start()
)

query.awaitTermination()
console.awaitTermination()