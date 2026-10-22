# Run: 2026-10-22, Claude Code

## Environment

| Item | Value |
| --- | --- |
| Agent | Claude Code, VS Code extension |
| Agent version | 2.1.306 |
| Model | claude-opus-5-5 |
| Operating system | Ubuntu 24.04 under WSL 2 on Windows 11 |
| Python | 3.12.3 |
| Working folder | A new, empty folder per task under `~/agent-runs/2026-10-22-claude-code/`, outside this repository |
| User instructions | None (`~/.claude/CLAUDE.md` absent) |
| Auto memory | Off (`autoMemoryEnabled: false`) |
| claude.ai connectors | Off (`disableClaudeAiConnectors: true`) |
| Other MCP servers | One configured (Illustrator), failed to connect |
| Account skills | Synced file-format, browser, research, and job-search skills; none related to LanceDB or vector search. None were used. |
| Caches | pip and Hugging Face caches already held packages and models from the reference run, so downloads were faster than for a new user |

## Tasks

| Task | Outcome | Hints | Folder |
| --- | --- | --- | --- |
| T1 | pass | 0 | [T1](T1/) |
| T2 | pass | 0 | [T2](T2/) |
| T3 | pass | 0 | [T3](T3/) |
| T4 | pass | 0 | [T4](T4/) |

Each task folder holds the agent's final `task.py` and the exported conversation, `transcript.md`. Where the reviewer's own run showed something the agent left out of its summary, the folder also has `output.txt`.
