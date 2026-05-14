from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
spark.read.parquet("output/windowed_avgs").show(truncate=False)
exit()