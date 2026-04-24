# Spark needs to know which Python to use on Windows
import os, sys
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

"""
==================================================
Run this to check your spark and scala versions.
==================================================
"""
from pyspark.sql import SparkSession
s = SparkSession.builder.getOrCreate()
print(s.version)                          # Spark version
print(s.sparkContext._jvm.scala.util.Properties.versionString())  # Scala version



"""
=====================================================================================
The Neo4j Spark Connector currently supports only Spark 3.3, 3.4, and 3.5
(Scala 2.12 or 2.13). Our environment runs PySpark 4.1.1, which is not yet
supported by the connector.

To use this approach you would need to either:
  - Downgrade PySpark to 3.5.x (pip install "pyspark<4")
  - Wait for the Neo4j team to release a Spark 4.x compatible version

For now, use the batched Python driver approach (extract_to_parquet_batched.py)
instead. It scales to full PaySim via keyset pagination and works with our
current Spark version.

the code below is untested, and probably has issues. It is included as an example 
for completeness.
=====================================================================================

Extract data from Neo4j and write as partitioned Parquet star schema.

SPARK CONNECTOR VERSION — uses the Neo4j Spark Connector instead of the
Python driver. Data flows directly from Neo4j into Spark DataFrames without
passing through Python driver memory.

Key differences from the Python driver versions:
  - No `neo4j` Python driver import or session management
  - No pagination loop — the connector handles parallelism internally
  - Data is never materialized in Python; it goes Bolt -> JVM -> Spark
  - Scales horizontally when run on a real cluster

What students customize:
  - Add derived node properties to the accounts query RETURN clause
  - Add derived edge properties to the transactions query RETURN clause
  - Update CONNECTOR_VERSION and SCALA_VERSION if needed
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number, lit
from pyspark.sql.window import Window

# -------------------------------------------------------------
# Config
# -------------------------------------------------------------
NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "password"

# Connector version matching — see Neo4j Spark Connector compatibility matrix
# https://neo4j.com/docs/spark/current/
SCALA_VERSION     = "2.13"     # match your Spark's Scala version
CONNECTOR_VERSION = "5.4.0"    # latest stable as of early 2026

CONNECTOR_COORDINATE = (
    f"org.neo4j:neo4j-connector-apache-spark_{SCALA_VERSION}"
    f":{CONNECTOR_VERSION}_for_spark_3"
)

START_DATE = datetime(2026, 3, 1)
OUTPUT_DIR = Path("./parquet_from_neo4j")


# -------------------------------------------------------------
# SparkSession — the connector JAR is pulled automatically via
# spark.jars.packages. Must be set BEFORE the session starts.
# -------------------------------------------------------------
def create_spark():
    return (
        SparkSession.builder
        .appName("neo4j-to-parquet-connector")
        .config("spark.jars.packages", CONNECTOR_COORDINATE)
        # Optional: tune executor memory for large reads
        # .config("spark.executor.memory", "4g")
        .getOrCreate()
    )


# -------------------------------------------------------------
# Read directly from Neo4j into Spark DataFrames.
# The connector handles parallelism, partitioning, and memory management.
# -------------------------------------------------------------
def read_accounts(spark):
    return (
        spark.read.format("org.neo4j.spark.DataSource")
        .option("url", NEO4J_URI)
        .option("authentication.basic.username", NEO4J_USER)
        .option("authentication.basic.password", NEO4J_PASSWORD)
        .option("query", """
            MATCH (a:Account)
            RETURN
              a.id   AS account_id,
              a.type AS account_type
              // ADD DERIVED NODE PROPERTIES HERE
              // , a.fraud_score AS fraud_score
              // , a.fan_in      AS fan_in
        """)
        .load()
    )


def read_transactions(spark):
    return (
        spark.read.format("org.neo4j.spark.DataSource")
        .option("url", NEO4J_URI)
        .option("authentication.basic.username", NEO4J_USER)
        .option("authentication.basic.password", NEO4J_PASSWORD)
        .option("query", """
            MATCH (orig:Account)-[t:TRANSACTION]->(dest:Account)
            RETURN
              orig.id          AS nameOrig,
              dest.id          AS nameDest,
              t.step           AS step,
              t.type           AS type,
              t.amount         AS amount,
              t.oldbalanceOrg  AS oldbalanceOrg,
              t.newbalanceOrig AS newbalanceOrig,
              t.oldbalanceDest AS oldbalanceDest,
              t.newbalanceDest AS newbalanceDest,
              t.isFraud        AS isFraud
              // ADD DERIVED EDGE PROPERTIES HERE
        """)
        # Partitioning hint — tells the connector to split the read into
        # multiple parallel queries. Tune for your cluster.
        .option("partitions", "4")
        .load()
    )


# -------------------------------------------------------------
# Build dimension tables from the loaded DataFrames.
# All operations stay in Spark — no Python materialization.
# -------------------------------------------------------------
def build_dim_account(accounts_df):
    # Assign surrogate keys by row number ordered by account_id
    w = Window.orderBy("account_id")
    return accounts_df.withColumn("account_key", row_number().over(w))


def build_dim_transaction_type(transactions_df):
    w = Window.orderBy("type_name")
    return (
        transactions_df.select(col("type").alias("type_name"))
        .distinct()
        .withColumn("type_key", row_number().over(w))
    )


def build_dim_date(spark, transactions_df):
    # Get max step from the data
    max_step = transactions_df.agg({"step": "max"}).collect()[0][0]

    rows = []
    for step in range(1, max_step + 1):
        dt = START_DATE + timedelta(hours=step - 1)
        rows.append((
            step,
            dt.strftime("%Y-%m-%d %H:00:00"),
            dt.date(),
            dt.hour,
            dt.strftime("%A"),
        ))
    return spark.createDataFrame(
        rows,
        ["date_key", "datetime", "date", "hour", "day_of_week"]
    )


# -------------------------------------------------------------
# Assemble fact table — resolve foreign keys via joins.
# -------------------------------------------------------------
def build_fact_transactions(transactions_df, dim_account, dim_transaction_type, dim_date):
    # Resolve type_key
    fact = transactions_df.join(
        dim_transaction_type,
        transactions_df.type == dim_transaction_type.type_name,
        how="inner"
    ).drop("type_name", "type")

    # Resolve orig account key
    orig = dim_account.select(
        col("account_id").alias("orig_id"),
        col("account_key").alias("orig_account_key"),
    )
    fact = fact.join(orig, fact.nameOrig == orig.orig_id, how="inner").drop("orig_id", "nameOrig")

    # Resolve dest account key
    dest = dim_account.select(
        col("account_id").alias("dest_id"),
        col("account_key").alias("dest_account_key"),
    )
    fact = fact.join(dest, fact.nameDest == dest.dest_id, how="inner").drop("dest_id", "nameDest")

    # date_key == step in our model
    fact = fact.withColumn("date_key", col("step"))

    # Join in `date` from dim_date for partitioning
    fact = fact.join(
        dim_date.select("date_key", "date"),
        on="date_key",
        how="inner",
    )

    # Assign transaction_id
    w = Window.orderBy("step")
    fact = fact.withColumn("transaction_id", row_number().over(w))

    return fact


# -------------------------------------------------------------
# Write everything to Parquet.
# -------------------------------------------------------------
def write_all(dim_account, dim_transaction_type, dim_date, fact_transactions):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    (dim_account.coalesce(1)
        .write.mode("overwrite")
        .option("compression", "snappy")
        .parquet(str(OUTPUT_DIR / "dim_account")))

    (dim_transaction_type.coalesce(1)
        .write.mode("overwrite")
        .option("compression", "snappy")
        .parquet(str(OUTPUT_DIR / "dim_transaction_type")))

    (dim_date.coalesce(1)
        .write.mode("overwrite")
        .option("compression", "snappy")
        .parquet(str(OUTPUT_DIR / "dim_date")))

    (fact_transactions
        .write.mode("overwrite")
        .option("compression", "snappy")
        .partitionBy("date")
        .parquet(str(OUTPUT_DIR / "fact_transactions")))


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
def main():
    print(f"Starting Spark with connector {CONNECTOR_COORDINATE}...")
    spark = create_spark()

    print("Reading from Neo4j...")
    accounts_df = read_accounts(spark)
    transactions_df = read_transactions(spark)

    print("Building star schema...")
    dim_account = build_dim_account(accounts_df)
    dim_transaction_type = build_dim_transaction_type(transactions_df)
    dim_date = build_dim_date(spark, transactions_df)
    fact_transactions = build_fact_transactions(
        transactions_df, dim_account, dim_transaction_type, dim_date
    )

    print(f"Writing Parquet to {OUTPUT_DIR.resolve()}...")
    write_all(dim_account, dim_transaction_type, dim_date, fact_transactions)

    print("Done.")
    spark.stop()


if __name__ == "__main__":
    main()