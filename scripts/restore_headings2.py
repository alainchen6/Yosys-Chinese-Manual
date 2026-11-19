#!/usr/bin/env python3
"""Restore missing heading underlines by matching heading order.

For files where the number of plausible Chinese heading lines equals the number
of English headings, assign them in order and restore the expected underline.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unicodedata

REPO = pathlib.Path(__file__).resolve().parent.parent
EN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/yosys-docs-src/docs/source")
ZH_ROOT = REPO / "docs" / "source"

spec = importlib.util.spec_from_file_location("rb", REPO / "scripts" / "restore_blocks.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

UNDER = set("=-~^\"'`#*+_:.")


def width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text.strip())


def headings_en(lines: list[str]):
    out = []
    for i in range(len(lines) - 1):
        title, under = lines[i].strip(), lines[i + 1].strip()
        if (
            title
            and under
            and len(set(under)) == 1
            and under[0] in UNDER
            and len(under) >= len(title)
            and not lines[i].startswith((" ", "\t"))
        ):
            out.append((i, under[0]))
    return out


def candidates(lines: list[str]):
    blocks = [(s, e) for _, _, s, e in rb.extract([l + "\n" for l in lines])]
    out = []
    for i, raw in enumerate(lines):
        if not raw.strip() or raw[:1].isspace():
            continue
        if any(s <= i < e for s, e in blocks):
            continue
        text = raw.strip()
        if raw.lstrip().startswith(("..", ":", "-", "*", "#", "|", "+")):
            continue
        if len(text) > 42 or text[-1] in "。！？：；":
            continue
        prev = i == 0 or not lines[i - 1].strip()
        nxt = (
            i + 1 >= len(lines)
            or not lines[i + 1].strip()
            or (lines[i + 1].strip() and set(lines[i + 1].strip()) <= UNDER)
        )
        if prev and nxt:
            out.append((i, text))
    return out


def main() -> int:
    fixed = 0
    skipped = []
    for zh_path in sorted(ZH_ROOT.rglob("*.rst")):
        en_path = EN_ROOT / zh_path.relative_to(ZH_ROOT)
        if not en_path.exists():
            continue
        en = en_path.read_text(encoding="utf-8").splitlines()
        zh = zh_path.read_text(encoding="utf-8").splitlines()
        heads = headings_en(en)
        if not heads:
            continue
        cands = candidates(zh)
        if len(cands) != len(heads):
            skipped.append((zh_path.relative_to(REPO), len(heads), len(cands)))
            continue
        changes = []
        for (i, text), (_, ch) in zip(cands, heads):
            want = ch * width(text)
            if i + 1 < len(zh) and zh[i + 1].strip() and set(zh[i + 1].strip()) == {ch}:
                if zh[i + 1] != want:
                    changes.append((i + 1, want))
            else:
                changes.append((i + 1, want))
        for idx, line in sorted(changes, reverse=True):
            if idx < len(zh) and zh[idx].strip() and set(zh[idx].strip()) <= UNDER:
                zh[idx] = line
            else:
                zh.insert(idx, line)
            fixed += 1
        zh_path.write_text("\n".join(zh) + "\n", encoding="utf-8")
    print(f"restored/padded {fixed} heading(s)")
    for p, a, b in skipped:
        print(f"MANUAL {p}: {a} english headings vs {b} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
