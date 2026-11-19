#!/usr/bin/env python3
"""Compare RST structure markers between the English source and translation."""

from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
EN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/yosys-docs-src/docs/source")
ZH_ROOT = REPO / "docs" / "source"

PATTERNS = {
    "directive": re.compile(r"^[ \t]*\.\. [A-Za-z][A-Za-z0-9_-]*::", re.M),
    "label": re.compile(r"^[ \t]*\.\. _[^:]+:", re.M),
    "ref": re.compile(r":(?:ref|numref|doc|file|cmd|cell):", re.M),
    "code": re.compile(r"\.\. (?:code-block|literalinclude|sourcecode)::", re.M),
    "toctree": re.compile(r"\.\. toctree::", re.M),
    "image": re.compile(r"\.\. (?:image|figure)::", re.M),
}


def counts(text: str) -> dict[str, int]:
    return {name: len(pat.findall(text)) for name, pat in PATTERNS.items()}


def main() -> int:
    bad = 0
    for zh in sorted(ZH_ROOT.rglob("*.rst")):
        en = EN_ROOT / zh.relative_to(ZH_ROOT)
        if not en.exists():
            continue
        a = counts(en.read_text(encoding="utf-8"))
        b = counts(zh.read_text(encoding="utf-8"))
        diff = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
        if diff:
            bad += 1
            print(f"{zh.relative_to(REPO)}: " + ", ".join(f"{k} {x}->{y}" for k, (x, y) in diff.items()))
    print(f"{bad} file(s) with structural differences")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
