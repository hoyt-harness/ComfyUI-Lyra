# Research: Core Node Rewrite

**Phase 0 output for `001-core-node-rewrite`**

All decisions resolved from pre-spec investigation and prior session work.

---

## Decision: Audio Effects Library

**Decision**: pedalboard (Spotify, Apache 2.0)

**Rationale**: pedalboard replaces SoX comprehensively with a pure-Python
interface to C++ DSP (no system binary). It provides pitch shift, time stretch
(speed), reverb, compression/limiting, delay/echo, and normalization — matching
SoX's full capabilities with identical parameters to what the upstream node
exposed. Cross-platform, actively maintained, single `pip install`.

**Alternatives considered**:
- librosa: has pitch shift and time stretch but no reverb or echo. Would require
  combining with scipy for delay effects. librosa stays as the I/O and
  resampling layer regardless.
- pyroomacoustics: full acoustic room simulation; far heavier than needed and
  overkill for a simple reverb effect on speech.
- Raw numpy: viable for echo (delay + decay is a one-liner), acceptable for
  volume; not viable for pitch shift or reverb without significant DSP work.
- soundfile: file I/O only; no processing capabilities.

**pedalboard dependency note**: Apache 2.0 license is GPL-compatible. Including
it in our GPLv3 project requires no special handling.

---

## Decision: Inference Backend

**Decision**: transformers + snac (no vllm)

**Rationale**: vllm is the official Canopy AI `orpheus-speech` package's backend
but is Linux-only and incompatible with Windows and ComfyUI environments. The
upstream ShmuelRonen fork proves the model runs cleanly under transformers +
snac on Windows. This decision is locked by Constitution Principle II.

**Alternatives considered**:
- `orpheus-speech` official package: requires vllm; blocked.
- llama.cpp / GGUF quantized Orpheus: would eliminate the transformers
  dependency but requires a different model format and complicates the
  model store convention. Deferred — evaluate if torch proves too heavy for
  users' existing ComfyUI environments.

---

## Decision: Dependency Split (Runtime vs Dev)

**Decision**: Optional extras for the runtime inference stack; dev tools in
dependency-groups.

**Rationale**: CI runners on standard hardware cannot install torch without
timing out or needing GPU drivers. Moving the inference stack to
`[project.optional-dependencies] runtime = [...]` lets CI install only
dev tools via `uv sync --group dev` and run lint/type checks cleanly.
ComfyUI's own environment provides torch and the inference stack at runtime;
the `requirements.txt` shim continues to list the full runtime deps for
ComfyUI Manager compatibility.

**Structure**:
```toml
[project]
dependencies = ["pedalboard", "soundfile", "numpy"]   # always-needed

[project.optional-dependencies]
runtime = ["torch", "transformers", "snac", "librosa",
           "huggingface_hub", "nltk>=3.8.0"]          # inference stack

[dependency-groups]
dev = ["ruff", "pyright", "safety", "bandit",
       "pip-licenses", "pytest"]                       # dev tooling
```

CI installs: `uv sync --group dev` (no torch).
Full local dev: `uv sync --group dev --extra runtime`.

---

## Decision: Source Layout

**Decision**: Flat root with `nodes/` and `core/` subdirectories.

**Rationale**: ComfyUI loads custom nodes from the root `__init__.py`. The
upstream flat layout (all code in `tts_nodes.py` and `orpheus_audio_effects.py`)
mixes node registration, model management, and inference into two large files.
Splitting into `nodes/` (ComfyUI interface) and `core/` (inference pipeline)
separates concerns without violating ComfyUI's loading requirements.

**No `src/` layout**: ComfyUI's loader expects `__init__.py` at the root.
A `src/` layout would break ComfyUI integration.

---

## Decision: Voice Consistency

**Decision**: Named voice presets only; no audio reference cloning.

**Rationale**: Orpheus 3B conditions voice on a named token prepended to the
prompt (e.g., `"tara: Hello..."`). The model has no audio-conditioning
mechanism — it cannot accept a reference audio clip. Voice consistency for
Joule and Rōnin is achieved by always using the same voice name for each
character and documenting which preset best matches each character's
description. True voice cloning requires a different model.
