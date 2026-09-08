"""Locates and imports the compiled catchup_engine backend module."""

import sys
from pathlib import Path

_BUILD_ENGINE_DIR = Path(__file__).resolve().parents[1] / "build" / "engine"
if str(_BUILD_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_BUILD_ENGINE_DIR))

import catchup_engine 

__all__ = ["catchup_engine"]
