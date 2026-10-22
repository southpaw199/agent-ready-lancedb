"""Build a 100k x 128-d LanceDB table, index it, and compare search latency.

Docs used:
  https://docs.lancedb.com/quickstart.md            (install, connect, create_table, search)
  https://docs.lancedb.com/tables/create.md         (PyArrow table, FixedSizeList vector column)
  https://docs.lancedb.com/indexing/vector-index.md (create_index, IVF_PQ, wait_for_index, index_stats)
  https://docs.lancedb.com/search/vector-search.md  (brute-force search, bypass_vector_index, refine_factor)
  https://docs.lancedb.com/performance.md           (when to index, choosing an index type)
"""

import time

import lancedb
import numpy as np
import pyarrow as pa
from lancedb.index import IvfPq

NUM_ROWS = 100_000
DIM = 128
QUERY_ROW = 123
K = 10
REPEATS = 20
INDEX_NAME = "vector_idx"


def time_search(query, repeats=REPEATS, **opts):
    """Return (median latency in ms, result ids, result distances) for a k-NN search."""

    def run():
        q = table.search(query).limit(K)
        if opts.get("bypass"):
            q = q.bypass_vector_index()
        if opts.get("refine_factor"):
            q = q.refine_factor(opts["refine_factor"])
        return q.to_arrow()

    run()  # warm-up so file opening/caching isn't counted
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = run()
        times.append((time.perf_counter() - start) * 1000)
    return float(np.median(times)), result["id"].to_pylist(), result["_distance"].to_pylist()


# 1. Data: 100,000 random 128-d float32 vectors, seed 42, ids 0..99,999.
rng = np.random.default_rng(42)
vectors = rng.random((NUM_ROWS, DIM), dtype=np.float32)
data = pa.table(
    {
        "id": pa.array(np.arange(NUM_ROWS, dtype=np.int64)),
        "vector": pa.FixedSizeListArray.from_arrays(pa.array(vectors.ravel()), DIM),
    }
)

db = lancedb.connect("lancedb_data")
table = db.create_table("random_vectors", data, mode="overwrite")
print(f"Created table with {table.count_rows():,} rows; schema:\n{table.schema}\n")

query = vectors[QUERY_ROW]

# 2. Search without an index (exhaustive / brute-force scan).
flat_ms, flat_ids, flat_dist = time_search(query)
print(f"Without index (brute force): {flat_ms:.2f} ms (median of {REPEATS})")
print(f"  ids:       {flat_ids}")
print(f"  distances: {[round(d, 3) for d in flat_dist]}\n")

# 3. Build an IVF_PQ index: the docs' general-purpose default, and the more
#    accurate PQ/RQ option for dimensions <= 256. num_partitions and
#    num_sub_vectors are left to LanceDB's defaults (auto partitions from
#    row count; num_sub_vectors = 128 // 16 = 8).
start = time.perf_counter()
table.create_index("vector", config=IvfPq(distance_type="l2"), name=INDEX_NAME)
table.wait_for_index([INDEX_NAME])
print(f"Built IVF_PQ index in {time.perf_counter() - start:.1f} s")
print(f"  {table.index_stats(INDEX_NAME)}\n")

# 4. Search again, now using the index (approximate nearest neighbours).
ann_ms, ann_ids, ann_dist = time_search(query)
print(f"With IVF_PQ index:           {ann_ms:.2f} ms (median of {REPEATS})")
print(f"  ids:       {ann_ids}")
print(f"  distances: {[round(d, 3) for d in ann_dist]}  (approximate, from PQ codes)\n")

# PQ compresses vectors, so the raw ANN ranking loses recall. refine_factor
# fetches K * refine_factor candidates and re-ranks them on the full vectors.
ref_ms, ref_ids, ref_dist = time_search(query, refine_factor=20)
print(f"With index + refine_factor(20): {ref_ms:.2f} ms (median of {REPEATS})")
print(f"  ids:       {ref_ids}")
print(f"  distances: {[round(d, 3) for d in ref_dist]}  (exact, re-ranked)\n")

# Same table, index ignored, as a sanity check on the brute-force timing.
bypass_ms, bypass_ids, _ = time_search(query, bypass=True)
print(f"Index present but bypassed:  {bypass_ms:.2f} ms (median of {REPEATS})")

def recall(ids):
    return len(set(ids) & set(bypass_ids)) / K


print(f"\nSpeed-up from index: {flat_ms / ann_ms:.1f}x (plain), {flat_ms / ref_ms:.1f}x (refined)")
print(f"Recall@{K} vs exact search: plain index {recall(ann_ids):.0%}, "
      f"index + refine_factor(20) {recall(ref_ids):.0%}")
print(f"Row {QUERY_ROW} is its own nearest neighbour: exact={flat_ids[0] == QUERY_ROW}, "
      f"indexed={ann_ids[0] == QUERY_ROW}")