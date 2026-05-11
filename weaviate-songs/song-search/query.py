import weaviate
from weaviate.classes.query import MetadataQuery, Filter

client = weaviate.connect_to_local()
songs = client.collections.get("Song")


print("Enter a search query: ")
query = input()


response = songs.query.near_text(
    query=query,
    limit=25,
    return_metadata=MetadataQuery(distance=True),
)


print("============================= RESULTS =============================")
for obj in response.objects:
    print(f"  {obj.properties['title']} — {obj.properties['artist']} (distance: {obj.metadata.distance:.3f})")
print("===================================================================")