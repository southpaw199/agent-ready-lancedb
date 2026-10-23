# Case study: LanceDB

[LanceDB](https://docs.lancedb.com) is an open-source multimodal lakehouse with vector search. This case study has two parts:

| Folder | What it holds |
| --- | --- |
| [`examples/`](examples/) | A runnable notebook that builds semantic search over the FastAPI documentation, including a search that fails, why, and how to fix it. |
| [`reviews/agent-task-review/`](reviews/agent-task-review/) | An [agent task review](../../methods/agent-task-review/method.md) of LanceDB's docs, run with Claude Code and Codex. |

## Results in brief

Two AI coding agents, Claude Code and Codex, each attempted five LanceDB tasks using only the docs. Both passed all five with no hints. Along the way, both copied deprecated commands from LanceDB's synchronous Python examples, and both hit gaps in install guidance and in how `_distance` is returned.

**[Read the report](reviews/agent-task-review/report.md)** for the findings, suggested fixes, and how the two agents compared.
