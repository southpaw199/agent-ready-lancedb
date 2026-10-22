# LanceDB: findings log

Observations about the docs collected during agent runs, before they're written up in the [report](report.md). Each finding needs evidence from a run and a check against the current docs page before it goes in the report.

| ID | Page | Finding | Evidence | Status |
| --- | --- | --- | --- | --- |
| F1 | [Vector search](https://docs.lancedb.com/search/vector-search.md) | The metrics table defines `l2` with a square root, but the `_distance` returned for `l2` searches is the squared distance. The page doesn't say which one `_distance` holds. | T1 (2026-10-22): distances of 0.03 and 0.09 equal the sums of squared differences; the plain Euclidean distances would be 0.173 and 0.300. The agent noticed the mismatch itself. | Confirmed against the page on 2026-10-22 |
| F2 | [Quickstart](https://docs.lancedb.com/quickstart.md) | Creating a new table prints `WARN lance::dataset::write::insert ... No existing dataset ... it will be created`. It looks like a problem but is normal, and the quickstart doesn't mention it. | Notebook development (2026-10-21) and T1 (2026-10-22). The agent explained it unprompted. | To check: search the docs for any mention of this message |
