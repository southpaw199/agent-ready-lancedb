"""Store PNG bytes and search local OpenCLIP embeddings in LanceDB.

Setup: .venv/bin/pip install lancedb open_clip_torch pillow
Run:   .venv/bin/python task.py

Official documentation used (starting at https://docs.lancedb.com/llms.txt):
https://docs.lancedb.com/integrations/embedding/openclip.md
https://docs.lancedb.com/tables/multimodal.md
https://docs.lancedb.com/search/vector-search.md
"""

import os
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    # Keep downloaded model weights and other caches in this folder.
    os.environ["HF_HOME"] = str(root / ".cache" / "huggingface")
    os.environ["TORCH_HOME"] = str(root / ".cache" / "torch")
    os.environ["XDG_CACHE_HOME"] = str(root / ".cache")
    os.environ["HF_HUB_DISABLE_XET"] = "1"

    import lancedb
    import torch
    from PIL import Image
    from lancedb.embeddings import get_registry
    from lancedb.pydantic import LanceModel, Vector

    torch.set_num_threads(4)
    paths = sorted((root / "images").glob("*.png"))
    if len(paths) != 12:
        raise ValueError(f"Expected 12 PNG images, found {len(paths)}")

    model = get_registry().get("open-clip").create(
        name="ViT-B-32", pretrained="laion2b_s34b_b79k", device="cpu"
    )

    class Shape(LanceModel):
        filename: str
        image_bytes: bytes = model.SourceField()
        vector: Vector(model.ndims()) = model.VectorField()

    rows = [dict(filename=p.name, image_bytes=p.read_bytes()) for p in paths]
    db = lancedb.connect(str(root / "lancedb_data"))
    table = db.create_table("shapes", data=rows, schema=Shape, mode="overwrite")

    # Verify that the stored binary payloads are the original PNG files.
    stored = table.search().select(["filename", "image_bytes"]).limit(12).to_list()
    assert table.count_rows() == 12
    assert {r["filename"]: r["image_bytes"] for r in stored} == {
        r["filename"]: r["image_bytes"] for r in rows
    }
    print("Stored 12 images with original PNG bytes and OpenCLIP embeddings.")
    print("Model: ViT-B-32 / laion2b_s34b_b79k (local CPU)")
    print("Distance: cosine (lower is more similar)")

    def show_results(label, query):
        results = (
            table.search(query)
            .distance_type("cosine")
            .select(["filename", "_distance"])
            .limit(3)
            .to_list()
        )
        print(f"\n{label}")
        for row in results:
            print(f"{row['filename']:<24} {row['_distance']:.6f}")

    with Image.open(root / "query.png") as image:
        show_results("Top 3 for query.png:", image.convert("RGB"))
    show_results('Top 3 for text "a red circle":', "a red circle")


if __name__ == "__main__":
    main()
