"""Reference solution for T3: full-text and hybrid search with a reranker."""
import lancedb
from lancedb.embeddings import get_registry
from lancedb.index import FTS
from lancedb.pydantic import LanceModel, Vector
from lancedb.rerankers import RRFReranker

embedder = get_registry().get("sentence-transformers").create(name="all-MiniLM-L6-v2", device="cpu")


class Passage(LanceModel):
    id: int
    text: str = embedder.SourceField()
    vector: Vector(embedder.ndims()) = embedder.VectorField()


passages = [
    "Press Ctrl+Z to undo the last change you made. Press Ctrl+Y to redo it.",
    "To change the color theme, open Settings and choose Appearance.",
    "Track changes records every edit so reviewers can accept or reject them.",
    "Your work is saved automatically every two minutes.",
    "To restore an earlier copy of a file, open File, then Version History.",
    "Use Ctrl+F to find text and Ctrl+H to replace it.",
    "You can change the default font size in Settings under Editor.",
    "Comments let you discuss a passage without changing the text.",
]
db = lancedb.connect("data/t3")
table = db.create_table("passages", schema=Passage, mode="overwrite")
table.add([{"id": i + 1, "text": t} for i, t in enumerate(passages)])
table.create_index("text", config=FTS(), replace=True)

question = "How do I reverse my most recent edit?"
for label, query in [
    ("vector", table.search(question)),
    ("full-text", table.search(question, query_type="fts")),
    ("hybrid", table.search(question, query_type="hybrid").rerank(RRFReranker())),
]:
    print(f"\n{label}:")
    print(query.limit(3).to_pandas()[["id", "text"]].to_string(index=False))
