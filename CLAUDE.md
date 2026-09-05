# CLAUDE.md — ComfyUI-Lyra

ComfyUI-Lyra is a ComfyUI custom node providing Orpheus TTS 3B text-to-speech
capabilities. Hard fork of ComfyUI-Orpheus-TTS (ShmuelRonen, MIT) — relicensed
GPLv3. Positronikal ownership (hoyt-harness). Core differences from upstream:
SoX dependency eliminated (pure Python via pedalboard), uv-based dev
environment, Positronikal model store path conventions, Positronikal repo
hardening.

Language: Python. ComfyUI custom node — loaded in-place from ComfyUI's
custom_nodes directory. Dev environment via uv (.venv/).

## Install (development)

```sh
uv sync --group dev          # lint/type/test only — no torch
uv sync --extra runtime      # full runtime stack (torch, transformers, snac…)
```

ComfyUI runtime installs from requirements.txt via its own environment.

**sys.path note**: ComfyUI loads __init__.py via importlib without adding the
node's directory to sys.path. __init__.py inserts its own directory at runtime
so that lyra_nodes/ and core/ are importable. This is correct and expected.

## Test

```sh
bash hooks/ci-check.sh
```

## Key files

- `__init__.py` — ComfyUI node registration; inserts node dir into sys.path
- `lyra_nodes/loader.py` — OrpheusTTSModelLoader node
- `lyra_nodes/generate.py` — OrpheusTTSGenerate node (tag placement logic)
- `lyra_nodes/effects.py` — LyraAudioEffects node
- `core/model.py` — ModelReference dataclass + load_model()
- `core/inference.py` — generate_speech_chunk(), SNAC decoding pipeline
- `core/chunking.py` — chunk_text(), concatenate_audio()
- `core/effects.py` — apply_effects() via pedalboard (no SoX)
- `hf_auth.py` — optional HuggingFace token helper (runs at import time)
- `requirements.txt` — ComfyUI Manager compatibility shim (generated from
  pyproject.toml runtime extras via `uv export --extra runtime --no-hashes
  --no-emit-project`)

## Nodes

**OrpheusTTSModelLoader** — loads Orpheus 3B model and SNAC codec.
Defaults to `D:\models\comfyui-models\checkpoints\orpheus-3b`. Outputs
MODEL_REF passed to Generate.

**OrpheusTTSGenerate** — synthesizes speech from text. Inputs: model,
text, voice (tara/leah/jess/leo/dan/mia/zac/zoe), paralinguistic element
and placement mode (none/append/prepend/pipe), generation parameters.
All 8 paralinguistic tags: `<laugh>`, `<chuckle>`, `<sigh>`, `<cough>`,
`<sniffle>`, `<groan>`, `<yawn>`, `<gasp>`.

**LyraAudioEffects** — post-processes AUDIO output. Pitch shift and speed
via pedalboard.time_stretch (pitch-corrected), reverb via pedalboard.Reverb,
echo via pedalboard.Delay, gain via pedalboard.Gain, normalize via numpy
peak normalization. No system binary required.

## Model

Default: `canopylabs/orpheus-3b-0.1-ft` (English). Multilingual variants
available: `canopylabs/3b-de-ft-research_release` (German),
`canopylabs/3b-fr-ft-research_release` (French), and others — specify via
the `orpheus_model_path` input. SNAC auto-downloads from HuggingFace on
first run if not already cached.

## Dependency split

| Group | Contents | When to install |
|---|---|---|
| base | numpy, pedalboard | always (dev and runtime) |
| runtime extra | torch, transformers, snac, librosa, etc. | ComfyUI environment |
| dev group | ruff, pyright, pytest, safety, bandit | development only |

Standards: https://github.com/Positronikal/PositronikalCodingStandards/tree/main/standards/
