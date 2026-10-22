"""Automatic local embeddings in LanceDB.

Documentation (discovered through https://docs.lancedb.com/llms.txt):
https://docs.lancedb.com/embedding/quickstart.md
https://docs.lancedb.com/integrations/embedding/sentence-transformers.md
https://docs.lancedb.com/search/vector-search.md

Run: .venv/bin/python task.py
The first run downloads the model; embedding inference runs locally on CPU.
"""

import os
from pathlib import Path

# Keep the database and downloaded model/cache files in this folder.
ROOT = Path(__file__).resolve().parent
os.environ["HF_HOME"] = str(ROOT / ".cache" / "huggingface")
os.environ["XDG_CACHE_HOME"] = str(ROOT / ".cache")

import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector


def main():
    model = get_registry().get("sentence-transformers").create(
        name="all-MiniLM-L6-v2", device="cpu", trust_remote_code=False
    )

    class Sentence(LanceModel):
        text: str = model.SourceField()
        vector: Vector(model.ndims()) = model.VectorField()

    db = lancedb.connect(str(ROOT / "animals.lancedb"))
    # Recreate this example table so rerunning the script keeps exactly five rows.
    table = db.create_table("animals", schema=Sentence, mode="overwrite")
    sentences = [
        "Cats often purr when they are content.",
        "Dogs need regular walks to stay healthy.",
        "Goldfish can live for more than ten years.",
        "Parrots can learn to imitate human speech.",
        "Rabbits are most active at dawn and dusk.",
    ]
    # Supply only text: LanceDB generates and stores the vectors automatically.
    table.add([{"text": text} for text in sentences])

    query = "Which animal makes a soft rumbling sound when happy?"
    # Supply the query text directly: LanceDB also embeds it automatically.
    results = table.search(query).distance_type("cosine").limit(3).to_list()
    print(f"Query: {query}")
    print("Top 3 matches (cosine distance; lower is closer):")
    for rank, row in enumerate(results, start=1):
        print(f"{rank}. {row['text']} | distance={row['_distance']:.6f}")


if __name__ == "__main__":
    main()
