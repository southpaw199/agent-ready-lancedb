# Case study: LanceDB

Can AI coding agents complete real LanceDB tasks using only its documentation? Claude Code and Codex each attempted five tasks, from creating a table to building a vector index on 100,000 rows.

**[Download the report (PDF)](https://github.com/southpaw199/agent-ready-lancedb/releases/latest/download/Alan-Sloan_LanceDB-Agent-Task-Review.pdf)** · [Read it online](reviews/agent-task-review/report.md)

## About this review

This case study is part of [agent-ready-docs](https://github.com/southpaw199/agent-ready-docs), a project that tests whether documentation works for AI agents as well as for people.

More and more developers meet a product through an AI coding agent: they ask Claude Code or Codex to set something up, and the agent reads the docs for them. When the docs leave out a prerequisite, show an example that doesn't run, or document an API in only one language, the agent either gets stuck or fills the gap from memory. The developer may never know which happened.

An [agent task review](https://github.com/southpaw199/agent-ready-docs/blob/main/methods/agent-task-review/method.md) tests docs the way agents use them:

1. **Choose real tasks.** Four to six tasks a new developer would attempt, from first install to a production concern.
2. **Limit the agent to the docs.** Each attempt starts in a clean environment, and the agent must cite every page it relies on.
3. **Verify independently.** The reviewer reruns the agent's code and checks the result against written success criteria. An agent saying it succeeded isn't evidence that it did.
4. **Check the sources.** Cited pages must say what the agent claims, and anything it used that isn't in the docs is recorded.
5. **Use two agents.** A gap that two different agents hit is stronger evidence than one.
6. **Report by root cause.** Each finding is traced to a cause, such as a missing prerequisite, an incomplete example, or a page the agent couldn't find, and comes with a specific fix. The report also credits what the docs do well.

Each run is scored pass, pass with issues, pass with hints, or fail, and each finding is rated High, Medium, or Low severity, using a shared [rubric](https://github.com/southpaw199/agent-ready-docs/blob/main/methods/agent-task-review/rubric.md) so results can be compared across case studies.

## This case study

[LanceDB](https://docs.lancedb.com) is an open-source multimodal lakehouse with vector search. This case study has two parts:

| Folder | What it holds |
| --- | --- |
| [`reviews/agent-task-review/`](reviews/agent-task-review/) | An agent task review of LanceDB's docs, run with Claude Code and Codex on October 22, 2026, under [method version 0.1](https://github.com/southpaw199/agent-ready-docs/blob/v0.1/methods/agent-task-review/method.md). |
| [`examples/`](examples/) | A runnable notebook that builds semantic search over the FastAPI documentation, including a search that fails, why, and how to fix it. |

## Results in brief

Two AI coding agents, Claude Code and Codex, each attempted five LanceDB tasks using only the docs. **Both passed all five, with no hints.** Along the way, both copied deprecated commands from LanceDB's synchronous Python examples, and both hit gaps in install guidance and in how `_distance` is returned.

| Task | What the agent had to do | Claude Code | Codex |
| --- | --- | --- | --- |
| T1 | Create a table from a DataFrame; filtered vector search | Pass | Pass |
| T2 | Automatic text embeddings | Pass | Pass |
| T3 | Full-text, vector, and hybrid search with a reranker | Pass | Pass |
| T4 | Store images; search by image and by text | Pass | Pass |
| T5 | Vector index on 100,000 rows; explain the tradeoff | Pass | Pass |

## Findings

No finding is High.

| ID | Finding | Severity |
| --- | --- | --- |
| F5, F7 | Synchronous Python examples use deprecated APIs | Medium |
| F3 | `_distance` behavior isn't explained | Medium |
| F4 | No install guidance for local embedding models | Medium |
| F1 | Returned L2 distances are squared, but the docs show a square root | Medium |
| F2 | A normal first run prints an alarming log line | Low |
| F6 | Stop-word removal can drop the word that matters | Low |
| F8 | Two thresholds for when brute force stops being enough | Low |
| F9 | Remote-code warning is missing where agents start | Low |

**[Read the report](reviews/agent-task-review/report.md)** (or [download it as a PDF](https://github.com/southpaw199/agent-ready-lancedb/releases/latest/download/Alan-Sloan_LanceDB-Agent-Task-Review.pdf)) for each finding's evidence and suggested fix, what the docs do well, how the two agents compared, and the limitations. The [findings log](reviews/agent-task-review/findings.md) has the evidence for each finding, the [run log](reviews/agent-task-review/run-log.csv) has a row per run, and the [tasks](reviews/agent-task-review/tasks.md) file has each task's prompt and success criteria.

## Use of AI tools

AI coding assistants helped draft code and content in this repo. I ran, tested, and verified every example and every finding myself. Agent outputs are evidence to check, not results to trust.

## License

Created by Alan Sloan ([LinkedIn](https://www.linkedin.com/in/alansloan)).

- **Code** (Python files, notebooks, and workflows) is licensed under the [MIT License](LICENSE).
- **Written content** (methods, reports, findings, task definitions, and READMEs) is © 2026 Alan Sloan. All rights reserved: you may read and link to it, but not copy, republish, or adapt it without permission. See [COPYRIGHT.md](COPYRIGHT.md).
- **Agent transcripts** in the `runs/` folders are records of each agent's output, included as evidence.
