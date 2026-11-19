#!/usr/bin/env python3
"""Restore heading underlines removed by an earlier cleanup script.

Uses exact-line anchors (code blocks, directives, blank lines) to map each
English heading to its translated title, then inserts the same underline level
with the translated title's display width.
"""
from __future__ import annotations

import difflib
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


def english_headings(lines: list[str]):
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
            out.append((i, title, under[0]))
    return out


def main() -> int:
    restored = 0
    missing = 0
    for zh_path in sorted(ZH_ROOT.rglob("*.rst")):
        en_path = EN_ROOT / zh_path.relative_to(ZH_ROOT)
        if not en_path.exists():
            continue
        en = en_path.read_text(encoding="utf-8").splitlines()
        zh = zh_path.read_text(encoding="utf-8").splitlines()
        heads = english_headings(en)
        if not heads:
            continue
        # blocks in the Chinese file: never pick a title inside one
        block_ranges = [(s, e) for _, _, s, e in rb.extract([l + "\n" for l in zh])]
        def in_block(i: int) -> bool:
            return any(s <= i < e for s, e in block_ranges)

        sm = difflib.SequenceMatcher(None, en, zh, autojunk=False)
        matches = [b for b in sm.get_matching_blocks() if b.size > 0]
        inserts = []  # (index after which to insert, underline char, title text)
        for e, title, ch in heads:
            prev = max((b for b in matches if b.a <= e), key=lambda b: b.a, default=None)
            nxt = min((b for b in matches if b.a > e + 1), key=lambda b: b.a, default=None)
            lo = prev.b + prev.size if prev else 0
            hi = nxt.b if nxt else len(zh)
            cands = []
            for i in range(lo, hi):
                if not zh[i].strip() or in_block(i):
                    continue
                if zh[i].lstrip().startswith(("..", ":", "-", "*", "#", "|")):
                    continue
                before_blank = i == 0 or not zh[i - 1].strip()
                after_blank = i + 1 >= len(zh) or not zh[i + 1].strip()
                if before_blank and after_blank:
                    cands.append(i)
            if not cands:
                missing += 1
                continue
            # heading is the first blank-surrounded line after the previous anchor
            idx = cands[0]
            inserts.append((idx, ch, zh[idx]))
        # apply from bottom to top
        for idx, ch, title in sorted(inserts, reverse=True):
            # skip if an underline already follows
            if idx + 1 < len(zh) and zh[idx + 1].strip() and set(zh[idx + 1].strip()) == {ch}:
                continue
            zh.insert(idx + 1, ch * width(title))
            restored += 1
        new = "\n".join(zh) + ("\n" if zh_path.read_text(encoding="utf-8").endswith("\n") else "")
        zh_path.write_text(new, encoding="utf-8")
    print(f"restored {restored} heading underline(s); {missing} heading(s) not located")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
