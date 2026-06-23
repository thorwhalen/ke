"""Small, CLI-friendly functions over the ``ke`` core (the dispatch surface).

These are thin, string-in/value-out wrappers designed for triple dispatch (CLI via
``argh``, and later HTTP/UI). The single ``_dispatch_funcs`` list is the SSOT of
what :mod:`ke.__main__` exposes, so there is no duplicated command registration.

Run them from the shell::

    python -m ke cer "hello wrld" "hello world"
    python -m ke where
    python -m ke check tesseract
"""

from __future__ import annotations

from typing import Optional

from .facade import score
from .registry import check_requirements
from .stores import app_folder


def cer(prediction: str, gold: str, *, normalize: Optional[str] = None) -> float:
    """Character Error Rate between a prediction and a gold string (lower is better)."""
    return score(prediction, gold, metric="cer", normalize=normalize).value


def wer(prediction: str, gold: str, *, normalize: Optional[str] = None) -> float:
    """Word Error Rate between a prediction and a gold string (lower is better)."""
    return score(prediction, gold, metric="wer", normalize=normalize).value


def where() -> str:
    """Print the local data folder where ``ke`` persists gold/results/runs."""
    return str(app_folder())


def check(engine: str) -> dict:
    """Report what an OCR engine needs to run (delegates to ocracy when installed)."""
    return check_requirements(engine=engine)


def engines() -> list:
    """List installed OCR backends (requires the ``ke[ocr]`` extra)."""
    try:
        import ocracy

        return list(ocracy.available_backends())
    except ImportError:
        return ["(install ke[ocr] to list OCR backends)"]


def version() -> str:
    """Print the installed ``ke`` version."""
    from . import __version__

    return __version__


#: SSOT of the functions exposed by the ``ke`` CLI.
_dispatch_funcs = [cer, wer, where, check, engines, version]
