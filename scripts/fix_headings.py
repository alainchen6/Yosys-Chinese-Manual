#!/usr/bin/env python3
"""Pad RST heading underlines so they cover the heading's display width.

docutils compares the underline width with the title width, and East Asian
wide characters count as two columns.  Only top-level (unindented) headings
are touched, so literal blocks cannot be mistaken for headings.
"""
import sys
import unicodedata
from pathlib import Path

UNDER = set("=-~^\"'`#*+_:.")


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def fix(text: str) -> str:
    lines = text.splitlines(keepends=True)
    for i in range(len(lines) - 1):
        raw_title, raw_under = lines[i], lines[i + 1]
        title, under = raw_title.rstrip("\n"), raw_under.rstrip("\n")
        if not title or not under:
            continue
        if title[:1].isspace() or under[:1].isspace():
            continue
        if set(under) <= UNDER and under and len(under) < display_width(title):
            lines[i + 1] = under[0] * display_width(title) + "\n"
    return "".join(lines)


def main(paths):
    changed = 0
    for p in map(Path, paths):
        old = p.read_text(encoding="utf-8")
        new = fix(old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            changed += 1
            print("fixed", p)
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main(sys.argv[1:])
