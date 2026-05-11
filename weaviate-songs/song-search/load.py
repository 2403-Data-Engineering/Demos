import weaviate
import weaviate.classes.config as wc
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("song-loader").getOrCreate()

client = weaviate.connect_to_local()
print("Connected:", client.is_ready())


# Clean slate if collection already exists
if client.collections.exists("Song"):
    client.collections.delete("Song")

client.collections.create(
    name="Song",
    vectorizer_config=wc.Configure.Vectorizer.text2vec_transformers(),
    properties=[
        wc.Property(name="title", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="artist", data_type=wc.DataType.TEXT, skip_vectorization=True),
        wc.Property(name="combined_text", data_type=wc.DataType.TEXT),
        wc.Property(name="year", data_type=wc.DataType.INT),
        wc.Property(name="genre", data_type=wc.DataType.TEXT, skip_vectorization=True),
    ],
)

print("Song collection created.")



df = spark.read.csv("songs.csv", header=True, inferSchema=True)
print(f"Loaded {df.count()} rows from CSV")

songs = client.collections.get("Song")

# Open a batch context. The client buffers add_object calls and sends them
# in batched HTTP requests under the hood. `dynamic` lets the client decide
# batch size based on throughput.
with songs.batch.dynamic() as batch:
    # collect() pulls all rows into the driver as a list. Fine for small data;
    # use df.toLocalIterator() for very large datasets.
    for row in df.collect():
        # Build combined_text from the descriptive fields — this is the only
        # property that gets vectorized.
        combined_text = (
            f"{row.title} by {row.artist}. "
            f"{row.description} "
            f"Genre: {row.genre}."
        )
        # Add one object to the batch. We send raw properties only — Weaviate
        # calls the transformers container to generate the vector server-side.
        # Batches may flush mid-loop when the buffer fills.
        batch.add_object(properties={
            "title": row.title,
            "artist": row.artist,
            "combined_text": combined_text,
            "year": int(row.year),
            "genre": row.genre,
        })
# When the `with` block exits, any remaining buffered objects are flushed.

# Always check for failures — batch errors are silent by default
failed = songs.batch.failed_objects
if failed:
    print(f"WARNING: {len(failed)} objects failed to import")
    for f in failed[:3]:
        print(f)
else:
    print("All songs imported successfully.")

# Confirm the count
result = songs.aggregate.over_all(total_count=True)
print(f"Total songs in collection: {result.total_count}")

client.close()
spark.stop()