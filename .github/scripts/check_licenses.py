"""Fail the build if a copyleft / non-commercial license is in ke's dep closure.

ke has no dependencies since issue #12's reset (the package is reserved,
empty, pending a future knowledge-extraction build), so this gate currently
guards an empty closure. It is kept -- and fixed, not just left dormant --
so the first real dependency a future build adds is checked from day one.

Fixed here (was issue #17): the gate used to allow LGPL on the "acceptable
for a dynamically-linked library" argument, which does not describe a
pure-Python import -- `pip install` puts an LGPL package's source in the same
interpreter as ke's, and the relinking right LGPL trades for is meaningless
there. This mirrors ek's own resolution of the same disagreement (see ek's
`.github/scripts/check_licenses.py`): the whole GPL family -- GPL, AGPL and
LGPL -- is now a violation, matching `AGENTS.md`'s eventual licensing
policy for this repo (no copyleft, ever, as a default).

License terms in this ecosystem often live only in repo files (invisible to
PyPI metadata), so this scans the *resolved* install, not just declared
dependencies, and rejects:

- The whole GPL family (GPL / LGPL / AGPL), in every spelling seen in the
  wild -- "GPL" catches the abbreviations and classifier tails; "GENERAL
  PUBLIC" catches spelled-out names with no "GPL" substring (e.g. "GNU
  Lesser General Public License").
- Any non-commercial / source-available restriction (RAIL, CC-BY-NC, BUSL,
  SSPL, Elastic License, ...).

Usage:
    pip-licenses --format=csv --with-system > licenses.csv
    python .github/scripts/check_licenses.py licenses.csv

Exit code 1 (with the offending rows printed) on any violation.
"""

from __future__ import annotations

import csv
import sys

# Substrings that mark a forbidden license (matched case-insensitively). No LGPL
# escape hatch -- see the module docstring for why.
_GPL = ("GPL", "GENERAL PUBLIC")
_NON_COMMERCIAL = (
    "NON-COMMERCIAL",
    "NONCOMMERCIAL",
    "NON COMMERCIAL",
    "CC-BY-NC",
    "CC BY-NC",
    "RAIL",
    "BUSL",
    "BUSINESS SOURCE",
    "PROPRIETARY",
    "SSPL",
    "ELASTIC-2.0",
    "ELASTIC LICENSE",
    "ELASTICV2",
)

# Audited overrides go here as real dependencies land -- see ek's own script for
# the shape (name/prefix allowlists with a dated justification per entry). Empty
# for now: ke has no dependencies to audit.
_CLEARED: set[str] = set()


def _is_violation(license_text: str) -> str:
    """Return why ``license_text`` is forbidden, or ``""`` if it is acceptable.

    >>> _is_violation("MIT")
    ''
    >>> _is_violation("LGPL-3.0")
    'GPL/LGPL/AGPL copyleft'
    >>> _is_violation("GNU Affero General Public License v3")
    'GPL/LGPL/AGPL copyleft'
    >>> _is_violation("CC-BY-NC-4.0")
    'non-commercial / source-available'
    """
    up = license_text.upper()
    if any(nc in up for nc in _NON_COMMERCIAL):
        return "non-commercial / source-available"
    if any(g in up for g in _GPL):
        return "GPL/LGPL/AGPL copyleft"
    return ""


def main(path: str) -> int:
    violations = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("Name") or "").strip()
            license_text = (row.get("License") or "").strip()
            if name in _CLEARED:
                continue
            reason = _is_violation(license_text)
            if reason:
                violations.append((name, license_text, reason))

    if violations:
        print("License gate FAILED -- forbidden licenses in the dependency closure:")
        for name, lic, reason in violations:
            print(f"  - {name}: {lic}  [{reason}]")
        print(
            "\nCopyleft/non-commercial dependencies are never a default here -- "
            "see AGENTS.md."
        )
        return 1
    print(
        "License gate passed: no copyleft/non-commercial licenses in the closure."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "licenses.csv"))
