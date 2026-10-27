# Case study: LanceDB

Part of [agent-ready-docs](https://github.com/southpaw199/agent-ready-docs), which tests whether documentation works for AI agents as well as for people.

[LanceDB](https://docs.lancedb.com) is an open-source multimodal lakehouse with vector search. This case study has two parts:

| Folder | What it holds |
| --- | --- |
| [`examples/`](examples/) | A runnable notebook that builds semantic search over the FastAPI documentation, including a search that fails, why, and how to fix it. |
| [`reviews/agent-task-review/`](reviews/agent-task-review/) | An [agent task review](https://github.com/southpaw199/agent-ready-docs/blob/v0.1/methods/agent-task-review/method.md) of LanceDB's docs, run with Claude Code and Codex. |

## Results in brief

Two AI coding agents, Claude Code and Codex, each attempted five LanceDB tasks using only the docs. Both passed all five with no hints. Along the way, both copied deprecated commands from LanceDB's synchronous Python examples, and both hit gaps in install guidance and in how `_distance` is returned.

**[Read the report](reviews/agent-task-review/report.md)** for the findings, suggested fixes, and how the two agents compared.

## Use of AI tools

AI coding assistants helped draft code and content in this repo. I ran, tested, and verified every example and every finding myself. Agent outputs are evidence to check, not results to trust.

## License

Created by Alan Sloan ([LinkedIn](https://www.linkedin.com/in/alansloan)).

- **Code** (Python files, notebooks, and workflows) is licensed under the [MIT License](LICENSE).
- **Written content** (methods, reports, findings, task definitions, and READMEs) is © 2026 Alan Sloan. All rights reserved: you may read and link to it, but not copy, republish, or adapt it without permission. See [COPYRIGHT.md](COPYRIGHT.md).
- **Agent transcripts** in the `runs/` folders are records of each agent's output, included as evidence.
