# SPDX-License-Identifier: GPL-3.0-or-later

# Try to set up Hugging Face authentication if config exists
try:
    from . import hf_auth
except Exception as e:
    print(
        f"Note: Hugging Face authentication not set up. This is optional for public models: {e}"
    )

"""
Orpheus TTS for ComfyUI - A Text-to-Speech node using the Orpheus system
"""

# Import nodes from TTS module
from .tts_nodes import NODE_CLASS_MAPPINGS as TTS_NODE_CLASS_MAPPINGS
from .tts_nodes import NODE_DISPLAY_NAME_MAPPINGS as TTS_NODE_DISPLAY_NAME_MAPPINGS

# Import nodes from audio effects module
try:
    from .orpheus_audio_effects import (
        NODE_CLASS_MAPPINGS as EFFECTS_NODE_CLASS_MAPPINGS,
    )
    from .orpheus_audio_effects import (
        NODE_DISPLAY_NAME_MAPPINGS as EFFECTS_NODE_DISPLAY_NAME_MAPPINGS,
    )

    # Combine node mappings
    NODE_CLASS_MAPPINGS = {**TTS_NODE_CLASS_MAPPINGS, **EFFECTS_NODE_CLASS_MAPPINGS}

    NODE_DISPLAY_NAME_MAPPINGS = {
        **TTS_NODE_DISPLAY_NAME_MAPPINGS,
        **EFFECTS_NODE_DISPLAY_NAME_MAPPINGS,
    }

    print("Orpheus TTS and Audio Effects nodes loaded successfully")
except Exception as e:
    print(
        f"Warning: Audio Effects module could not be loaded, only TTS nodes will be available: {e}"
    )
    NODE_CLASS_MAPPINGS = TTS_NODE_CLASS_MAPPINGS
    NODE_DISPLAY_NAME_MAPPINGS = TTS_NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
