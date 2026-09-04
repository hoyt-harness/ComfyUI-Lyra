# Data Model: Core Node Rewrite

**Phase 1 output for `001-core-node-rewrite`**

---

## Entities

### ModelReference

Passed between the Loader and Generate nodes via ComfyUI's node graph.

```
ModelReference:
  orpheus_model    — loaded Orpheus 3B transformer model
  snac_model       — loaded SNAC 24kHz codec
  tokenizer        — Orpheus tokenizer
  device           — torch device (cpu / cuda)
  model_path       — absolute path from which the model was loaded
  snac_path        — absolute path from which SNAC was loaded
```

**Validation**: model_path and snac_path must exist at load time. device is
auto-detected from torch unless explicitly overridden.

**State transitions**: ModelReference is created once by the Loader and held in
memory for the session. ComfyUI re-invokes the Loader if the node is
reconnected or ComfyUI restarts.

---

### AudioOutput

ComfyUI-standard audio dict passed between Generate, Effects, and downstream
audio nodes.

```
AudioOutput:
  waveform    — torch.Tensor, shape (1, channels, samples), float32
  sample_rate — int, 24000 (Orpheus native sample rate)
```

This structure matches ComfyUI's expected AUDIO type dict
(`{"waveform": tensor, "sample_rate": int}`).

---

### Voice

An enum-like selection value represented as a string in the node UI.

```
Voice:
  name — one of: tara, leah, jess, leo, dan, mia, zac, zoe
```

The voice name is prepended to the prompt text as a conditioning token before
inference. No audio reference is used.

---

### ParalinguisticTag

An inline text marker that triggers an emotional vocalization.

```
ParalinguisticTag:
  token — one of: <laugh>, <chuckle>, <sigh>, <cough>,
                  <sniffle>, <groan>, <yawn>, <gasp>
```

Tags are embedded in the text prompt. The model is trained to produce
corresponding vocalizations when it encounters these tokens.

---

### TagPlacementMode

Controls how the UI inserts a selected paralinguistic tag into text.

```
TagPlacementMode:
  NONE    — no automatic insertion; user places tags manually in text
  APPEND  — selected tag appended to end of text
  PREPEND — selected tag prepended to start of text
  PIPE    — each | character in text replaced with the selected tag
```

---

### EffectsConfig

Parameters consumed by the Audio Effects node.

```
EffectsConfig:
  pitch_shift      — float, semitones, range -12.0 to +12.0, default 0.0
  speed_factor     — float, multiplier, range 0.5 to 2.0, default 1.0
  gain_db          — float, decibels, range -20.0 to +20.0, default 0.0
  normalize        — bool, default False
  add_reverb       — bool, default False
  reverb_room_size — float, 0.0 to 1.0, default 0.5
  reverb_amount    — float, 0.0 to 1.0, default 0.3
  add_echo         — bool, default False
  echo_delay       — float, seconds, range 0.1 to 2.0, default 0.5
  echo_decay       — float, 0.0 to 1.0, default 0.5
```

All parameters are exposed as ComfyUI node inputs with their respective
ranges enforced by the INT/FLOAT type constraints.
