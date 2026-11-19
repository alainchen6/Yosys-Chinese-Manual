#!/usr/bin/env python3
"""Insert underlines for the few files where automatic heading matching was ambiguous."""
from __future__ import annotations

import pathlib
import unicodedata

REPO = pathlib.Path(__file__).resolve().parent.parent
ROOT = REPO / "docs" / "source"

# file -> [(1-based title line, underline char), ...]
PLAN = {
    "appendix/auxlibs.rst": [(1, "="), (7, "-"), (18, "-"), (26, "-"), (33, "-"), (42, "-"), (55, "-"), (60, "-"), (69, "-")],
    "cmd/index_other.rst": [(3, "=")],
    "cmd/index_techlibs_intel_alm.rst": [(1, "-")],
    "using_yosys/bugpoint.rst": [(1, "="), (18, "-"), (52, "-"), (65, "~"), (116, "~"), (195, "~"), (226, "-"), (247, "~"), (289, "~"), (306, "~"), (352, "-")],
    "using_yosys/pyosys.rst": [(1, "="), (25, "-"), (56, "-"), (132, "-"), (207, "-")],
    "using_yosys/synthesis/extract.rst": [(1, "-"), (66, "~"), (87, "~")],
    "using_yosys/synthesis/fsm.rst": [(1, "="), (18, "~"), (40, "~"), (91, "~"), (111, "~")],
    "yosys_internals/extending_yosys/contributing.rst": [(1, "="), (5, "-"), (13, "-"), (21, "~"), (36, "~"), (100, "~"), (112, "~"), (134, "~"), (167, "-"), (171, "~"), (191, "~"), (229, "~"), (239, "~"), (271, "~"), (292, "~"), (310, "~"), (323, "-"), (328, "~"), (357, "~")],
    "yosys_internals/idstring.rst": [(1, "-"), (4, "~"), (45, "~"), (49, "^"), (72, "^"), (158, "^"), (200, "^")],
}


def width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text.strip())


def main() -> int:
    n = 0
    for rel, plan in PLAN.items():
        p = ROOT / rel
        lines = p.read_text(encoding="utf-8").splitlines()
        for line_no, ch in sorted(plan, reverse=True):
            idx = line_no - 1
            title = lines[idx]
            underline = ch * width(title)
            if idx + 1 < len(lines) and lines[idx + 1].strip() and set(lines[idx + 1].strip()) <= set("=-~^\"'`#*+_:."):
                lines[idx + 1] = underline
            else:
                lines.insert(idx + 1, underline)
            n += 1
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"inserted {n} heading underlines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
