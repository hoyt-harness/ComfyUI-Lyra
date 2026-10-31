# Code Review Notes — ComfyUI-Lyra

## What failure looks like here

The core risk is silent audio corruption: the SNAC decode pipeline produces
garbled or empty output when token grouping or chunk concatenation breaks,
and there is no runtime assertion to catch it — the node returns audio data
regardless.

## Key invariants the reviewer should check

- `__init__.py` inserts its own directory into `sys.path` before importing
  from `lyra_nodes/` or `core/` — this is required for ComfyUI's import
  model and must not be removed
- SNAC decoding in `core/inference.py` consumes exactly 7 tokens per audio
  frame in a fixed hierarchical structure; off-by-one errors produce silence
- `core/chunking.py` splits at sentence boundaries — splits at whitespace
  or character count are bugs
- Audio effect chain in `core/effects.py` must not call SoX or any system
  binary; all processing goes through pedalboard
- No `requirements.txt` runtime package should pull in SoX as a dependency

## Paths to skip

- `.venv/` — virtual environment, not source
- `var/` — health reports
- `hooks/` — dev tooling boilerplate
- `example_workflows/` — JSON workflow examples, not executable code

## Finding standards

- Every finding must cite a specific file and line number
- Cap nits at 3 per review pass; flag the class, not every instance
- Audio correctness bugs outrank style issues regardless of count
