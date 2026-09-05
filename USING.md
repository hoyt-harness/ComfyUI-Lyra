# Using ComfyUI-Lyra

Orpheus TTS 3B text-to-speech custom node for ComfyUI. No SoX or other
system-level audio tools required.

## Installation

### 1. Place the node

Clone into your ComfyUI instance's `custom_nodes` directory, or symlink for
development:

```sh
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/hoyt-harness/ComfyUI-Lyra
```

### 2. Install Python dependencies

Install into the Python environment that runs ComfyUI:

```sh
/path/to/comfyui/python -m pip install -r ComfyUI-Lyra/requirements.txt
```

With ComfyUI Desktop on Windows (the `.venv` path):

```
C:\Users\<user>\AppData\Local\Programs\ComfyUI\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Download the model

```sh
hf download canopylabs/orpheus-3b-0.1-ft --local-dir /path/to/models/checkpoints/orpheus-3b
```

SNAC (`hubertsiuzdak/snac_24khz`) auto-downloads from HuggingFace on first
run if not already cached.

> **Note**: `canopylabs/orpheus-3b-0.1-ft` is a gated model — you must
> accept the terms on the HuggingFace model page before downloading.

### 4. Restart ComfyUI

The three Lyra nodes appear under **Extensions › Lyra** in the node browser.

---

## Basic workflow

**Orpheus TTS Model Loader** → **Orpheus TTS Generate** → **Preview Audio**

1. Add `Orpheus TTS Model Loader`. Set `orpheus_model_path` to your model
   directory (default: `D:\models\comfyui-models\checkpoints\orpheus-3b`).
2. Add `Orpheus TTS Generate`. Connect Loader `model` → Generate `model`.
3. Type your text. Select a voice. Run.
4. Connect the `audio` output to `Preview Audio` or `Save Audio`.

---

## Voices

Eight voice presets from the English fine-tune:

`tara` · `leah` · `jess` · `leo` · `dan` · `mia` · `zac` · `zoe`

---

## Paralinguistic tags

Embed emotional vocalizations inline in text or use the placement helper:

| Tag | Effect |
|---|---|
| `<laugh>` | Laughter |
| `<chuckle>` | Light laughter |
| `<sigh>` | Exhale with emotion |
| `<cough>` | Throat clearing |
| `<sniffle>` | Subtle nasal sound |
| `<groan>` | Low grumble |
| `<yawn>` | Tired exhale |
| `<gasp>` | Sudden intake of breath |

**Placement modes** (via the `element_position` input):

- `none` — type tags directly in text: `That's funny! <laugh> I love it.`
- `append` — selected tag added at the end of text
- `prepend` — selected tag added at the start
- `pipe` — each `|` in text is replaced by the selected tag:
  `That's funny! | I love it.` with `laugh` → `That's funny! <laugh> I love it.`

---

## Audio effects

Chain `Lyra Audio Effects` after `Orpheus TTS Generate`:

| Parameter | Range | Effect |
|---|---|---|
| `pitch_shift` | -12 to +12 semitones | Pitch-corrected pitch change |
| `speed_factor` | 0.5× to 2.0× | Speed without pitch change |
| `gain_db` | -20 to +20 dB | Volume |
| `normalize` | bool | Peak normalize to -1 dBFS |
| `add_reverb` | bool | Room reverb |
| `reverb_room_size` | 0.0–1.0 | Room size |
| `reverb_amount` | 0.0–1.0 | Dry/wet mix |
| `add_echo` | bool | Echo/delay |
| `echo_delay` | 0.1–2.0 s | Delay time |
| `echo_decay` | 0.0–1.0 | Feedback |

No SoX installation required. All effects use pedalboard (pure Python).

---

## Multilingual models

The node supports Canopy AI's language-specific fine-tunes. Specify the
model path or HuggingFace repo ID in the Loader's `orpheus_model_path`:

| Language | Repo |
|---|---|
| German | `canopylabs/3b-de-ft-research_release` |
| French | `canopylabs/3b-fr-ft-research_release` |
| Spanish/Italian | `canopylabs/3b-es-it-ft-research_release` |
| Korean | `canopylabs/3b-ko-ft-research_release` |
| Hindi | `canopylabs/3b-hi-ft-research_release` |
| Chinese | `canopylabs/3b-zh-ft-research_release` |

---

## Long text

Text longer than ~220 characters is automatically chunked at sentence
boundaries and the audio segments are concatenated. No manual splitting
required.
