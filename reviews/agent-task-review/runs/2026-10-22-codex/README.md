# Run: 2026-10-22, Codex

A second agent on the same five tasks, so findings can be compared across model families. The tasks, standard instructions, and scoring are identical to the [Claude Code run](../2026-10-22-claude-code/).

## Environment

| Item | Value |
| --- | --- |
| Agent | Codex CLI, in a WSL terminal |
| Agent version | 0.163.0 |
| Model | GPT-6.1-Sol, reasoning "low" (Codex's default setting at the time) |
| Operating system | Ubuntu 24.04 under WSL 2 on Windows 11 |
| Python | 3.12.3 |
| Working folder | A new, empty folder per task under `~/agent-runs/2026-10-22-codex/`, outside this repository |
| User instructions | None (`AGENTS.md` absent) |
| Approvals | `approval_policy = "on-request"`, workspace sandbox: every command needing the network asked for approval |
| Web search | Off (`web_search = "disabled"`), because Codex's search tool doesn't ask before each search |
| ChatGPT connectors | Off (`features.apps = false`) |
| Memories | Off (`features.memories = false`) |

## Notes

- Codex printed a warning that bubblewrap, the Linux sandboxing tool it prefers, wasn't available, and used its built-in sandbox instead. Bubblewrap was kept off the path for all five tasks so the runs are comparable.

## How Codex differs from the Claude Code run

- Codex has no page-reading tool, so it read docs pages with `curl`. The full page contents it downloaded are left out of the transcripts here, which keep the commands and the agent's messages.
- The sandbox blocks network access until a command is approved, so the first attempt at each page fetch or install typically failed, then succeeded once approved.

## Tasks

| Task | Outcome | Hints | Folder |
| --- | --- | --- | --- |
| T1 | pass | 0 | [T1](T1/) |
| T2 | pass | 0 | [T2](T2/) |
| T3 | pass | 0 | [T3](T3/) |

Each task folder holds the agent's final `task.py` and its exported conversation, `transcript.md`. Where the reviewer's own run showed something the agent left out of its summary, the folder also has `output.txt`.
