# Quickstart Validation Guide

**Phase 1 output for `001-core-node-rewrite`**

Runnable scenarios that prove the feature works end-to-end.

---

## Prerequisites

- ComfyUI Desktop running on port 8188
- Orpheus 3B model at `D:\models\comfyui-models\checkpoints\orpheus-3b\`
- SNAC model downloaded (auto-downloads from HuggingFace on first run if not
  present)
- ComfyUI-Lyra in `custom_nodes/` directory

---

## Scenario 1: Basic TTS (validates P1 — FR-001, FR-003, FR-004)

**Setup**: Fresh ComfyUI workflow, no existing nodes.

**Steps**:
1. Add `Orpheus TTS Model Loader` node. Leave paths at default. Run.
2. Add `Orpheus TTS Generate` node. Connect Loader `model` → Generate `model`.
3. Set text: `"Hello. This is a test of the Lyra text-to-speech system."`
4. Select voice: `tara`. Run.
5. Connect `audio` output to `Preview Audio` node. Run.

**Expected**: Audio plays a female voice reading the text clearly. No error
about SoX or missing system tools. Model loads from the Positronikal model
store path without user configuration.

---

## Scenario 2: SoX-Free Audio Effects (validates P2 — FR-001, FR-002)

**Setup**: Verify SoX is not installed (`sox --version` should fail).

**Steps**:
1. Build Scenario 1 workflow.
2. Add `Lyra Audio Effects` node. Connect Generate `audio` → Effects `audio`.
3. Set `pitch_shift = 3.0`. Run.
4. Compare output audio pitch to Scenario 1.

**Expected**: Audio is pitch-shifted up by approximately 3 semitones. No error
about SoX. Output connects to `Preview Audio` and plays normally.

---

## Scenario 3: Reverb Effect (validates FR-002)

**Steps**: Same as Scenario 2, but set:
- `add_reverb = True`
- `reverb_room_size = 0.7`
- `reverb_amount = 0.5`

**Expected**: Audio has audible room reverb. No clipping or distortion.

---

## Scenario 4: Paralinguistic Tags (validates P2 — FR-005, FR-006)

**Steps**:
1. In Generate node, set text: `"Are you serious? <laugh> That is the funniest thing I've heard all week."`
2. Set `element_position = none` (tags are manual). Run.

**Expected**: Audio contains laughter after "Are you serious?" and before "That
is the funniest thing."

**Pipe mode sub-test**:
1. Set text: `"I can't believe it | That's incredible | Wow."`
2. Set `paralinguistic_element = laugh`, `element_position = pipe`. Run.

**Expected**: Audio contains laughter at each `|` position.

---

## Scenario 5: Long Text Chunking (validates FR-007)

**Steps**:
1. Set text to a passage of 5+ sentences (at least 500 characters).
2. Run.

**Expected**: Audio plays the full passage continuously. No truncation. No
visible join artifacts between chunks that would indicate incorrect
concatenation.

---

## Scenario 6: Dev Environment (validates P3 — FR-008, FR-009, FR-010)

**Steps** (from repo root):
```bash
uv sync --group dev
ruff check .
ruff format . --check
uv run pyright .
```

**Expected**: All three commands exit 0. No warnings in production source files.

**CI sub-test**: Trigger a push to a branch. CI workflow completes without
pulling torch or timing out on model downloads.

---

## Known Limitations at v1.0

- Voice cloning from audio reference: not supported (Orpheus 3B architecture).
- Long-form audio (full episode dialogue): chunked but join artifacts may be
  audible at sentence boundaries in some cases.
- GPU required for reasonable generation speed; CPU generation is supported but
  slow (~5–10× real-time on modern hardware).
