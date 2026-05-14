from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, upper, lit
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType

spark = (
    SparkSession.builder
    .appName("demo-03-transform")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

event_schema = StructType([
    StructField("id", IntegerType()),
    StructField("user", StringType()),
    StructField("action", StringType()),
    StructField("event_time", TimestampType()),
])

raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "earliest")
    .load()
)

parsed = (
    raw
    .selectExpr("CAST(value AS STRING) AS json_str")
    .select(from_json(col("json_str"), event_schema).alias("event"))
    .select("event.*")
    .filter(col("id") >= 10)                       # drop early events
    .withColumn("user_upper", upper(col("user")))  # derived column
    .withColumn("source", lit("demo"))             # constant tag
)

query = (
    parsed.writeStream
    .format("console")
    .outputMode("append")
    .start()
)

query.awaitTermination()