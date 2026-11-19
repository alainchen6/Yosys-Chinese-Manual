#!/usr/bin/env python3
"""Remove underlines that were inserted under ordinary prose lines."""
from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZH = ROOT / "docs" / "source"
EN_ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/yosys-docs-src/docs/source")
UNDER = set("=-~^\"'`#*+_:.")


def heading_indices(lines):
    out = []
    for i in range(len(lines) - 1):
        t, u = lines[i].strip(), lines[i + 1].strip()
        if t and u and len(set(u)) == 1 and u[0] in UNDER and len(u) >= len(t) and not lines[i].startswith((" ", "\t")):
            out.append(i)
    return out


def english_count(p):
    lines = p.read_text(encoding="utf-8").splitlines()
    return len(heading_indices(lines))


def main():
    changed = 0
    for p in ZH.rglob("*.rst"):
        en = EN_ROOT / p.relative_to(ZH)
        if not en.exists():
            continue
        want = english_count(en)
        lines = p.read_text(encoding="utf-8").splitlines()
        heads = heading_indices(lines)
        extra = len(heads) - want
        if extra <= 0:
            continue
        candidates = []
        for i in heads:
            title = lines[i].strip()
            score = 0
            if title.endswith(("。", "：", "；")):
                score += 3
            if "。" in title:
                score += 2
            if len(title) > 32:
                score += 2
            if score:
                candidates.append((score, len(title), i))
        candidates.sort(reverse=True)
        remove = {i + 1 for _, _, i in candidates[:extra]}
        if len(remove) < extra:
            print(f"MANUAL {p.relative_to(ROOT)}: need {extra}, found {len(remove)} prose candidates")
            continue
        lines = [line for i, line in enumerate(lines) if i not in remove]
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        changed += 1
        print(f"trimmed {extra} in {p.relative_to(ROOT)}")
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main()
