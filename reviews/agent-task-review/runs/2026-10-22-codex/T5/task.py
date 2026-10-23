"""Run with .venv/bin/python task.py (requires lancedb, numpy, pyarrow).

Official documentation used:
https://docs.lancedb.com/llms.txt
https://docs.lancedb.com/quickstart.md
https://docs.lancedb.com/tables/create.md
https://docs.lancedb.com/indexing/vector-index.md
https://docs.lancedb.com/search/vector-search.md
"""

from pathlib import Path
from statistics import median
from time import perf_counter

import lancedb
from lancedb.index import IvfPq
import numpy as np
import pyarrow as pa


def main():
    rows, dimensions, k = 100_000, 128, 10
    rng = np.random.default_rng(42)
    vectors = rng.random((rows, dimensions), dtype=np.float32)
    data = pa.table({
        "id": pa.array(np.arange(rows, dtype=np.int64)),
        "vector": pa.FixedSizeListArray.from_arrays(
            pa.array(vectors.ravel()), dimensions
        ),
    })
    db = lancedb.connect(str(Path(__file__).resolve().parent / "lancedb_data"))
    # Rerunning replaces only this example table.
    table = db.create_table("random_vectors", data=data, mode="overwrite")
    assert table.count_rows() == rows
    query_vector = vectors[123].copy()  # Row 123 has id=123; keep the self-match.

    # IVF_PQ suits low-dimensional vectors. 316 partitions is our sizing choice
    # (approximately sqrt(100,000)); 16 sub-vectors divide 128 evenly.
    table.create_index("vector", config=IvfPq(
        distance_type="l2", num_partitions=316, num_sub_vectors=16,
    ))
    table.wait_for_index(["vector_idx"])
    stats = table.index_stats("vector_idx")
    assert stats.num_unindexed_rows == 0, stats

    def search(indexed):
        query = table.search(query_vector).distance_type("l2").limit(k)
        if indexed:
            # Rerank 100 candidates using full vectors; ANN is still approximate.
            query = query.nprobes(20).refine_factor(10)
        else:
            query = query.bypass_vector_index()
        return query.select(["id", "_distance"]).to_list()

    # Warm both paths, then alternate their order to reduce ordering bias.
    search(False)
    search(True)
    timings = {False: [], True: []}
    results = {}
    for repetition in range(10):
        for indexed in ((False, True) if repetition % 2 == 0 else (True, False)):
            start = perf_counter()
            results[indexed] = search(indexed)  # Materialize inside timed region.
            timings[indexed].append((perf_counter() - start) * 1000)

    print(f"LanceDB {lancedb.__version__}; NumPy {np.__version__}; PyArrow {pa.__version__}")
    print(f"Table: {rows:,} rows x {dimensions} float32 dimensions; seed=42")
    print("Index: IVF_PQ, L2, 316 partitions, 16 sub-vectors; all rows indexed")
    print("Query: row/id 123; k=10; self-match included")
    print("Timing: median of 10 warmed searches, including result materialization")
    for indexed, label in ((False, "Without index (exact)"), (True, "With index (ANN; nprobes=20, refine_factor=10)")):
        print(f"{label}: {median(timings[indexed]):.3f} ms")
        print("  IDs:", [row["id"] for row in results[indexed]])
        print("  Distances:", [round(row["_distance"], 6) for row in results[indexed]])
    truth = {row["id"] for row in results[False]}
    ann = {row["id"] for row in results[True]}
    assert len(results[False]) == len(results[True]) == k
    assert results[False][0]["id"] == 123
    print(f"ANN recall@10 for this query: {len(truth & ann) / k:.0%}")
    print("Index construction is excluded; timings vary by machine and cache state.")


if __name__ == "__main__":
    main()
