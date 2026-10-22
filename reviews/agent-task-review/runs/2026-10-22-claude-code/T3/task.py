"""LanceDB demo: vector, full-text, and hybrid search over help-center passages."""

import lancedb
from lancedb.embeddings import get_registry
from lancedb.index import FTS
from lancedb.pydantic import LanceModel, Vector
from lancedb.rerankers import RRFReranker

PASSAGES = [
    "Press Ctrl+Z to undo the last change you made. Press Ctrl+Y to redo it.",
    "To change the color theme, open Settings and choose Appearance.",
    "Track changes records every edit so reviewers can accept or reject them.",
    "Your work is saved automatically every two minutes.",
    "To restore an earlier copy of a file, open File, then Version History.",
    "Use Ctrl+F to find text and Ctrl+H to replace it.",
    "You can change the default font size in Settings under Editor.",
    "Comments let you discuss a passage without changing the text.",
]
QUESTION = "How do I reverse my most recent edit?"
TOP_K = 3

# Local sentence-transformers model; LanceDB embeds the source field automatically.
embedder = get_registry().get("sentence-transformers").create(
    name="all-MiniLM-L6-v2", device="cpu"
)


class Passage(LanceModel):
    id: int
    text: str = embedder.SourceField()
    vector: Vector(embedder.ndims()) = embedder.VectorField()


db = lancedb.connect("./lancedb_data")
table = db.create_table("help_center", schema=Passage, mode="overwrite")
table.add([{"id": i, "text": t} for i, t in enumerate(PASSAGES, start=1)])

# Full-text search index on the passage text.
table.create_index("text", config=FTS(), replace=True)
table.wait_for_index(["text_idx"])


def show(title, rows, score_col):
    print(f"\n=== {title} ===")
    for rank, row in enumerate(rows, start=1):
        print(f"{rank}. [#{row['id']}] {score_col}={row[score_col]:.4f}  {row['text']}")


print(f"Question: {QUESTION}")

# 1. Vector search: the query string is embedded with the same model.
vector_rows = table.search(QUESTION).limit(TOP_K).to_list()
show("Vector search (lower _distance = closer)", vector_rows, "_distance")

# 2. Full-text (BM25) search over the indexed text column.
fts_rows = table.search(QUESTION, query_type="fts").limit(TOP_K).to_list()
show("Full-text search (higher _score = better)", fts_rows, "_score")

# 3. Hybrid search, fused with an explicitly chosen Reciprocal Rank Fusion reranker.
reranker = RRFReranker(K=60)
hybrid_rows = (
    table.search(QUESTION, query_type="hybrid")
    .rerank(reranker=reranker)
    .limit(TOP_K)
    .to_list()
)
show("Hybrid search with RRFReranker(K=60)", hybrid_rows, "_relevance_score")
