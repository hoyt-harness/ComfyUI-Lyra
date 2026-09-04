<!-- SYNC IMPACT REPORT
Version change: (none) → 1.0.0
Added sections: Core Principles (I–V), ComfyUI Integration Standards, Development Workflow, Governance
Removed sections: all placeholder tokens replaced
Follow-up TODOs: none
-->

# ComfyUI-Lyra Constitution

## Core Principles

### I. No System Dependencies

All audio processing MUST use pure Python (librosa, soundfile, scipy, numpy).
No subprocess calls to system audio tools. The SoX dependency inherited from
upstream is eliminated entirely. This is the primary architectural departure
from the upstream fork and is non-negotiable. Any proposed audio feature that
requires a system binary install is out of scope until a pure-Python equivalent
is evaluated and ruled out.

**Rationale:** SoX is a system-level install that breaks in clean environments,
containers, and CI runners. ComfyUI users should not need to install external
tools to use a custom node.

### II. Inference via Transformers Only

The Orpheus 3B model MUST be loaded and run via `transformers` + `snac` directly.
`vllm` is explicitly prohibited — it is incompatible with Windows environments
and the ComfyUI ecosystem. The inference implementation follows ShmuelRonen's
proven approach. Swapping the inference backend requires a new spec.

**Rationale:** vllm is the official `orpheus-speech` package's backend but is
Linux-only. `transformers` works on Windows and is already proven against this
model by the upstream fork.

### III. ComfyUI-Native Integration

Nodes MUST conform to ComfyUI's type and pattern conventions: proper
`INPUT_TYPES`, `RETURN_TYPES`, `FUNCTION`, and `CATEGORY` class attributes.
Node outputs use ComfyUI's `AUDIO` type to chain into the standard audio graph.
No monkey-patching ComfyUI internals. Behavior is validated against the
ComfyUI Desktop app (port 8188), not a standalone runner.

**Rationale:** Conformance to ComfyUI's patterns ensures the node works in any
ComfyUI environment and can pass through ComfyUI Manager's type system if
registration is ever pursued.

### IV. Positronikal Model Store Convention

Models MUST default to loading from `D:\models\comfyui-models\` (our local
model store). Paths MUST be configurable via node inputs — no hardcoded
HuggingFace cache paths in the default config. The model loader node exposes
explicit path inputs rather than relying on implicit cache resolution.

**Rationale:** Consistency with our broader ComfyUI model inventory. All models
live in one place; nodes that scatter downloads to hidden cache dirs create
inventory and disk management problems.

### V. Character Production Ready

The primary production use case is voice generation for Positronikal characters
(Joule Volta and Rōnin Saja). Node design MUST support repeatable, consistent
voice selection — the same voice name produces consistent output. Paralinguistic
tags (`<laugh>`, `<sigh>`, etc.) MUST be exposed with a clean UI. Features that
complicate the character voice workflow are deprioritized against features that
improve it.

**Rationale:** This is not a general-purpose TTS node for the community — it is
production tooling for a specific content pipeline. Design decisions serve that
use case first.

## ComfyUI Integration Standards

- Node `CATEGORY` prefix: `"Lyra"`
- All nodes register via `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`
  in `__init__.py`
- Node outputs that carry audio data MUST use ComfyUI's `AUDIO` type
- Model references passed between nodes use ComfyUI's standard dict-passing
  convention (not global state)
- `requirements.txt` is a generated ComfyUI Manager compatibility shim;
  `pyproject.toml` is the source of truth for dependencies
- The `uv.lock` file is committed and defines the reproducible dev environment

## Development Workflow

All significant changes follow the spec-kit workflow:
`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`

The hooks gate (`hooks/ci-check.sh`) MUST pass before any commit. CI is
confirmation only — local pass is the gate.

Runtime and dev dependencies MUST be separated before CI is declared green.
The `torch`/`transformers`/`snac` runtime stack MUST NOT be required for
lint-only CI runs.

The SoX removal is the first and highest-priority spec item. It gates all
other audio feature work.

## Governance

This constitution supersedes upstream patterns where they conflict. Amendments
require a `/speckit-constitution` update and version bump before implementation
begins. Spec-kit specs supersede CLAUDE.md for project-specific implementation
decisions; CLAUDE.md governs repo-level operations (commits, hooks, standards).

Compliance review: any PR or significant commit is checked against these
principles before merge. The spec-kit plan and tasks documents are the
implementation-level expression of these principles.

**Version**: 1.0.0 | **Ratified**: 2026-09-04 | **Last Amended**: 2026-09-04
