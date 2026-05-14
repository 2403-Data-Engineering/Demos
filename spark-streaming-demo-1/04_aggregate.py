from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, from_json, avg, window
from pyspark.sql.types import DoubleType, StructType, StructField, IntegerType, StringType, TimestampType

spark = (
    SparkSession.builder
    .appName("demo-04-aggregate")
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

# groupBy on a stream is stateful — Spark holds a running avg per room.
# avgs = parsed.groupBy("room").agg(avg("temp").alias("avg_temp"))


# Watermark + windowed groupBy: state is bounded because old windows get evicted.
avgs = (parsed
    .withWatermark("event_time", "2 minutes")
    .groupBy(window("event_time", "1 minute"), "room")
    .agg(avg("temp").alias("avg_temp")))


out = avgs.select(
    date_format(col("window.start"), "HH:mm:ss").alias("window"),
    "room",
    "avg_temp",
)


query = (
    out.writeStream
    .format("console")
    .outputMode("append")
    .start()
)

query.awaitTermination()