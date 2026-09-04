# SPDX-License-Identifier: GPL-3.0-or-later
"""LyraAudioEffects — ComfyUI node for pure-Python audio post-processing."""

from __future__ import annotations

from core.effects import apply_effects
from core.inference import comfy_audio_to_numpy, waveform_to_comfy_audio


class LyraAudioEffects:
    """Apply pitch, speed, reverb, echo, and gain effects to AUDIO input."""

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "audio": ("AUDIO",),
            },
            "optional": {
                "pitch_shift": (
                    "FLOAT",
                    {"default": 0.0, "min": -12.0, "max": 12.0, "step": 0.5},
                ),
                "speed_factor": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.5, "max": 2.0, "step": 0.05},
                ),
                "gain_db": (
                    "FLOAT",
                    {"default": 0.0, "min": -20.0, "max": 20.0, "step": 0.5},
                ),
                "normalize": ("BOOLEAN", {"default": False}),
                "add_reverb": ("BOOLEAN", {"default": False}),
                "reverb_room_size": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "reverb_amount": (
                    "FLOAT",
                    {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
                "add_echo": ("BOOLEAN", {"default": False}),
                "echo_delay": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.1, "max": 2.0, "step": 0.1},
                ),
                "echo_decay": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.05},
                ),
            },
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "apply"
    CATEGORY = "Lyra"

    def apply(
        self,
        audio: dict,
        pitch_shift: float = 0.0,
        speed_factor: float = 1.0,
        gain_db: float = 0.0,
        normalize: bool = False,
        add_reverb: bool = False,
        reverb_room_size: float = 0.5,
        reverb_amount: float = 0.3,
        add_echo: bool = False,
        echo_delay: float = 0.5,
        echo_decay: float = 0.5,
    ) -> tuple[dict]:
        sample_rate: int = audio.get("sample_rate", 24_000)
        waveform_np = comfy_audio_to_numpy(audio)

        processed = apply_effects(
            waveform=waveform_np,
            sample_rate=sample_rate,
            pitch_shift=pitch_shift,
            speed_factor=speed_factor,
            gain_db=gain_db,
            normalize=normalize,
            add_reverb=add_reverb,
            reverb_room_size=reverb_room_size,
            reverb_amount=reverb_amount,
            add_echo=add_echo,
            echo_delay=echo_delay,
            echo_decay=echo_decay,
        )

        return (waveform_to_comfy_audio(processed, sample_rate),)
