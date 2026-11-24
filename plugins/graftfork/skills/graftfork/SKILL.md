---
name: graftfork
description: Keep internal open-source fork patches alive across upstream releases using GraftFork (graftfork.com). Use when inspecting fork divergence, checking test-gated carry readiness, explaining GraftFork's 0-wrong-moves rule, or opening the GraftFork Inspector side pane.
---

# GraftFork Skill

Use the bundled `graftfork_inspector` MCP server tools whenever working with upstream forks or `graft`:

- **`open_graftfork_inspector(repo_path)`**: Opens the interactive **GraftFork Inspector** side pane (`aux_pane` / `global`) showing local fork divergence, recent commits to carry, GraftFork benchmark posture (`0 wrong moves`), and quick links to `graftfork.com` and `claude.ai/directory/graftfork`.
- **`graft_inspect_local_repo(repo_path)`**: Inspects any local git repository (branch, latest tag, commits ahead of tag, modified files) to estimate carry surface before running `graft sync`.
- **`graft_benchmark_status()`**: Returns GraftFork's public test-gate guarantee and CLI/MCP quick commands (`graft sync`, `graft why`, `graft pull`, `graft verify-record`).

## Core Carry Rules
1. Clean commits carry deterministically; commits already absorbed upstream are dropped cleanly.
2. Only conflicting hunks go to a sandboxed agent, paired with the original commit rationale.
3. **Hard test gate:** Never move or merge a fork branch when upstream baseline or moved-tree tests fail; surface `graft why` instead.
