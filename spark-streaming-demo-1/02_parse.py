from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, avg, date_format
from pyspark.sql.types import DoubleType, StructType, StructField, IntegerType, StringType, TimestampType

spark = (
    SparkSession.builder
    .appName("demo-02-parse")
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
    .option("startingOffsets", "earliest")
    .load()
)

parsed = (
    raw
    .selectExpr("CAST(value AS STRING) AS json_str")
    .select(from_json(col("json_str"), event_schema).alias("event"))
    .select("event.*")
)

agg = (parsed
    .withWatermark("event_time", "2 minutes")
    .groupBy(window("event_time", "1 minute"), "room")  # WINDOW != INTERVAL
    .agg(avg("temp").alias("avg_temp")))

out = agg.select(
    date_format(col("window.start"), "HH:mm:ss").alias("win_start"),
    date_format(col("window.end"),   "HH:mm:ss").alias("win_end"),
    "room",
    "avg_temp",
)

query = (
    out.writeStream
    .format("console")
    .outputMode("complete")   # switch to "append" for the watermark-finalization demo
    .trigger(processingTime="10 seconds")
    .start()
)

query.awaitTermination()