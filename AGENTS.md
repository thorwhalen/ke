# AGENTS.md — `ke`

`ke` is **reserved for a future knowledge-*extraction* package**: producing
structured knowledge from raw sources (the inverse of evaluating extraction
outputs, which is what [`ek`](https://github.com/thorwhalen/ek) does).

## Current state

This repo previously held a first draft of knowledge-*evaluation* tooling.
That work continued under the name `ek` and has since grown well past what
lived here (more metrics, an agent-evaluation layer, a full test suite). The
superseded contents were removed in
[issue #12](https://github.com/thorwhalen/ke/issues/12); see that issue for
the evidence and the full reasoning.

If you are here to evaluate information-extraction or agent outputs, you
want [`ek`](https://github.com/thorwhalen/ek), not this repo.

## Starting knowledge-extraction work here

Nothing is built yet. Before writing code:

- Read the `architecture-first` skill (seams before surfaces) — this is a
  fresh build, not a continuation.
- `[tool.wads.ci.publish]` is deliberately `enabled = false` in
  `pyproject.toml` (see the comment there) — re-enable only once there is
  code worth shipping, so `pip install ke` does not silently start serving
  an empty or half-built package.
- `ke` is already published on PyPI as an older, unrelated package (a file
  access utility, last released 2025-06-17). A release from this repo would
  supersede it under the same name — deliberate, per issue #12 — but confirm
  that is still the intent before publishing.
