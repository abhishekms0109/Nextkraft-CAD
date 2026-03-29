"""Load calculate_parking from Function_Ref/Python_ref.py without package boilerplate."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    root = Path(__file__).resolve().parents[1]
    path = root / "Function_Ref" / "Python_ref.py"
    spec = importlib.util.spec_from_file_location("python_ref", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.calculate_parking


calculate_parking = _load()
