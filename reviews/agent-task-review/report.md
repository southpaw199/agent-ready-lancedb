# LanceDB: agent task review report

**Author:** Alan Sloan · [linkedin.com/in/alansloan](https://www.linkedin.com/in/alansloan) · [github.com/southpaw199](https://github.com/southpaw199)

- **Method:** [agent task review](https://github.com/southpaw199/agent-ready-docs/blob/v0.1/methods/agent-task-review/method.md), version 0.1
- **Agents:** Claude Code 2.1.306 (claude-opus-5-5) and Codex CLI 0.163.0 (GPT-6.1-Sol, reasoning "low")
- **Runs:** October 22, 2026, against the live docs at [docs.lancedb.com](https://docs.lancedb.com), with LanceDB 0.40.0
- **Findings checked against the live docs:** October 22 and 23, 2026

## Summary

Two AI coding agents from different companies each attempted the same five LanceDB tasks, using only LanceDB's documentation. **Both passed all five, with no hints.** LanceDB's docs are in good shape for agents: every task was achievable from the docs alone.

The problems showed up in *how* the agents got there. **Both agents copied deprecated commands straight from LanceDB's Python examples**, on two separate pages. One agent shipped the deprecated code anyway, reporting that it "ran successfully". Two more gaps also tripped up both agents: what to install for local embedding models, and an undocumented change in how the `_distance` column is returned.

| Task | What the agent had to do | Claude Code | Codex |
| --- | --- | --- | --- |
| T1 | Create a table from a DataFrame; filtered vector search | Pass | Pass |
| T2 | Automatic text embeddings | Pass | Pass |
| T3 | Full-text, vector, and hybrid search with a reranker | Pass | Pass |
| T4 | Store images; search by image and by text | Pass | Pass |
| T5 | Vector index on 100,000 rows; explain the tradeoff | Pass | Pass |

Every result was confirmed by running the agent's final code separately, not by trusting the agent's summary. That mattered: in six of the ten runs, the agent's summary left out or misdescribed warnings that the code printed.

## What the docs do well

- **Built for agents from the start.** An [`llms.txt`](https://docs.lancedb.com/llms.txt) index lists about 240 pages, and most pages have a Markdown version. Both agents used `llms.txt` as their map and found the right pages for every task.
- **Tested code snippets.** Snippets are generated from tested code, so nothing either agent copied failed to run. The problems were deprecations, not broken examples.
- **The embedding registry is explained clearly.** Neither agent fell back on computing embeddings by hand in T2, T3, or T4. Both used the schema's `SourceField` and `VectorField` exactly as documented.
- **Reranking concepts land.** Both agents correctly explained why the RRF reranker ranked a weaker passage first in T3, using the [RRF page](https://docs.lancedb.com/reranking/rrf.md).
- **LanceDB already audits its own docs.** The [docs repository](https://github.com/lancedb/docs) includes a weekly LLM-driven audit that compares the docs with the code to find gaps. This review is complementary: it tests the docs from the outside, by watching agents use them.

## Main findings

### 1. Synchronous Python examples use deprecated APIs (F5, F7)

**Seen with both agents. The strongest finding in the review.**

Two pages show the deprecated form as the standard synchronous Python example, with no deprecation note. The current form appears only in the async examples.

| Page | Documented sync form | What LanceDB 0.40.0 prints |
| --- | --- | --- |
| [Full-text search](https://docs.lancedb.com/search/full-text-search.md) and [FTS index](https://docs.lancedb.com/indexing/fts-index.md) | `table.create_fts_index("text")` | "create_fts_index is deprecated as of 0.25.0. Use create_index() with config=FTS() instead." |
| [Vector index](https://docs.lancedb.com/indexing/vector-index.md) | `table.create_index(metric=..., index_type="IVF_PQ", ...)` | "The create_index() API with metric/num_partitions parameters is deprecated and will be removed in a future version." |

**What happened:** both agents copied both forms. Claude Code read the warnings and switched to the current form each time. Codex switched for the vector index but kept `create_fts_index` in its final T3 code, even though the warning printed in its own run.

**Suggested fix:** show `table.create_index("text", config=FTS())` and `table.create_index("vector", config=IvfPq(...))` as the synchronous Python examples, matching what the async examples already show. Until then, add a deprecation note beside the old forms.

### 2. `_distance` behavior isn't explained (F3)

**Seen with both agents.**

Every vector search example in the [quickstart](https://docs.lancedb.com/quickstart.md) lists `_distance` in `.select()`, but nothing says why. An agent that selected only the columns it wanted, then read `_distance`, got a deprecation warning: today LanceDB adds `_distance` automatically, but a future release will stop, and that code will break.

**What happened:** this occurred in four runs. Claude Code never fixed it (T2, T4). Codex fixed it both times by adding `_distance` to `.select()` (T4, T5).

**Suggested fix:** add one sentence beside the first `.select()` example: include `_distance` (or `_score`, `_relevance_score`) explicitly if you need it, because it won't be added automatically in future releases.

### 3. No install guidance for local embedding models (F4)

**Seen with both agents.**

The [embedding quickstart](https://docs.lancedb.com/embedding/quickstart.md) and the [OpenCLIP page](https://docs.lancedb.com/integrations/embedding/openclip.md) use local models but give no install command for the model's package (`sentence-transformers`, `open-clip-torch`), and don't mention PyTorch. A default `pip install` pulls the full GPU build of PyTorch, several gigabytes.

**What happened:** in T2, both agents ran a plain `pip install`, which pulls the GPU build; Codex's install alone took over 6 minutes. In T4, both agents installed the CPU-only build (Codex also did in T3), but from their own knowledge, and Claude Code flagged its package choices as "not from the docs".

**Suggested fix:** add an install line to each local-model page (for example, `pip install lancedb sentence-transformers`) and a short note on installing the CPU-only PyTorch build when there's no GPU.

### 4. Returned L2 distances are squared, but the docs show a square root (F1)

**Seen with one agent.**

The [vector search](https://docs.lancedb.com/search/vector-search.md) metrics table defines `l2` with a square root. The `_distance` LanceDB returns for `l2` is the squared distance: in T1, 0.03 rather than 0.173. The page doesn't say which.

**What happened:** Claude Code noticed the mismatch on its own and explained it. Codex didn't notice. Rankings are unaffected, but anyone comparing distances to a threshold would get the wrong answer.

**Suggested fix:** state that `_distance` for `l2` is the squared Euclidean distance.

## Minor findings

- **F2. A normal first run prints an alarming log line.** Creating a table prints `WARN lance::dataset::write::insert ... No existing dataset ... it will be created`. It's expected, but nothing in the quickstart, [Troubleshooting](https://docs.lancedb.com/troubleshooting.md), or the [OSS FAQ](https://docs.lancedb.com/faq/faq-oss.md) says so. Claude Code explained it; Codex left it out of every summary. *Fix:* one line in the quickstart, or a Troubleshooting entry.
- **F6. Stop-word removal can drop the word that matters.** The full-text search pages document `remove_stop_words` (on by default) but not its effect on queries. In a companion notebook, it removed "after" from "How can I run code after returning a response?", so the right page wasn't found until stop words were kept. *Fix:* a short example of when to turn it off.
- **F8. Two thresholds for when brute force stops being enough.** [Performance](https://docs.lancedb.com/performance.md) says brute-force search "works fine below ~100K vectors"; [vector search](https://docs.lancedb.com/search/vector-search.md) says it's "not scalable for datasets larger than a few hundred thousand vectors". *Fix:* use one figure in both places.
- **F9. Remote-code warning is missing where agents start.** The `sentence-transformers` provider defaults `trust_remote_code` to `True`. Its [integration page](https://docs.lancedb.com/integrations/embedding/sentence-transformers.md) warns about this, but the [embedding quickstart](https://docs.lancedb.com/embedding/quickstart.md), which uses that provider, doesn't. The [Hugging Face page](https://docs.lancedb.com/integrations/embedding/huggingface.md) says to enable the setting only for trusted repositories, and that provider defaults it to off. Codex turned it off deliberately. *Fix:* carry the warning into the quickstart, or align the defaults.

The full evidence for each finding, with run references, is in the [findings log](findings.md).

## How the two agents differed

| | Claude Code | Codex |
| --- | --- | --- |
| Tasks passed, hints needed | 5 of 5, none | 5 of 5, none |
| Errors recovered from | 2 | 10 |
| Fixed the deprecated index commands it copied (F5, F7) | 2 of 2 | 1 of 2 |
| Fixed the `_distance` warning (F3) | 0 of 2 | 2 of 2 |
| Noticed squared distances (F1) | Yes | No |
| Explained the first-run `WARN` line (F2) | Yes | No |
| Typical time per task | 2 to 10 minutes | 4 to 20 minutes |

Most of Codex's errors and extra time came from its sandbox, not the docs: network access was blocked until approved, and LanceDB scripts stalled when run inside the sandbox. Claude Code explained more and caught more; Codex was more cautious with security settings (F9) and with the `_distance` fix (F3).

## Limitations

- **Prior knowledge.** Both models may know LanceDB from training data, so each run tests the docs plus that knowledge. Requiring page citations reduces the effect but doesn't remove it.
- **One run per task per agent.** Agents and approximate indexes are non-deterministic; Codex's T5 recall varied from 20% to 40% between rebuilds of the same index. Treat each result as a signal, not a verdict.
- **Settings.** Codex ran at its default "low" reasoning setting, and with web search turned off because its search tool doesn't ask before each search. Different settings could change its results.
- **Caches.** Some packages and models were already cached from earlier runs, so some setups were faster than they'd be for a new user.
- **AI assistance.** Claude helped design this review and draft this report. Every finding was checked against the live docs and against the code's actual output by the reviewer.

## Files

- [Tasks, success criteria, and reference results](tasks.md)
- [Run log](run-log.csv): one row per attempt
- [Findings log](findings.md): evidence and status for each finding
- Runs: [Claude Code](runs/2026-10-22-claude-code/) and [Codex](runs/2026-10-22-codex/), with each task's code, transcript, and the reviewer's own output where it differed from the agent's summary

---

© 2026 Alan Sloan. All rights reserved. You may read and link to this report; you may not copy, republish, or adapt it without permission. See [COPYRIGHT.md](../../COPYRIGHT.md).
