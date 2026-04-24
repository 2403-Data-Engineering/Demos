# Neo4j → Parquet: Extraction Methods Overview

Three approaches to move data from Neo4j into a partitioned Parquet star schema, each with different trade-offs around scalability, setup complexity, and environment compatibility.

Remember, for Spark to work we need to be using python 3.11, so make sure to create a 3.11 virtual environment for any of these methods which utilize pyspark.
```
py -3.11 -m venv .venv
```

## Method 1 — Batched Python Driver (keyset pagination)

**Status: Complete and ready to use.**

Uses the official `neo4j` Python driver to pull data in batches, converts each batch to a Spark DataFrame, and writes Parquet incrementally. Pagination uses keyset/cursor-based iteration on `elementId(t)` — constant cost per batch regardless of dataset size.

- Memory stays bounded — only one batch in Python at a time
- Works with current Spark 4.x environment
- Tested end-to-end on the `smallsim` dataset
- Can handle full PaySim on a laptop without memory issues. Runtime depends on hardware and tuning — expect it to be the slowest of the three methods, but it will complete. Rough ballpark for ~6M transactions: 20-60 minutes on a typical laptop.

Relevant file: `extract_to_parquet_batched.py`

## Method 2 — Neo4j Spark Connector

**Status: Example code only, not runnable with current Spark version.**

Uses the Neo4j Spark Connector to read directly from Neo4j into Spark DataFrames. No Python driver involvement — data flows over Bolt straight into the JVM.

- Production-correct approach for scale
- Simpler code once configured
- **Blocked by Spark version**: the connector supports Spark 3.3, 3.4, and 3.5. Our environment runs Spark 4.1.1.

To use this approach you'd need to either downgrade PySpark to 3.5.x or wait for a Spark 4.x-compatible connector release.

Relevant file: `extract_to_parquet_connector.py` (marked as not runnable at the top)

## Method 3 — APOC Export

**Status: Expanded guide with example code, untested.**

Two-step pipeline: export CSVs from Neo4j using APOC procedures, then a separate Spark job reads the CSVs and writes the partitioned Parquet star schema.

- Export runs entirely inside Neo4j — no Python driver or Spark memory concerns during extraction
- Requires APOC installed and `apoc.export.file.enabled=true` configured in `neo4j.conf`
- Two-step workflow means intermediate CSV files on disk
- The Spark conversion step reuses most of the patterns from the original `csv_to_parquet.py`
- Not tested end-to-end; config instructions should be verified against current Neo4j version

Relevant file: `apoc_export_guide.md`

## Method 4 — APOC Export + pandas

**Status: Guide with example code, untested.**

Same first step as Method 3 — APOC exports CSVs from Neo4j. The difference is the conversion step uses pandas instead of Spark.

- Lighter weight than Method 3 — no Spark session or JVM required for the conversion
- Cleaner code for a simple CSV-to-Parquet transformation
- Only works when the data fits in memory (smallsim fine; full PaySim requires chunking)
- Requires `pandas` and `pyarrow` installed

Relevant file: `apoc_export_pandas_guide.md`

## Summary

| Method | Status | Current Spark 4.x? | Best for |
|---|---|---|---|
| 1. Batched Python driver | Ready | Yes | What students should use now |
| 2. Spark Connector | Example only | No | Future use on supported Spark |
| 3. APOC export + Spark | Untested guide | Yes | Clean separation, scales to large data |
| 4. APOC export + pandas | Untested guide | N/A | Clean separation, in-memory data |

For the immediate demo and student projects, **Method 1** is the working path. Methods 2, 3, and 4 are documented for reference and future revisiting.