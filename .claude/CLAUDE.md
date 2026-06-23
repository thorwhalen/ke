# CLAUDE.md

The project guide for agents lives in **[AGENTS.md](../AGENTS.md)** (the SSOT,
read by every agent host). Read it first.

@AGENTS.md

## Claude Code specifics

- Dev skills are in `skills/` and surfaced here via per-skill relative symlinks
  (`.claude/skills/<name> -> ../../skills/<name>`). Invoke them as
  `/ke-dev-architecture`, `/ke-dev-licensing`, `/ke-dev-add-metric`,
  `/ke-dev-add-signal`, `/ke-dev-ocr`. Start with `ke-dev-architecture`.
- Per-session handoff notes go in the gitignored `.claude/handoffs/`.
