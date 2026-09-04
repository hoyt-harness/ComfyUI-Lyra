# CLAUDE.md — ComfyUI-Lyra

ComfyUI-Lyra is a ComfyUI custom node providing Orpheus TTS 3B text-to-speech
capabilities. Hard fork of ComfyUI-Orpheus-TTS (ShmuelRonen, MIT) — relicensed
GPLv3. Positronikal ownership (hoyt-harness). Core differences from upstream:
SoX dependency eliminated (pure Python audio stack), uv-based dev environment,
Positronikal model store path conventions, Positronikal repo hardening.

Language: Python. ComfyUI custom node — loads in-place from ComfyUI's
custom_nodes directory. Dev environment via uv (.venv/).

## Install (development)

```sh
uv sync
```

ComfyUI runtime uses requirements.txt via its own environment.

## Test

```sh
bash hooks/ci-check.sh
```

## Key files

- `tts_nodes.py` — Orpheus TTS Model Loader and Generate nodes
- `orpheus_audio_effects.py` — Audio effects node (pitch, speed, reverb, echo)
- `hf_auth.py` — Hugging Face token helper
- `__init__.py` — ComfyUI node registration
- `requirements.txt` — ComfyUI Manager compatibility shim (generated from pyproject.toml)

## Nodes

**Orpheus TTS Model Loader** — loads the Orpheus 3B model and SNAC codec.
Outputs a model reference passed to the generate node.

**Orpheus TTS Generate** — synthesizes speech from text. Inputs: model,
text, voice (tara/leah/jess/leo/dan/mia/zac/zoe), optional language and
chunk size. Supports paralinguistic tags: `<laugh>`, `<chuckle>`, `<sigh>`,
`<cough>`, `<sniffle>`, `<groan>`, `<yawn>`, `<gasp>`.

**Orpheus Audio Effects** — post-processes generated audio. Pitch shift,
speed, volume, normalization, reverb, echo. Pure Python — no SoX dependency.

## Model

Default: `canopylabs/orpheus-3b-0.1-ft` from Hugging Face. Place at
`D:\models\comfyui-models\` per local model store convention.

Standards: https://github.com/Positronikal/PositronikalCodingStandards/tree/main/standards/
