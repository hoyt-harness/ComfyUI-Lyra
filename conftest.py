# SPDX-License-Identifier: GPL-3.0-or-later
"""Pytest root conftest — ensures core/ and nodes/ are importable without
loading the ComfyUI plugin entry point (__init__.py).

ComfyUI custom nodes use relative imports in __init__.py that fail outside
a ComfyUI runtime. This conftest adds the repo root to sys.path directly so
pytest can import core.* and nodes.* as top-level packages.
"""

import sys
from pathlib import Path

# Insert repo root first so 'core', 'nodes', 'tests' resolve directly.
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
