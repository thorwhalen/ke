"""Characterization tests pinning the ``ke`` command-line grammar.

Recorded from the pre-migration ``argh`` implementation and replayed against
:mod:`cw`. Beyond the usual help/usage surface, three things here are load-bearing
and nothing else in the suite covers them:

* **egress** — ``cer``/``wer`` return floats, ``version`` a string, ``engines`` a list
  and ``check`` a dict, and the CLI is what prints them. Diffing only ``--help`` would
  miss a printing regression entirely;
* the **exit code**, which ``cw.run`` *returns* where ``argh`` raised it, so both
  entry points have to forward it;
* the **namespaced** dispatch path, which was silently broken under ``argh >= 0.30``
  (see :func:`test_a_namespace_group_actually_works_now`).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

import pytest

from ke import tools
from ke.__main__ import dispatch_with_namespaces, main, mk_parser

COMMANDS = ("cer", "wer", "where", "check", "engines", "version")


@pytest.fixture(scope="module")
def parser():
    """The very parser :func:`ke.__main__.main` dispatches, built without I/O.

    ``sys.argv[0]`` is pinned because argparse derives ``prog`` from it at
    construction time, and this suite asserts on usage lines.
    """
    argv = sys.argv
    sys.argv = ["ke"]
    try:
        return mk_parser(tools._dispatch_funcs)
    finally:
        sys.argv = argv


@pytest.fixture(scope="module")
def subparsers(parser):
    action = next(
        a for a in parser._actions if isinstance(a, argparse._SubParsersAction)
    )
    return action.choices


def _run(*argv):
    """Run ``python -m ke ARGV`` end to end."""
    env = {k: v for k, v in os.environ.items() if k != "COLUMNS"}
    return subprocess.run(
        [sys.executable, "-m", "ke", *argv],
        capture_output=True,
        text=True,
        env={"COLUMNS": "80", **env},
    )


# --------------------------------------------------------------------------- grammar


def test_the_dispatch_funcs_ssot_is_what_reaches_the_parser(parser, subparsers):
    """``tools._dispatch_funcs`` is the SSOT; this is what stops it drifting."""
    assert [f.__name__ for f in tools._dispatch_funcs] == list(COMMANDS)
    assert tuple(subparsers) == COMMANDS
    assert parser.format_usage() == (
        "usage: ke [-h] {cer,wer,where,check,engines,version} ...\n"
    )


@pytest.mark.parametrize(
    "command, usage",
    [
        ("cer", "usage: ke cer [-h] [-n NORMALIZE] prediction gold"),
        ("wer", "usage: ke wer [-h] [-n NORMALIZE] prediction gold"),
        ("where", "usage: ke where [-h]"),
        ("check", "usage: ke check [-h] engine"),
        ("engines", "usage: ke engines [-h]"),
        ("version", "usage: ke version [-h]"),
    ],
)
def test_each_subcommand_keeps_its_recorded_usage_line(subparsers, command, usage):
    """Flag spellings and positionals, exactly as argh rendered them.

    Line wrapping is normalised away -- it depends on the terminal width the test
    happens to run under.
    """
    assert " ".join(subparsers[command].format_usage().split()) == usage


def test_normalize_is_an_option_with_a_none_default(subparsers):
    assert subparsers["cer"].parse_args(["a", "b"]).normalize is None
    assert subparsers["cer"].parse_args(["a", "b", "-n", "lower"]).normalize == "lower"


# ---------------------------------------------------------------------------- egress


@pytest.mark.parametrize(
    "argv, expected",
    [
        (("cer", "hello wrld", "hello world"), "0.09090909090909091"),
        (("wer", "hello wrld", "hello world"), "0.5"),
        (("version",), tools.version()),
    ],
)
def test_return_values_are_printed(argv, expected):
    """The wrappers *return*; the CLI prints. A regression here is invisible to --help."""
    done = _run(*argv)
    assert done.returncode == 0
    assert done.stdout.strip() == expected


def test_a_list_return_prints_one_line_per_item():
    """argh's type whitelist: a list is lines, not its ``repr``. cw reproduces it."""
    done = _run("engines")
    assert done.returncode == 0
    assert done.stdout.splitlines() == tools.engines()


def test_a_dict_return_prints_as_one_str_line():
    """The other half of the whitelist: a dict is *not* iterated -- it is ``str``'d."""
    done = _run("check", "tesseract")
    assert done.returncode == 0
    assert done.stdout.strip() == str(tools.check("tesseract"))


# ------------------------------------------------------------------------ exit codes


def test_no_arguments_prints_usage_to_stdout_and_exits_zero():
    """argh's behaviour, which bare argparse does not reproduce. Pinned deliberately."""
    done = _run()
    assert done.returncode == 0
    assert done.stdout.startswith("usage: ")
    assert done.stderr == ""


@pytest.mark.parametrize(
    "argv",
    [
        ("no-such-command",),
        ("cer",),  # both positionals missing
        ("cer", "only-one"),  # one positional missing
        ("check",),  # positional missing
    ],
)
def test_bad_invocations_exit_two(argv):
    done = _run(*argv)
    assert done.returncode == 2
    assert done.stdout == ""
    assert done.stderr.startswith("usage: ")


def test_main_returns_the_exit_code_rather_than_swallowing_it(monkeypatch):
    """``main()`` yields an int, not ``None``.

    That is what makes ``raise SystemExit(main())`` in ``__main__`` -- and the console
    script's own ``sys.exit(main())`` -- report a failure instead of success.
    """
    monkeypatch.setattr(sys, "argv", ["ke", "no-such-command"])
    assert main() == 2
    monkeypatch.setattr(sys, "argv", ["ke", "version"])
    assert main() == 0


# ------------------------------------------------------------------------ namespaces


def test_a_namespace_group_actually_works_now(capsys, monkeypatch):
    """``dispatch_with_namespaces``' second argument was dead code under ``argh``.

    ``argh >= 0.30`` renamed ``add_commands``' ``namespace=`` keyword to ``group_name=``
    with no alias, so the loop body raised ``TypeError`` for anyone who ever passed
    ``namespaced_funcs``. Nothing in the package did, which is why it went unnoticed.
    ``cw.add_commands`` accepts both spellings, so the documented contract is real
    again -- this test is what keeps it that way.
    """

    def alpha(value: str):
        """A command that only exists under a namespace."""
        return f"alpha:{value}"

    monkeypatch.setattr(sys, "argv", ["ke", "extra", "alpha", "x"])
    assert dispatch_with_namespaces(tools._dispatch_funcs, {"extra": [alpha]}) == 0
    assert capsys.readouterr().out.strip() == "alpha:x"

    parser = mk_parser(tools._dispatch_funcs, {"extra": [alpha]})
    assert "extra" in " ".join(parser.format_usage().split())
