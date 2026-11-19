#!/usr/bin/env python3
"""Ensure a directive line is followed by options or a blank line, never raw content."""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIR = re.compile(r"^([ \t]*)\.\. [A-Za-z][A-Za-z0-9_-]*::")
OPT = re.compile(r"^[ \t]+:[A-Za-z][A-Za-z0-9_-]*:")


def main(paths):
    changed = 0
    for p in map(Path, paths):
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        out = []
        i = 0
        n = len(lines)
        while i < n:
            out.append(lines[i])
            if not DIR.match(lines[i]):
                i += 1
                continue
            i += 1
            # skip any immediate option lines
            while i < n and OPT.match(lines[i]):
                out.append(lines[i])
                i += 1
            # if the next line is blank we are fine; otherwise insert one
            if i < n and lines[i].strip():
                out.append("\n")
        new = "".join(out)
        if new != "".join(lines):
            p.write_text(new, encoding="utf-8")
            changed += 1
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main(sys.argv[1:])
