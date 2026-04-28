import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, count, avg, max as spark_max

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = SparkSession.builder.appName("LibraryDemo").getOrCreate()


checkouts_data = [
    (1, "Alice",   101, 2024, 14),
    (2, "Bob",     102, 2024, 7),
    (3, "Carol",   101, 2023, 21),
    (4, "Dan",     103, 2024, 14),
    (5, "Eve",     102, 2025, 3),
    (6, "Frank",   104, 2024, 28),
    (7, "Grace",   103, 2023, 14),
    (8, "Heidi",   101, 2025, 7),
    (9, "Ivan",    104, 2024, 21),
    (10, "Judy",   102, 2024, 14),
]

checkouts_schema = [
    "checkout_id",
    "Patron",
    "book_id",
    "year",
    "days_borrowed"
]


checkout_dataframe = spark.createDataFrame(checkouts_data, checkouts_schema)

checkout_dataframe.createOrReplaceTempView("checkouts")

# print("Patrons")
# print("Schema: ")
# checkout_dataframe.printSchema()

# print("Show: ")
# checkout_dataframe.show()

# print("Count: ")
# print(checkout_dataframe.count())


books_data = [
    (101, "Dune",                "Sci-Fi"),
    (102, "Pride and Prejudice", "Romance"),
    (103, "The Great Gatsby",    "Fiction"),
    (104, "Sapiens",             "Non-Fiction"),
]

books_dataframe = spark.createDataFrame(
    books_data,
    ["book_id", "title", "genre"]
)


books_dataframe.createOrReplaceTempView("books")


# print("Books")
# print("Schema: ")
# books_dataframe.printSchema()

# print("Show: ")
# books_dataframe.show()

# print("Count: ")
# print(books_dataframe.count())


# I want patrons who borrowed for two weeks or more, and only checkouts from 2024 or later.
# How would we do this in SQL?
"""
SELECT *
FROM checkouts
WHERE year >= 2024
AND days_borrowed >= 14
"""

checkout_dataframe.select("checkout_id","Patron", "book_id", "year", "days_borrowed") \
    .filter((checkout_dataframe.year >= 2024) & (checkout_dataframe.days_borrowed >= 14)) \
    # .show()

checkout_dataframe.withColumn("loan_type", 
                              when(col("days_borrowed") <= 7, "short") \
                                .when(col("days_borrowed") <= 14, "standard") \
                                .otherwise("extended")
                              ) \
    # .show()


# joined_dataframe = checkout_dataframe.join(books_dataframe, "book_id")
joined_dataframe = checkout_dataframe.join(books_dataframe, checkout_dataframe.book_id == books_dataframe.book_id)
# joined_dataframe.show()


joined_dataframe.groupBy("genre").agg(
    count("*").alias("total_checkouts"),
    avg("days_borrowed").alias("avg_days"),
    spark_max("days_borrowed").alias("longest_loan")
).orderBy(col("total_checkouts").desc()).show()

spark.sql("""
    SELECT
        b.genre,
        COUNT(*) AS total_checkouts,
        AVG(c.days_borrowed) AS avg_days,
        MAX(c.days_borrowed) AS longest_loan
    FROM checkouts c
    JOIN books b
      ON c.book_id = b.book_id
    GROUP BY b.genre
    ORDER BY total_checkouts DESC
""").show()