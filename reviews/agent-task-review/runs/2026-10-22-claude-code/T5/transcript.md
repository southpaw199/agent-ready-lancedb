
❯ I'm learning LanceDB, an open-source vector database. Use only the official
  LanceDB documentation at https://docs.lancedb.com to do this task. Start from
  https://docs.lancedb.com/llms.txt. Don't rely on what you remember about
  LanceDB, and don't use other websites. Each time you rely on a docs page,
  tell me its URL.

  Work only in the current folder. Create a Python virtual environment here and
  install what you need. When you're done, give me the final code as a single
  Python file named task.py, run it, and show me the output.

  Create a LanceDB table of 100,000 random 128-dimensional vectors, generated
  with NumPy using the seed 42, with an integer id column from 0 to 99,999. Add
  a vector index suited to a table this size. Then search for the 10 nearest
  neighbors of the vector in row 123, and print the time the search took both
  with and without the index. Finally, explain in a few sentences when a
  LanceDB table needs a vector index, and what you give up by using one.

● Fetch(https://docs.lancedb.com/llms.txt)
  ⎿  Received 43.9KB (200 OK)

  Ran 1 shell command (ctrl+o to expand)

● Fetch(https://docs.lancedb.com/quickstart.md)
  ⎿  Received 24.5KB (200 OK)

● Fetch(https://docs.lancedb.com/indexing/vector-index.md)
  ⎿  Received 18.2KB (200 OK)

● Fetch(https://docs.lancedb.com/search/vector-search.md)
  ⎿  Received 28.9KB (200 OK)

● Fetch(https://docs.lancedb.com/indexing/vector-index.md)
  ⎿  Received 18.2KB (200 OK)

● Fetch(https://docs.lancedb.com/performance.md)
  ⎿  Received 15.4KB (200 OK)

● Fetch(https://docs.lancedb.com/tables/create.md)
  ⎿  Received 30KB (200 OK)

  Ran 1 shell command (ctrl+o to expand)

● I've read the docs I need and set up .venv with lancedb 0.40.0. Next I'll
  write task.py.

● Write(task.py)
  ⎿  Wrote 94 lines to task.py
      1 """Build a 100k x 128-d LanceDB table, index it, and compare sear
      2
      3 Docs used:
        nect, create_table, search)
      5   https://docs.lancedb.com/tables/create.md         (PyArrow tabl
      6   https://docs.lancedb.com/indexing/vector-index.md (create_index
        , IVF_PQ, wait_for_index, index_stats)
        search, bypass_vector_index, refine_factor)
      8   https://docs.lancedb.com/performance.md           (when to inde
      9 """
     … +104 lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

● The indexed search only matched 1 of 10 true neighbors, and the index creation
  method triggered a deprecation warning. I'll switch to the recommended newer
  syntax and add a refine_factor to recover accuracy lost from compression.

  Ran 2 shell commands (ctrl+o to expand)

● Update(task.py)
  ⎿  Added 1 line, removed 1 line
      24  
      25  
      26  def time_search(query, repeats=REPEATS, **opts):
      27 -    """Return (median latency in ms, ids of the results) for a 
         -k-NN search."""                                                
      27 +    """Return (median latency in ms, result ids, result distanc
         +es) for a k-NN search."""                                      
      28  
      29      def run():
      30          q = table.search(query).limit(K)

● The index made the search about 10× faster: 6.5 ms with it versus 64 ms
  without. The cost was accuracy. The plain indexed search found only 1 of the
  10 true nearest neighbors, and 3 of 10 after a re-ranking step. That low score
  comes from the random data, not from a broken index.

  The final code is in task.py. It uses a Python virtual environment in .venv/
  with lancedb 0.40.0, and the table is stored in lancedb_data/. After the run
  shown below I made one docstring-only edit and didn't run it again.

  Docs pages I relied on

  - https://docs.lancedb.com/llms.txt: the starting index, used to find the
    pages below.
  - https://docs.lancedb.com/quickstart.md: install, connecting, creating a
    table and searching.
  - https://docs.lancedb.com/tables/create.md: building a table from PyArrow
    data; the vector column must be a fixed-size list.
  - https://docs.lancedb.com/indexing/vector-index.md: index types,
    create_index, wait_for_index, index_stats and bypass_vector_index.
  - https://docs.lancedb.com/search/vector-search.md: brute-force search and
    refine_factor, plus the accuracy trade-off and its limit on scaling.
  - https://docs.lancedb.com/performance.md: when to add an index and which type
    to choose.

  What the script does

  - Data: it uses np.random.default_rng(42) to make 100,000 × 128 float32
    vectors, plus an id column from 0 to 99,999.
  - Index: it builds an IVF_PQ index and leaves the settings at their defaults.
    The performance page calls IVF_PQ the general-purpose default and says it is
    more accurate than RQ for vectors of 256 dimensions or fewer. The docs' own
    example (create_index(metric=..., index_type="IVF_PQ")) printed a
    deprecation warning in this version. I switched to the form the warning
    suggested, create_index("vector", config=IvfPq(...)), which the docs pages I
    read never showed.
  - Timing: each search is run once to warm up, then 20 more times, and the
    script prints the middle (median) time.

  Output

  Created table with 100,000 rows; schema:
  id: int64
  vector: fixed_size_list<item: float>[128]
    child 0, item: float

  Without index (brute force): 63.66 ms (median of 20)
    ids:       [123, 44547, 44218, 3346, 91506, 51484, 42787, 25341, 66262, 995]
    distances: [0.0, 14.056, 14.289, 14.323, 14.395, 14.535, 14.86, 14.861,
  14.953, 14.971]

  Built IVF_PQ index in 6.6 s
    IndexStatistics(num_indexed_rows=100000, num_unindexed_rows=0,
  index_type='IVF_PQ', distance_type='l2', num_indices=1)

  With IVF_PQ index:           6.51 ms (median of 20)
    ids:       [123, 63858, 60710, 96462, 68030, 43910, 19766, 17741, 8436,
  48347]
    distances: [6.459, 10.722, 11.268, 11.321, 11.349, 11.486, 11.566, 11.654,
  11.822, 11.891]  (approximate, from PQ codes)

  With index + refine_factor(20): 8.99 ms (median of 20)
    ids:       [123, 51484, 42787, 19766, 84257, 8309, 14036, 49310, 63858,
  91763]
    distances: [0.0, 14.535, 14.86, 15.131, 15.377, 15.438, 15.52, 15.65, 15.69,
  15.695]  (exact, re-ranked)

  Index present but bypassed:  63.59 ms (median of 20)

  Speed-up from index: 9.8x (plain), 7.1x (refined)
  Recall@10 vs exact search: plain index 10%, index + refine_factor(20) 30%
  Row 123 is its own nearest neighbour: exact=True, indexed=True
  (I left out one line of LanceDB log output saying the dataset was being
  created for the first time.)

  Why recall is so low: this is my own reasoning, not something the docs say. In
  uniform random 128-dimensional data, every vector is almost the same distance
  from every other. The true top 10 lie between 14.06 and 14.97, and the next
  candidates are only slightly farther away. An approximate index can't tell
  such close points apart. Real embeddings form clusters, so on real data an
  index usually does much better. Raising nprobes or refine_factor would also
  recover more accuracy, at some cost in speed.

  When a table needs a vector index, and what you give up

  Without an index, LanceDB compares the query against every row. That gives
  exact results, but search time grows in step with the number of rows. The
  performance page says this "works fine below ~100K vectors, but past that you
  should build a dedicated vector index". The vector-search page adds that it
  "is not scalable for datasets larger than a few hundred thousand vectors."

  This table, at exactly 100K rows, sits right at that line, and the index still
  made search about 10× faster. An index such as IVF_PQ gets its speed by
  searching only part of the data and comparing compressed copies of the
  vectors. That means:
  - Accuracy: results are approximate, so you lose some true neighbors (10%
    recall here before tuning). Distances come from the compressed vectors
    unless you re-rank with refine_factor, which adds time.
  - Build and upkeep: the index takes time to build (6.6 s here). Rows added or
    updated later are not indexed until you run optimize() or rebuild, and
    searching them falls back to a slower path.
  - Fixed distance metric: the metric is set when the index is built. A query
    using a different metric falls back to a brute-force scan.