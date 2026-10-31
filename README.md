# ComfyUI-Lyra

Orpheus TTS 3B text-to-speech for ComfyUI. Hard fork of
[ComfyUI-Orpheus-TTS](https://github.com/ShmuelRonen/ComfyUI-Orpheus-TTS)
(MIT) — relicensed GPLv3. No SoX or other system-level audio tools required;
all effects run via [pedalboard](https://github.com/spotify/pedalboard).

## Nodes

**Orpheus TTS Model Loader** — loads the Orpheus 3B model and SNAC codec.
Default model path: `D:\models\comfyui-models\checkpoints\orpheus-3b`.
Outputs a `MODEL_REF` passed to the generate node.

**Orpheus TTS Generate** — synthesizes speech from text. Inputs: model,
text, voice, paralinguistic element, placement mode, generation parameters.
Eight voices: `tara` · `leah` · `jess` · `leo` · `dan` · `mia` · `zac` · `zoe`

**Lyra Audio Effects** — post-processes audio. Pitch shift, speed,
gain, reverb, echo, normalize — all via pedalboard (pure Python, no SoX).

## Paralinguistic tags

Embed emotional vocalizations in text or use the placement helper:

`<laugh>` · `<chuckle>` · `<sigh>` · `<cough>` · `<sniffle>` · `<groan>` · `<yawn>` · `<gasp>`

**Placement modes:** `none` (manual inline) · `append` · `prepend` · `pipe`
(`|` in text is replaced by the selected tag)

## Quick start

See [USING.md](USING.md) for full installation, workflow, audio effects
reference, multilingual models, and long-text handling.

```
Orpheus TTS Model Loader → Orpheus TTS Generate → Preview Audio
```

Clone into your ComfyUI `custom_nodes` directory, install dependencies
into ComfyUI's Python environment, download the model, restart ComfyUI:

```sh
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/hoyt-harness/ComfyUI-Lyra
/path/to/comfyui/python -m pip install -r ComfyUI-Lyra/requirements.txt
hf download canopylabs/orpheus-3b-0.1-ft --local-dir /path/to/models/checkpoints/orpheus-3b
```

## Development

```sh
uv sync --group dev          # lint / type / test (no GPU required)
uv sync --extra runtime      # full runtime stack
bash hooks/ci-check.sh       # full CI check
```

## Version

See [releases](https://github.com/hoyt-harness/ComfyUI-Lyra/releases) or
`git tag`.

## License

GPLv3 — see [LICENSE](LICENSE). Incorporates upstream
[ComfyUI-Orpheus-TTS](https://github.com/ShmuelRonen/ComfyUI-Orpheus-TTS)
(MIT) — see [ATTRIBUTION.md](ATTRIBUTION.md).
