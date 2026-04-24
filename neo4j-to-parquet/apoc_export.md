# Neo4j → Parquet via APOC Export

Two-step pipeline: export from Neo4j with APOC, then shape the data with Spark.

## 1. Prerequisites

**APOC plugin** — APOC comes in two flavors:

- **APOC Core** — bundled with recent Neo4j versions (5.x+), includes basic export procedures like `apoc.export.csv.*`
- **APOC Extended** — separate install, adds Parquet export and other advanced features

For this approach, APOC Core is sufficient. To verify it's installed, in Neo4j Browser:

```cypher
RETURN apoc.version()
```

**Enable file export** — by default, Neo4j disables writing files from Cypher for security. Edit `neo4j.conf` (find it via Neo4j Desktop → your DB → `...` menu → Settings, or in the config folder):

```
apoc.export.file.enabled=true
```

Restart the database after changing this.

**Export directory** — by default, APOC writes to Neo4j's `import/` folder. You can specify absolute paths in the export call, but only if you also set:

```
dbms.security.allow_csv_import_from_file_urls=true
```

For this demo, we'll use the default `import/` location — no extra config needed.

## 2. Export from Neo4j (Cypher)

Run these in Neo4j Browser or via cypher-shell. Each writes one CSV to the `import/` folder.

### Accounts

```cypher
CALL apoc.export.csv.query(
  "MATCH (a:Account)
   RETURN
     a.id   AS account_id,
     a.type AS account_type
     // ADD DERIVED NODE PROPERTIES HERE
     // , a.fraud_score AS fraud_score
     // , a.fan_in      AS fan_in
   ORDER BY a.id",
  "accounts.csv",
  {}
)
```

### Transactions

```cypher
CALL apoc.export.csv.query(
  "MATCH (orig:Account)-[t:TRANSACTION]->(dest:Account)
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
   ORDER BY t.step",
  "transactions.csv",
  {}
)
```

APOC streams results directly to disk — no memory pressure on the driver or on Spark. Even at full PaySim scale, this runs in seconds.

### Verify the export

Each call returns a summary row showing how many rows were written, time elapsed, etc. Example:

```
file: "accounts.csv"
source: "statement: ..."
rows: 1738
time: 142
```

Confirm the files exist in Neo4j's `import/` folder.

## 3. Locate the exported files

APOC writes to `<neo4j_home>/import/`. In Neo4j Desktop:

1. Right-click the database → **Open folder** → **Import**
2. You'll see `accounts.csv` and `transactions.csv`

For the Spark job, either:

- Copy the files to the Spark job's working directory, or
- Point Spark at the import folder directly

Copying is cleaner (keeps Spark's inputs local to its own workspace). A simple shell copy is enough:

```
cp <neo4j_home>/import/accounts.csv ./input/
cp <neo4j_home>/import/transactions.csv ./input/
```

## 4. Convert CSVs to Parquet (Spark)

From here, the pipeline is effectively the same as the original `csv_to_parquet.py`, with two differences:

1. Only two CSVs to read (accounts and transactions), not four
2. Build `dim_transaction_type` and `dim_date` from the transaction data rather than loading them

```python
import os, sys
from datetime import datetime, timedelta
from pathlib import Path

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, DoubleType, DateType,
)

# -------------------------------------------------------------
# Config
# -------------------------------------------------------------
INPUT_DIR  = Path("./input")
OUTPUT_DIR = Path("./parquet_from_apoc")
START_DATE = datetime(2026, 3, 1)


# -------------------------------------------------------------
# Schemas — keep in sync with the APOC export RETURN clauses
# -------------------------------------------------------------
ACCOUNT_SCHEMA = StructType([
    StructField("account_id",   StringType(), False),
    StructField("account_type", StringType(), False),
    # ADD DERIVED NODE PROPERTIES HERE
])

TRANSACTION_SCHEMA = StructType([
    StructField("nameOrig",       StringType(),  False),
    StructField("nameDest",       StringType(),  False),
    StructField("step",           IntegerType(), False),
    StructField("type",           StringType(),  False),
    StructField("amount",         DoubleType(),  False),
    StructField("oldbalanceOrg",  DoubleType(),  False),
    StructField("newbalanceOrig", DoubleType(),  False),
    StructField("oldbalanceDest", DoubleType(),  False),
    StructField("newbalanceDest", DoubleType(),  False),
    StructField("isFraud",        IntegerType(), False),
    # ADD DERIVED EDGE PROPERTIES HERE
])


def main():
    spark = (
        SparkSession.builder
        .appName("apoc-csv-to-parquet")
        .getOrCreate()
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # Read the APOC exports
    # -------------------------------------------------------------
    accounts = (
        spark.read
        .option("header", True)
        .schema(ACCOUNT_SCHEMA)
        .csv(str(INPUT_DIR / "accounts.csv"))
    )

    transactions = (
        spark.read
        .option("header", True)
        .schema(TRANSACTION_SCHEMA)
        .csv(str(INPUT_DIR / "transactions.csv"))
    )

    # -------------------------------------------------------------
    # Build dim_account — assign surrogate keys
    # -------------------------------------------------------------
    w = Window.orderBy("account_id")
    dim_account = accounts.withColumn("account_key", row_number().over(w))

    # -------------------------------------------------------------
    # Build dim_transaction_type — distinct types from transactions
    # -------------------------------------------------------------
    w = Window.orderBy("type_name")
    dim_transaction_type = (
        transactions.select(col("type").alias("type_name"))
        .distinct()
        .withColumn("type_key", row_number().over(w))
    )

    # -------------------------------------------------------------
    # Build dim_date — generated from max step value
    # -------------------------------------------------------------
    max_step = transactions.agg({"step": "max"}).collect()[0][0]
    date_rows = []
    for step in range(1, max_step + 1):
        dt = START_DATE + timedelta(hours=step - 1)
        date_rows.append((
            step,
            dt.strftime("%Y-%m-%d %H:00:00"),
            dt.date(),
            dt.hour,
            dt.strftime("%A"),
        ))
    dim_date = spark.createDataFrame(
        date_rows,
        StructType([
            StructField("date_key",    IntegerType(), False),
            StructField("datetime",    StringType(),  False),
            StructField("date",        DateType(),    False),
            StructField("hour",        IntegerType(), False),
            StructField("day_of_week", StringType(),  False),
        ])
    )

    # -------------------------------------------------------------
    # Build fact_transactions — resolve foreign keys via joins
    # -------------------------------------------------------------
    # Resolve type_key
    fact = transactions.join(
        dim_transaction_type,
        transactions.type == dim_transaction_type.type_name,
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

    # date_key == step, then join in `date` for partitioning
    fact = fact.withColumn("date_key", col("step"))
    fact = fact.join(
        dim_date.select("date_key", "date"),
        on="date_key",
        how="inner",
    )

    # Assign transaction_id
    w = Window.orderBy("step")
    fact = fact.withColumn("transaction_id", row_number().over(w))

    # -------------------------------------------------------------
    # Write Parquet
    # -------------------------------------------------------------
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

    (fact
        .write.mode("overwrite")
        .option("compression", "snappy")
        .partitionBy("date")
        .parquet(str(OUTPUT_DIR / "fact_transactions")))

    print(f"Done. Output: {OUTPUT_DIR.resolve()}")
    spark.stop()


if __name__ == "__main__":
    main()
```