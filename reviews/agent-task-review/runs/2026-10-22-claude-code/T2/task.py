import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

# Local sentence-transformers model, registered as LanceDB's embedding function.
model = get_registry().get("sentence-transformers").create(
    name="BAAI/bge-small-en-v1.5", device="cpu"
)


# SourceField: the text that gets embedded. VectorField: where LanceDB stores
# the embedding it generates. Together they make embedding automatic on add and search.
class Sentences(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()


db = lancedb.connect("./lancedb_data")
table = db.create_table("sentences", schema=Sentences, mode="overwrite")

table.add([
    {"text": "Cats often purr when they are content."},
    {"text": "Dogs need regular walks to stay healthy."},
    {"text": "Goldfish can live for more than ten years."},
    {"text": "Parrots can learn to imitate human speech."},
    {"text": "Rabbits are most active at dawn and dusk."},
])

query = "Which animal makes a soft rumbling sound when happy?"
results = table.search(query).limit(3).select(["text"]).to_pandas()

print(f"Query: {query}\n")
for rank, (_, row) in enumerate(results.iterrows(), start=1):
    print(f"{rank}. {row['text']}  (distance: {row['_distance']:.4f})")
