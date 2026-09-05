# SPDX-License-Identifier: GPL-3.0-or-later
"""ComfyUI-Lyra: Orpheus TTS 3B custom node.

Loaded by ComfyUI from custom_nodes/ComfyUI-Lyra/__init__.py.
"""

import os
import sys

# ComfyUI loads __init__.py directly via importlib without adding the node's
# directory to sys.path. Add it manually so lyra_nodes/ and core/ are importable.
_node_dir = os.path.dirname(os.path.abspath(__file__))
if _node_dir not in sys.path:
    sys.path.insert(0, _node_dir)

# Optional Hugging Face authentication — silently skipped if not configured
try:
    import hf_auth  # noqa: F401  # pyright: ignore[reportUnusedImport]
except Exception:
    pass

# Node registration — fails gracefully when runtime deps are absent
NODE_CLASS_MAPPINGS: dict = {}
NODE_DISPLAY_NAME_MAPPINGS: dict = {}

try:
    from lyra_nodes.generate import OrpheusTTSGenerate
    from lyra_nodes.loader import OrpheusTTSModelLoader

    NODE_CLASS_MAPPINGS.update(
        {
            "OrpheusTTSModelLoader": OrpheusTTSModelLoader,
            "OrpheusTTSGenerate": OrpheusTTSGenerate,
        }
    )
    NODE_DISPLAY_NAME_MAPPINGS.update(
        {
            "OrpheusTTSModelLoader": "Orpheus TTS Model Loader",
            "OrpheusTTSGenerate": "Orpheus TTS Generate",
        }
    )
except Exception:
    pass

try:
    from lyra_nodes.effects import LyraAudioEffects

    NODE_CLASS_MAPPINGS["LyraAudioEffects"] = LyraAudioEffects
    NODE_DISPLAY_NAME_MAPPINGS["LyraAudioEffects"] = "Lyra Audio Effects"
except Exception:
    pass

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
