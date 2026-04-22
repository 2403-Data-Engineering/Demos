import os, sys
os.environ["PYSPARK_PYTHON"] = f'{sys.executable}'
os.environ["PYSPARK_DRIVER_PYTHON"] = f'{sys.executable}'
# os.environ["HADOOP_HOME"] = r"C:\hadoop"
# os.environ["PATH"] = os.environ["HADOOP_HOME"] + r"\bin;" + os.environ["PATH"]
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

spark = SparkSession.builder.appName("Ridgeline").getOrCreate()

# Read CSVs using the DataFrame reader
stores_df = spark.read.csv("stores.csv", header=True, inferSchema=True)
products_df = spark.read.csv("products.csv", header=True, inferSchema=True)


# Show what we loaded
stores_df.show()
products_df.show()

# Check the inferred schema
stores_df.printSchema()
products_df.printSchema()

# Write them back down as JSON and PARQUET
products_df.write.mode("overwrite").json("products_json")
stores_df.write.mode("overwrite").parquet("stores_parquet")

# load the data back
products_from_json = spark.read.json("products_json")
products_from_json.show()

stores_from_parquet = spark.read.parquet("stores_parquet")
stores_from_parquet.show()



sc = spark.sparkContext
lines = sc.textFile("sales_data.csv")
header = lines.first()
data = lines.filter(lambda line: line != header)
print(f"Raw rows: {data.count()}")



