"""Compatibility shim for running src/aios without installing the package."""

from pathlib import Path

_SRC_AIOS = Path(__file__).resolve().parent.parent / "src" / "aios"
if _SRC_AIOS.is_dir():
    __path__.append(str(_SRC_AIOS))

