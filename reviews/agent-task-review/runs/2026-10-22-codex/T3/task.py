"""Compare automatic vector embeddings, BM25, and RRF hybrid retrieval.

Run: .venv/bin/python task.py
Official documentation used:
https://docs.lancedb.com/llms.txt
https://docs.lancedb.com/embedding/quickstart.md
https://docs.lancedb.com/integrations/embedding/sentence-transformers.md
https://docs.lancedb.com/search/vector-search.md
https://docs.lancedb.com/search/full-text-search.md
https://docs.lancedb.com/search/hybrid-search.md
https://docs.lancedb.com/reranking/rrf.md
"""

import os
from pathlib import Path

# Keep all generated data and model caches beside this script.
ROOT = Path(__file__).resolve().parent
os.environ["HF_HOME"] = str(ROOT / ".cache" / "huggingface")
os.environ["TORCH_HOME"] = str(ROOT / ".cache" / "torch")
os.environ["XDG_CACHE_HOME"] = str(ROOT / ".cache")
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import lancedb
from lancedb.embeddings import get_registry
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


def print_results(label, rows, score_column):
    print(f"\n{label} (top 3; returned {len(rows)})")
    for rank, row in enumerate(rows, 1):
        print(f"{rank}. [passage {row['id']}; {score_column}={row[score_column]:.6f}] {row['text']}")
    if len(rows) < 3:
        print("Fewer than 3 passages matched; no unmatched passages were added.")


def main():
    model = get_registry().get("sentence-transformers").create(
        name="all-MiniLM-L6-v2", device="cpu", normalize=True,
        trust_remote_code=False,
    )

    class Passage(LanceModel):
        id: int
        text: str = model.SourceField()
        vector: Vector(model.ndims()) = model.VectorField()

    db = lancedb.connect(str(ROOT / "lancedb_data"))
    table = db.create_table("help_center", schema=Passage, mode="overwrite")
    # No vectors are supplied: LanceDB generates them through the schema.
    table.add([{"id": i, "text": text} for i, text in enumerate(PASSAGES, 1)])
    table.create_fts_index("text", replace=True)

    print(f"Created help_center: {table.count_rows()} passages")
    print("Local embedding model: all-MiniLM-L6-v2 (CPU)")
    print(f"Question: {QUESTION}")
    vector = table.search(QUESTION, query_type="vector").limit(3).to_list()
    fts = table.search(QUESTION, query_type="fts", fts_columns="text").limit(3).to_list()
    hybrid = (
        table.search(QUESTION, query_type="hybrid", fts_columns="text")
        .rerank(reranker=RRFReranker(K=60))
        .limit(3)
        .to_list()
    )
    print_results("Vector search", vector, "_distance")
    print_results("Full-text search (BM25)", fts, "_score")
    print_results("Hybrid search (RRFReranker, K=60)", hybrid, "_relevance_score")


if __name__ == "__main__":
    main()
