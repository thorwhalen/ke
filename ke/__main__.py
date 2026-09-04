# PYTHON_ARGCOMPLETE_OK
"""Command-line entry point for ``ke`` (``python -m ke`` / the ``ke`` script).

Commands come from :data:`ke.tools._dispatch_funcs` (the SSOT), dispatched with
``cw`` -- which reads each function's signature to build its flags -- and optionally
completed with ``argcomplete``. The ``# PYTHON_ARGCOMPLETE_OK`` marker on line 1
enables shell tab-completion (after the user activates it); ``cw.run`` is what offers
the parser to ``argcomplete``, at the same point ``argh`` used to.
"""

from __future__ import annotations

import argparse
from typing import Iterable, Mapping, Optional


def mk_parser(
    functions: Iterable, namespaced_funcs: Optional[Mapping[str, Iterable]] = None
) -> argparse.ArgumentParser:
    """Build a parser from top-level and namespaced functions. No parsing, no I/O.

    Returns a plain :class:`argparse.ArgumentParser`, which is what
    ``argcomplete.autocomplete`` is typed for.
    """
    import cw

    parser = cw.mk_parser(list(functions))
    for namespace, funcs in (namespaced_funcs or {}).items():
        cw.add_commands(parser, list(funcs), group_name=namespace)
    return parser


def dispatch_with_namespaces(
    functions: Iterable, namespaced_funcs: Optional[Mapping[str, Iterable]] = None
) -> int:
    """Dispatch top-level and namespaced functions; return the process exit code.

    Returning rather than raising is ``cw``'s contract, and the reason both callers
    below wrap it -- the console script in ``sys.exit``, the ``__main__`` guard in
    ``raise SystemExit``.
    """
    import cw

    return cw.run(mk_parser(functions, namespaced_funcs))


def main() -> int:
    """Entry point registered as the ``ke`` console script."""
    from . import tools

    return dispatch_with_namespaces(tools._dispatch_funcs)


if __name__ == "__main__":
    raise SystemExit(main())
