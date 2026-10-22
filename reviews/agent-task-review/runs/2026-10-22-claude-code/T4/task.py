"""Store shape images in LanceDB with OpenCLIP embeddings, then search by image and by text.

Docs used:
  https://docs.lancedb.com/quickstart.md                     (connect / create_table)
  https://docs.lancedb.com/integrations/embedding/openclip.md (open-clip embedding function, image + text search)
  https://docs.lancedb.com/tables/multimodal.md               (storing raw image bytes in a binary column)
  https://docs.lancedb.com/search/vector-search.md            (limit, distance_type, _distance column)
"""

import io
from pathlib import Path

import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from PIL import Image

HERE = Path(__file__).resolve().parent
IMAGES_DIR = HERE / "images"
QUERY_IMAGE = HERE / "query.png"

db = lancedb.connect(str(HERE / "lancedb_data"))

# Local multimodal model (default: ViT-B-32, laion2b_s34b_b79k, on CPU).
func = get_registry().get("open-clip").create()


class Shapes(LanceModel):
    filename: str
    image_bytes: bytes = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()


rows = [
    {"filename": p.name, "image_bytes": p.read_bytes()}
    for p in sorted(IMAGES_DIR.glob("*.png"))
]

table = db.create_table("shapes", schema=Shapes, mode="overwrite")
table.add(rows)  # embeddings are computed automatically from image_bytes
print(f"Stored {table.count_rows()} images in table 'shapes'")


def show(title, results):
    print(f"\n{title}")
    for r in results:
        print(f"  {r['filename']:<22} distance={r['_distance']:.4f}")


# CLIP embeddings are compared by angle, so use cosine distance.
query_image = Image.open(io.BytesIO(QUERY_IMAGE.read_bytes()))
image_results = (
    table.search(query_image)
    .distance_type("cosine")
    .select(["filename"])
    .limit(3)
    .to_list()
)
show("Top 3 images most similar to query.png:", image_results)

text_results = (
    table.search("a red circle")
    .distance_type("cosine")
    .select(["filename"])
    .limit(3)
    .to_list()
)
show('Top 3 images matching the text "a red circle":', text_results)

# The image data is stored in the table itself: read one back and decode it.
stored = table.search().where("filename = 'red_circle.png'").limit(1).to_list()[0]
img = Image.open(io.BytesIO(stored["image_bytes"]))
print(f"\nRead back red_circle.png from the table: {len(stored['image_bytes'])} bytes, {img.size[0]}x{img.size[1]} {img.mode}")
