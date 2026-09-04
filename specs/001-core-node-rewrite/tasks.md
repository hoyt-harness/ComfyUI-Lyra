# Tasks: Core Node Rewrite

**Input**: Design documents from `specs/001-core-node-rewrite/`

**References**: [spec.md](spec.md) | [plan.md](plan.md) | [data-model.md](data-model.md) | [contracts/node-interface.md](contracts/node-interface.md) | [quickstart.md](quickstart.md)

**Tests**: Unit tests included for effects pipeline and chunking logic (independently testable without ComfyUI runtime).

**Format**: `[ID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Dependency split, directory structure, and CI configuration.
No user story work begins until this phase is complete.

- [ ] T001 Update `pyproject.toml` — move torch/transformers/snac/librosa/huggingface_hub/nltk/soundfile into `[project.optional-dependencies] runtime = [...]`; keep pedalboard/numpy in base `dependencies`; add pedalboard to dependencies
- [ ] T002 Add pedalboard to `pyproject.toml` base dependencies and run `uv lock` to regenerate `uv.lock`
- [ ] T003 Regenerate `requirements.txt` from the runtime extras for ComfyUI Manager compatibility: `uv export --extra runtime --no-hashes > requirements.txt`
- [ ] T004 Update `hooks/ci-check.sh` — change `uv sync` to `uv sync --group dev` (dev tools only, no torch); remove pyright call on `src/` path (no src/ layout); target root Python files
- [ ] T005 Update `.github/workflows/ci.yml` — verify it still calls `bash hooks/ci-check.sh` unchanged (script is the source of truth; no workflow changes needed if ci-check.sh is correct)
- [ ] T006 Create directory structure: `nodes/`, `core/`, `tests/` at repo root; add `nodes/__init__.py`, `core/__init__.py`, `tests/__init__.py` (empty)

**Checkpoint**: `uv sync --group dev && ruff check . && pyright .` all pass without touching torch.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core inference pipeline. No node can function without this layer.

**⚠️ CRITICAL**: All Phase 3–5 tasks depend on this phase being complete and passing `ruff check` + `pyright`.

- [ ] T007 Write `core/model.py` — `ModelReference` dataclass (fields: orpheus_model, snac_model, tokenizer, device, model_path, snac_path); `load_model(orpheus_path, snac_path, device)` function that loads from local path or HF hub; raises descriptive `FileNotFoundError` if path missing and not a valid HF repo id
- [ ] T008 Write `core/inference.py` — `generate_tokens(model_ref, prompt_string, temperature, top_p, repetition_penalty, max_tokens)` generator; `tokens_to_audio(token_stream, snac_model)` returning numpy float32 waveform at 24kHz; `format_prompt(text, voice)` that prepends voice token; extract logic from upstream `tts_nodes.py` and clean it up
- [ ] T009 Write `core/chunking.py` — `chunk_text(text, max_chars)` splitting at sentence boundaries using nltk `sent_tokenize`; `concatenate_audio(waveforms)` returning a single numpy array; edge cases: empty text raises `ValueError`, single long sentence splits at commas then by character
- [ ] T010 [P] Write `tests/test_chunking.py` — unit tests for `chunk_text`: empty string, single short sentence, multiple sentences, sentence exceeding max_chars, pipe character handling; no ComfyUI or torch dependency

**Checkpoint**: `tests/test_chunking.py` passes via `uv run pytest tests/test_chunking.py` without torch installed.

---

## Phase 3: User Story 1 — Basic TTS Voice Generation (Priority: P1) 🎯 MVP

**Goal**: Complete `Loader → Generate → Audio` flow works in ComfyUI Desktop.

**Independent Test**: Quickstart Scenario 1 — add Loader + Generate + Preview Audio, type text, run, hear audio.

### Implementation

- [ ] T011 [US1] Write `nodes/loader.py` — `OrpheusTTSModelLoader` class with `INPUT_TYPES` (orpheus_model_path STRING default `D:\models\comfyui-models\checkpoints\orpheus-3b`, snac_model_path STRING default `hubertsiuzdak/snac_24khz`, device COMBO [`auto`, `cpu`, `cuda`]); `RETURN_TYPES = ("MODEL_REF",)`; `FUNCTION = "load"`; `CATEGORY = "Lyra"`; calls `core.model.load_model`
- [ ] T012 [US1] Write `nodes/generate.py` — `OrpheusTTSGenerate` class with `INPUT_TYPES` per [contracts/node-interface.md](contracts/node-interface.md); `RETURN_TYPES = ("AUDIO",)`; `FUNCTION = "generate"`; `CATEGORY = "Lyra"`; calls `core.inference.format_prompt`, `core.chunking.chunk_text`, `core.inference.generate_tokens`, `core.inference.tokens_to_audio`, wraps in ComfyUI AUDIO dict `{"waveform": tensor, "sample_rate": 24000}`; raises `ValueError` on empty text
- [ ] T013 [US1] Update `__init__.py` — remove old imports of `tts_nodes` and `orpheus_audio_effects`; import from `nodes.loader` and `nodes.generate`; build `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`; keep `hf_auth` try/except block
- [ ] T014 [US1] Delete upstream source files that have been replaced: `tts_nodes.py`, `orpheus_audio_effects.py`
- [ ] T015 [US1] Run `ruff check . && pyright .` and fix any issues in the new files
- [ ] T016 [US1] Validate Quickstart Scenario 1 in ComfyUI Desktop (manual): add nodes, run, confirm audio plays

**Checkpoint**: Quickstart Scenario 1 passes. User Story 1 fully functional.

---

## Phase 4: User Story 2 — SoX-Free Audio Effects (Priority: P2)

**Goal**: Effects node works without SoX installed using pedalboard.

**Independent Test**: Quickstart Scenario 2 — chain Effects node after Generate, set pitch_shift=3.0, confirm pitched audio with no SoX error.

### Implementation

- [ ] T017 [P] [US2] Write `core/effects.py` — `apply_effects(waveform_np, sample_rate, pitch_shift, speed_factor, gain_db, normalize, add_reverb, reverb_room_size, reverb_amount, add_echo, echo_delay, echo_decay)` using pedalboard; effects chain order: pitch → speed → reverb → echo → gain → normalize; returns numpy float32 array; passthrough when all params at defaults
- [ ] T018 [P] [US2] Write `tests/test_effects.py` — unit tests for `apply_effects`: passthrough (defaults), pitch shift changes pitch, speed factor changes duration, reverb changes audio length, echo adds samples, gain scales amplitude; no ComfyUI dependency; uses synthetic numpy sine wave as input
- [ ] T019 [US2] Write `nodes/effects.py` — `LyraAudioEffects` class with `INPUT_TYPES` per [contracts/node-interface.md](contracts/node-interface.md); `RETURN_TYPES = ("AUDIO",)`; `FUNCTION = "apply"`; `CATEGORY = "Lyra"`; extracts numpy waveform from AUDIO dict, calls `core.effects.apply_effects`, wraps result back into AUDIO dict
- [ ] T020 [US2] Add `LyraAudioEffects` to `__init__.py` `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`
- [ ] T021 [US2] Run `uv run pytest tests/test_effects.py` and fix failures
- [ ] T022 [US2] Validate Quickstart Scenarios 2 and 3 in ComfyUI Desktop (manual): pitch shift and reverb

**Checkpoint**: Both effects tests pass; Quickstart Scenarios 2–3 pass. No SoX required.

---

## Phase 5: User Story 3 — Paralinguistic Tag Authoring (Priority: P2)

**Goal**: All 8 tags work inline and via placement modes in the Generate node.

**Independent Test**: Quickstart Scenario 4 — text with `<laugh>` tag produces laughter at correct position; pipe mode replaces `|` correctly.

### Implementation

- [ ] T023 [P] [US3] Extend `nodes/generate.py` — add `paralinguistic_element` COMBO input (none, laugh, chuckle, sigh, cough, sniffle, groan, yawn, gasp) and `element_position` COMBO input (none, append, prepend, pipe); implement `_apply_tag_placement(text, element, position)` method that handles all four modes; call before chunking
- [ ] T024 [US3] Validate Quickstart Scenario 4 in ComfyUI Desktop (manual): `<laugh>` inline, pipe mode with `|` characters

**Checkpoint**: Paralinguistic tags produce correct vocalizations; pipe mode works as specified.

---

## Phase 6: User Story 4 — Developer Setup and CI (Priority: P3)

**Goal**: Dev environment installs cleanly without torch; CI runs lint-only and passes.

**Independent Test**: Quickstart Scenario 6 — `uv sync --group dev && ruff check . && uv run pyright .` all exit 0.

### Implementation

- [ ] T025 [P] [US4] Update `hooks/ci-check.sh` to add `uv run pytest tests/` after the lint/type check steps (tests run in CI without torch since test_chunking and test_effects use no model dependencies)
- [ ] T026 [US4] Verify `ruff check .` and `uv run pyright .` are clean across all new files; suppress only intentional issues with inline comments where needed
- [ ] T027 [US4] Validate Quickstart Scenario 6 locally; push to trigger CI and confirm it completes without GPU or model downloads

**Checkpoint**: CI passes on standard runner; Scenario 6 passes.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T028 [P] Update `CLAUDE.md` — replace key files section with new layout (nodes/, core/, tests/, pyproject.toml runtime/dev split)
- [ ] T029 [P] Write `USING.md` — installation (copy to custom_nodes/, run requirements.txt in ComfyUI env), model downloads (hf download paths), workflow guide for all three nodes
- [ ] T030 Update `AUTHORS.md` — replace template with Hoyt Harness author entry and ShmuelRonen attribution
- [ ] T031 Generate SBOM: `uv sync --extra runtime && uv run python -m cyclonedx_py environment -o sbom.cdx.json`
- [ ] T032 Run full `positronikal-check D:/Engineering/ComfyUI-Lyra --check all` and fix remaining issues
- [ ] T033 Run all 6 Quickstart scenarios end-to-end for final validation
- [ ] T034 Commit all changes with conventional prefix `feat:`, tag `v1.0.0`, push when remote is configured

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Start immediately — no dependencies
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS Phases 3–6
- **Phase 3 (US1)**: Depends on Phase 2 — P1 priority, implement first
- **Phase 4 (US2) and Phase 5 (US3)**: Both depend on Phase 2; US2 and US3 are independent of each other and can run in parallel
- **Phase 6 (US4)**: Depends on Phases 3, 4, 5 all complete (needs full test suite)
- **Phase 7 (Polish)**: Depends on Phase 6

### Within Each Phase

- [P]-marked tasks within a phase have no dependency on each other
- Non-[P] tasks within a phase run sequentially in list order

### Parallel Opportunities

- T017 (core/effects.py) and T018 (test_effects.py) are parallel — different files
- T023 (tag placement) is parallel to T017/T018 — different files
- T028 (CLAUDE.md) and T029 (USING.md) are parallel — different files

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational) — T007–T010
3. Complete Phase 3 (US1) — T011–T016
4. **STOP and VALIDATE**: ComfyUI Desktop, Quickstart Scenario 1

### Incremental Delivery

1. Phases 1–3 → MVP: Basic TTS works
2. Phase 4 → Add: SoX-free effects
3. Phase 5 → Add: Paralinguistic tags
4. Phase 6 → Add: CI passing
5. Phase 7 → Polish and release v1.0.0

---

## Notes

- [P] tasks have no file conflicts and can be dispatched in the same turn
- Unit tests (T010, T018) have no torch/ComfyUI dependency — they run in dev-only env
- Delete T014 (upstream files) only after verifying the replacements (T011–T013) are complete
- Commit after each phase checkpoint — do not batch unrelated phases into one commit
- Total tasks: 34 | US1: 6 | US2: 6 | US3: 2 | US4: 3 | Setup: 6 | Foundational: 4 | Polish: 7
