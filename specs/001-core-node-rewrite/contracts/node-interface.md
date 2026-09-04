# Node Interface Contracts

**Phase 1 output for `001-core-node-rewrite`**

ComfyUI custom nodes expose their interface via class attributes read by
ComfyUI's node registry. The contracts below define the binding interface for
each node in ComfyUI-Lyra.

---

## OrpheusTTSModelLoader

**Category**: `Lyra`
**Display Name**: `Orpheus TTS Model Loader`
**Output type**: `MODEL_REF` (custom type string, acts as opaque handle)

### Inputs

| Name | Type | Default | Notes |
|---|---|---|---|
| orpheus_model_path | STRING | `D:\models\comfyui-models\checkpoints\orpheus-3b` | Path to Orpheus 3B model directory or HF repo id |
| snac_model_path | STRING | `hubertsiuzdak/snac_24khz` | SNAC codec path or HF repo id |
| device | COMBO | `auto` | `auto`, `cpu`, `cuda` |

### Outputs

| Name | Type | Notes |
|---|---|---|
| model | MODEL_REF | Opaque reference dict consumed by Generate node |

### Behavior

- Loads model from `orpheus_model_path` on first execution.
- ComfyUI caches the output; model is not reloaded unless inputs change.
- Raises a descriptive error if the path does not exist and is not a valid
  HuggingFace repo id.

---

## OrpheusTTSGenerate

**Category**: `Lyra`
**Display Name**: `Orpheus TTS Generate`
**Output type**: `AUDIO`

### Inputs

| Name | Type | Default | Notes |
|---|---|---|---|
| model | MODEL_REF | required | From OrpheusTTSModelLoader |
| text | STRING | `""` | Prompt text; may contain paralinguistic tags |
| voice | COMBO | `tara` | tara, leah, jess, leo, dan, mia, zac, zoe |
| paralinguistic_element | COMBO | `none` | none, laugh, chuckle, sigh, cough, sniffle, groan, yawn, gasp |
| element_position | COMBO | `none` | none, append, prepend, pipe |
| temperature | FLOAT | `0.6` | 0.1–2.0 |
| top_p | FLOAT | `0.8` | 0.1–1.0 |
| repetition_penalty | FLOAT | `1.2` | 1.0–2.0 |
| max_tokens | INT | `2048` | 128–16384 |

### Outputs

| Name | Type | Notes |
|---|---|---|
| audio | AUDIO | `{"waveform": Tensor, "sample_rate": 24000}` |

### Behavior

- Applies tag placement before inference (none / append / prepend / pipe).
- Splits text at sentence boundaries when it exceeds a safe token length.
  Concatenates audio chunks.
- Raises a descriptive error if text is empty after stripping whitespace.

---

## LyraAudioEffects

**Category**: `Lyra`
**Display Name**: `Lyra Audio Effects`
**Output type**: `AUDIO`

### Inputs

| Name | Type | Default | Notes |
|---|---|---|---|
| audio | AUDIO | required | From Generate node or any AUDIO source |
| pitch_shift | FLOAT | `0.0` | -12.0–+12.0 semitones |
| speed_factor | FLOAT | `1.0` | 0.5–2.0 |
| gain_db | FLOAT | `0.0` | -20.0–+20.0 dB |
| normalize | BOOLEAN | `False` | Normalize output to -1 dBFS |
| add_reverb | BOOLEAN | `False` | Apply room reverb |
| reverb_room_size | FLOAT | `0.5` | 0.0–1.0 |
| reverb_amount | FLOAT | `0.3` | 0.0–1.0, dry/wet mix |
| add_echo | BOOLEAN | `False` | Apply echo/delay |
| echo_delay | FLOAT | `0.5` | 0.1–2.0 seconds |
| echo_decay | FLOAT | `0.5` | 0.0–1.0, feedback |

### Outputs

| Name | Type | Notes |
|---|---|---|
| audio | AUDIO | Processed audio at original sample rate |

### Behavior

- All effects implemented via pedalboard (no system binaries).
- Effects chain order: pitch → speed → reverb → echo → gain → normalize.
- Passthrough when all parameters are at their defaults (no processing).
- Output sample rate matches input sample rate.

---

## NODE_CLASS_MAPPINGS (registration)

```python
NODE_CLASS_MAPPINGS = {
    "OrpheusTTSModelLoader": OrpheusTTSModelLoader,
    "OrpheusTTSGenerate": OrpheusTTSGenerate,
    "LyraAudioEffects": LyraAudioEffects,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OrpheusTTSModelLoader": "Orpheus TTS Model Loader",
    "OrpheusTTSGenerate": "Orpheus TTS Generate",
    "LyraAudioEffects": "Lyra Audio Effects",
}
```
