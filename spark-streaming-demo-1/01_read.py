from pyspark.sql import SparkSession

# The spark-sql-kafka package provides the Kafka connector.
# The _2.12 suffix must match Spark's Scala build (3.5.1 ships with 2.12).
spark = (
    SparkSession.builder
    .appName("demo-01-read")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# readStream (not read) returns a streaming DataFrame.
# "earliest" replays the whole topic; "latest" would only show new events.
stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "earliest")
    .load()
)

# Show the schema so students see what Kafka gives us.
stream.printSchema()

# Console sink — prints each micro-batch to stdout. Dev only.
query = (
    stream.writeStream
    .format("console")
    .outputMode("append")
    .start()
)

query.awaitTermination()