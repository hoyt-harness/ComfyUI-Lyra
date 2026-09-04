# SPDX-License-Identifier: GPL-3.0-or-later
"""Model loading and ModelReference for ComfyUI-Lyra."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    import torch
    from snac import SNAC
    from transformers import AutoModelForCausalLM, AutoTokenizer

    _RUNTIME_AVAILABLE = True
except ImportError:
    _RUNTIME_AVAILABLE = False

SAMPLE_RATE = 24_000
DEFAULT_ORPHEUS_PATH = r"D:\models\comfyui-models\checkpoints\orpheus-3b"
DEFAULT_SNAC_PATH = "hubertsiuzdak/snac_24khz"


@dataclass
class ModelReference:
    """Opaque handle passed between the Loader and Generate nodes."""

    orpheus_model: Any
    snac_model: Any
    tokenizer: Any
    device: Any
    model_path: str
    snac_path: str


def _resolve_device(device_str: str) -> Any:
    import torch  # noqa: PLC0415

    if device_str == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device_str)


def load_model(
    orpheus_path: str = DEFAULT_ORPHEUS_PATH,
    snac_path: str = DEFAULT_SNAC_PATH,
    device: str = "auto",
) -> ModelReference:
    """Load Orpheus 3B and SNAC models.

    Raises FileNotFoundError for local paths that do not exist.
    Raises RuntimeError if runtime dependencies are not installed.
    """
    if not _RUNTIME_AVAILABLE:
        raise RuntimeError(
            "Runtime dependencies not installed. "
            "Install with: uv sync --extra runtime"
        )

    if os.path.sep in orpheus_path and not os.path.isdir(orpheus_path):
        raise FileNotFoundError(
            f"Orpheus model path not found: {orpheus_path}\n"
            "Provide a local directory path or a HuggingFace repo id (e.g. "
            "'canopylabs/orpheus-3b-0.1-ft')."
        )

    resolved_device = _resolve_device(device)

    snac_model = SNAC.from_pretrained(snac_path).to(resolved_device)
    snac_model.eval()

    orpheus_model = AutoModelForCausalLM.from_pretrained(
        orpheus_path,
        torch_dtype=torch.bfloat16,  # type: ignore[name-defined]
    ).to(resolved_device)
    orpheus_model.eval()

    tokenizer = AutoTokenizer.from_pretrained(orpheus_path)

    return ModelReference(
        orpheus_model=orpheus_model,
        snac_model=snac_model,
        tokenizer=tokenizer,
        device=resolved_device,
        model_path=orpheus_path,
        snac_path=snac_path,
    )
