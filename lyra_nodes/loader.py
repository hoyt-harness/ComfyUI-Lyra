# SPDX-License-Identifier: GPL-3.0-or-later
"""OrpheusTTSModelLoader — ComfyUI node that loads Orpheus 3B and SNAC."""

from __future__ import annotations

from core.model import (
    DEFAULT_ORPHEUS_PATH,
    DEFAULT_SNAC_PATH,
    ModelReference,
    load_model,
)


class OrpheusTTSModelLoader:
    """Load Orpheus 3B and SNAC codec models into a ModelReference."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {},
            "optional": {
                "orpheus_model_path": (
                    "STRING",
                    {"default": DEFAULT_ORPHEUS_PATH},
                ),
                "snac_model_path": (
                    "STRING",
                    {"default": DEFAULT_SNAC_PATH},
                ),
                "device": (
                    ["auto", "cuda", "cpu"],
                    {"default": "auto"},
                ),
            },
        }

    RETURN_TYPES = ("MODEL_REF",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load"
    CATEGORY = "Lyra"

    def load(
        self,
        orpheus_model_path: str = DEFAULT_ORPHEUS_PATH,
        snac_model_path: str = DEFAULT_SNAC_PATH,
        device: str = "auto",
    ) -> tuple[ModelReference]:
        model_ref = load_model(
            orpheus_path=orpheus_model_path,
            snac_path=snac_model_path,
            device=device,
        )
        return (model_ref,)
