"""Reference solution for T5: vector index on a large table."""
import time

import lancedb
import numpy as np
from lancedb.index import IvfPq

rng = np.random.default_rng(42)
vectors = rng.random((100_000, 128), dtype=np.float32)
db = lancedb.connect("data/t5")
table = db.create_table(
    "vectors", data=[{"id": i, "vector": v} for i, v in enumerate(vectors)], mode="overwrite"
)
query = vectors[123]


def timed_search(**settings):
    search = table.search(query).limit(10)
    for name, value in settings.items():
        search = getattr(search, name)(value)
    start = time.perf_counter()
    result = search.select(["id", "_distance"]).to_pandas()
    return result, time.perf_counter() - start


exact, exact_time = timed_search()
table.create_index("vector", config=IvfPq(distance_type="l2"))
print([index.name for index in table.list_indices()])
indexed, indexed_time = timed_search(nprobes=20, refine_factor=10)

print(f"Without index: {exact_time * 1000:.1f} ms, first id {exact.id[0]}")
print(f"With index:    {indexed_time * 1000:.1f} ms, first id {indexed.id[0]}")
print(f"Overlap of the two top-10 lists: {len(set(exact.id) & set(indexed.id))} of 10")
