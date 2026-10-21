"""Reference solution for T4: store images and search by image and by text.

Needs extra packages: pip install open-clip-torch pillow
Run from a folder prepared with make_sample_images.py.
"""
from pathlib import Path

import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from PIL import Image

clip = get_registry().get("open-clip").create()


class ImageRow(LanceModel):
    file_name: str
    image_bytes: bytes = clip.SourceField()
    vector: Vector(clip.ndims()) = clip.VectorField()


paths = sorted(Path("images").glob("*.png"))
db = lancedb.connect("data/t4")
table = db.create_table("images", schema=ImageRow, mode="overwrite")
table.add([{"file_name": p.name, "image_bytes": p.read_bytes()} for p in paths])

print("Image search:")
print(table.search(Image.open("query.png")).limit(3).select(["file_name", "_distance"]).to_pandas())
print("\nText search:")
print(table.search("a red circle").limit(3).select(["file_name", "_distance"]).to_pandas())
