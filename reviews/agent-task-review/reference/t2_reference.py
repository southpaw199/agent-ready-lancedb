"""Reference solution for T2: automatic text embeddings."""
import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

embedder = get_registry().get("sentence-transformers").create(name="all-MiniLM-L6-v2", device="cpu")


class Sentence(LanceModel):
    text: str = embedder.SourceField()
    vector: Vector(embedder.ndims()) = embedder.VectorField()


sentences = [
    "Cats often purr when they are content.",
    "Dogs need regular walks to stay healthy.",
    "Goldfish can live for more than ten years.",
    "Parrots can learn to imitate human speech.",
    "Rabbits are most active at dawn and dusk.",
]
db = lancedb.connect("data/t2")
table = db.create_table("sentences", schema=Sentence, mode="overwrite")
table.add([{"text": s} for s in sentences])
print(table.search("Which animal makes a soft rumbling sound when happy?").limit(3)
      .select(["text", "_distance"]).to_pandas())
