# Feature Specification: Core Node Rewrite

**Feature Branch**: `001-core-node-rewrite`

**Created**: 2026-09-04

**Status**: Draft

**Input**: Rebuild ComfyUI-Lyra from the upstream hard fork into a clean,
production-ready Orpheus TTS custom node — SoX-free audio effects, clean node
architecture, working dev environment, and CI passing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Basic TTS Voice Generation (Priority: P1)

A content producer opens ComfyUI, adds the Lyra TTS model loader and generate
nodes, selects a voice, types dialogue text, and connects the output to an audio
preview or save node. The audio plays back correctly with no external tools
installed beyond ComfyUI and its Python environment.

**Why this priority**: This is the entire reason the node exists. Nothing else
matters until basic generation works cleanly without external dependencies.

**Independent Test**: Add Orpheus TTS Model Loader → Orpheus TTS Generate →
Preview Audio in a fresh ComfyUI Desktop workflow. Enter text, run. Audio plays.

**Acceptance Scenarios**:

1. **Given** ComfyUI Desktop is running with Lyra in custom_nodes, **When** the
   user loads the Orpheus model and generates speech with default settings,
   **Then** audio plays back in the ComfyUI audio preview within a reasonable
   wait time and sounds like the selected voice.

2. **Given** no SoX is installed on the system, **When** the user runs the TTS
   generate node, **Then** generation succeeds without any error about missing
   system tools.

3. **Given** the model files are in the Positronikal model store path, **When**
   the loader node runs, **Then** it finds and loads the model without requiring
   the user to configure a different path.

---

### User Story 2 — Audio Effects Without System Tools (Priority: P2)

A content producer chains the Lyra audio effects node after voice generation to
apply pitch adjustment, speed change, or reverb to a generated clip — without
installing SoX or any other system-level audio program.

**Why this priority**: The audio effects node is the second major node in the
set and directly supports the character voice post-processing workflow.
Eliminating the SoX dependency is the primary architectural goal of the fork.

**Independent Test**: Add Orpheus TTS Generate → Lyra Audio Effects → Preview
Audio. Apply a non-default pitch shift. Audio plays back pitch-shifted. Verify
SoX is not present on the system during the test.

**Acceptance Scenarios**:

1. **Given** SoX is not installed, **When** the user applies pitch shift via the
   audio effects node, **Then** the audio is pitch-shifted and no error is raised.

2. **Given** default reverb settings, **When** the user enables reverb in the
   effects node, **Then** the output audio has audible reverb applied.

3. **Given** speed factor set to 0.8, **When** the node runs, **Then** the output
   audio is slowed to approximately 80% of the original speed.

---

### User Story 3 — Paralinguistic Tag Authoring (Priority: P2)

A content producer writes dialogue containing emotional cues — laughter, sighs,
gasps — by typing tags directly into the text input or using the tag placement
helper in the generate node.

**Why this priority**: Character voice production for Joule and Rōnin requires
emotional performance. Paralinguistic tags are how Orpheus expresses emotion.
This is a direct production requirement, not a nice-to-have.

**Independent Test**: Enter text containing `<laugh>` and `<sigh>` tags in the
generate node. Run. Verify the output audio contains the corresponding emotional
vocalizations at the correct positions.

**Acceptance Scenarios**:

1. **Given** a text input containing `That's hilarious! <laugh> I can't stop.`,
   **When** the generate node runs, **Then** the audio contains laughter at the
   tagged position.

2. **Given** the pipe placement mode selected and a text with `|` characters,
   **When** a paralinguistic element is chosen, **Then** each `|` is replaced by
   that element tag before generation.

---

### User Story 4 — Developer Setup and CI (Priority: P3)

A developer clones the repo, runs `uv sync`, and has a working dev environment
with lint and type checking passing. The CI workflow runs the same checks on
push without pulling in the heavy runtime model stack.

**Why this priority**: Operational hygiene for ongoing maintenance. Required
before any further development can happen cleanly, but does not block basic
generation from working.

**Independent Test**: Fresh clone, `uv sync --group dev` (dev deps only), `ruff
check .` and `pyright .` both pass. CI workflow completes without timing out on
model downloads.

**Acceptance Scenarios**:

1. **Given** a fresh clone with no model files present, **When** the developer
   runs the dev-only install, **Then** linting and type checking pass without
   errors.

2. **Given** a CI runner with no GPU, **When** the CI workflow runs on push,
   **Then** lint and static analysis complete successfully without attempting to
   download or load model weights.

---

### Edge Cases

- What happens when the model files are not present at the configured path? The
  loader node should raise a clear, actionable error — not a Python traceback.
- What happens when the input text is empty? The generate node should surface a
  clear validation error before attempting inference.
- What happens when text is very long (thousands of characters)? Chunking must
  split at sentence boundaries without losing content.
- What happens when an unknown paralinguistic tag is entered? The node should
  pass it through to the model without crashing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The node package MUST install in a ComfyUI environment using only
  `requirements.txt`, with no system-level dependencies beyond Python.
- **FR-002**: All audio effects (pitch, speed, volume, reverb, echo,
  normalization) MUST be implemented using pure-Python audio libraries with no
  subprocess calls to system binaries.
- **FR-003**: The Orpheus TTS Model Loader node MUST accept an explicit model
  path and default to the Positronikal model store location.
- **FR-004**: The Orpheus TTS Generate node MUST produce a ComfyUI `AUDIO`-typed
  output compatible with standard ComfyUI audio nodes.
- **FR-005**: The generate node MUST support all eight paralinguistic tags:
  `<laugh>`, `<chuckle>`, `<sigh>`, `<cough>`, `<sniffle>`, `<groan>`,
  `<yawn>`, `<gasp>`.
- **FR-006**: The generate node MUST support tag placement modes: none (manual),
  append, prepend, and pipe (replace `|` with the selected tag).
- **FR-007**: The generate node MUST handle long text by chunking at sentence
  boundaries and concatenating audio output.
- **FR-008**: The dev environment MUST separate runtime dependencies (model
  inference stack) from dev-only dependencies (lint, type check, test tooling)
  so that lint and static analysis can run without model weights present.
- **FR-009**: The `ruff check` and `pyright` passes MUST be clean against the
  rewritten source files.
- **FR-010**: The hooks CI gate (`hooks/ci-check.sh`) MUST pass for lint-only
  checks before the runtime stack is available.

### Key Entities

- **Model Reference**: A handle to loaded Orpheus 3B model + SNAC codec, passed
  between the loader and generate nodes.
- **Audio Output**: A ComfyUI-compatible audio dict containing waveform data and
  sample rate, produced by the generate and effects nodes.
- **Voice**: A named character preset (tara, leah, jess, leo, dan, mia, zac,
  zoe) selecting tonal characteristics from the fine-tuned model.
- **Paralinguistic Tag**: An inline text marker (`<laugh>`, etc.) that triggers
  an emotional vocalization in the generated audio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A complete TTS workflow (loader → generate → audio preview) runs
  end-to-end in ComfyUI Desktop with no external system tool installed.
- **SC-002**: All eight paralinguistic tags produce audibly distinct emotional
  vocalizations in generated audio.
- **SC-003**: All three audio effects (pitch shift, speed change, reverb)
  produce audibly correct results when applied via the effects node.
- **SC-004**: Lint and static analysis pass cleanly on all rewritten source files
  with zero suppressed warnings in production code.
- **SC-005**: The CI workflow completes in a standard (non-GPU) environment
  without timing out or requiring model downloads.
- **SC-006**: A developer can install the dev environment and run all CI checks
  in under 5 minutes on a machine with cached dependencies.

## Assumptions

- ComfyUI Desktop is the primary runtime environment; the Desktop app's Python
  environment provides torch, CUDA, and ComfyUI core at runtime.
- Model weights (`canopylabs/orpheus-3b-0.1-ft`, `hubertsiuzdak/snac_24khz`)
  have already been downloaded to the Positronikal model store.
- Pure-Python audio processing (via librosa or equivalent) is sufficient for the
  required effects quality — professional studio-grade processing is out of scope.
- Long-form audio for full episode dialogue is out of scope for v1; chunk-and-
  concatenate is the accepted mechanism for passages beyond a few sentences.
- Voice cloning from arbitrary audio reference is out of scope — Orpheus 3B uses
  named voice presets from its fine-tuning, not audio conditioning.
- No GUI configuration panel beyond ComfyUI's standard node inputs is in scope.
