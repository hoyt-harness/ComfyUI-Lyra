# SPDX-License-Identifier: GPL-3.0-or-later
"""OrpheusTTSGenerate — ComfyUI node for Orpheus TTS speech generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.chunking import MAX_CHARS, chunk_text, concatenate_audio
from core.inference import generate_speech_chunk, waveform_to_comfy_audio

if TYPE_CHECKING:
    from core.model import ModelReference

_VOICES = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]
_ELEMENTS = [
    "none",
    "laugh",
    "chuckle",
    "sigh",
    "cough",
    "sniffle",
    "groan",
    "yawn",
    "gasp",
]
_POSITIONS = ["none", "append", "prepend", "pipe"]


def _apply_tag_placement(text: str, element: str, position: str) -> str:
    """Insert a paralinguistic tag into text according to placement mode."""
    if element == "none" or position == "none":
        return text
    tag = f"<{element}>"
    if position == "append":
        return f"{text} {tag}"
    if position == "prepend":
        return f"{tag} {text}"
    if position == "pipe":
        return text.replace("|", tag)
    return text


class OrpheusTTSGenerate:
    """Generate speech audio from text using the loaded Orpheus model."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "model": ("MODEL_REF",),
                "text": ("STRING", {"multiline": True, "default": ""}),
                "voice": (_VOICES, {"default": "tara"}),
            },
            "optional": {
                "paralinguistic_element": (_ELEMENTS, {"default": "none"}),
                "element_position": (_POSITIONS, {"default": "none"}),
                "temperature": (
                    "FLOAT",
                    {"default": 0.6, "min": 0.1, "max": 2.0, "step": 0.05},
                ),
                "top_p": (
                    "FLOAT",
                    {"default": 0.95, "min": 0.1, "max": 1.0, "step": 0.05},
                ),
                "repetition_penalty": (
                    "FLOAT",
                    {"default": 1.1, "min": 1.0, "max": 2.0, "step": 0.05},
                ),
                "max_new_tokens": (
                    "INT",
                    {"default": 2000, "min": 128, "max": 4000, "step": 100},
                ),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "generate"
    CATEGORY = "Lyra"

    @classmethod
    def IS_CHANGED(cls, **_kwargs: object) -> float:
        return float("NaN")  # always re-run

    def generate(
        self,
        model: ModelReference,
        text: str,
        voice: str = "tara",
        paralinguistic_element: str = "none",
        element_position: str = "none",
        temperature: float = 0.6,
        top_p: float = 0.95,
        repetition_penalty: float = 1.1,
        max_new_tokens: int = 2000,
    ) -> tuple[dict]:
        text = _apply_tag_placement(text, paralinguistic_element, element_position)

        chunks = chunk_text(text, max_chars=MAX_CHARS)

        audio_segments = [
            generate_speech_chunk(
                model,
                chunk,
                voice=voice,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                max_new_tokens=max_new_tokens,
            )
            for chunk in chunks
        ]

        combined = concatenate_audio(audio_segments)
        return (waveform_to_comfy_audio(combined),)
