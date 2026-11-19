#!/usr/bin/env python3
"""Ensure a blank line between directive options and the directive's content."""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIR = re.compile(r"^([ \t]*)\.\. [A-Za-z][A-Za-z0-9_-]*::")
OPT = re.compile(r"^[ \t]+:(?P<key>[A-Za-z][A-Za-z0-9_-]*):\s*")
KEYS = {
    "name", "class", "alt", "align", "height", "width", "scale", "target",
    "caption", "figwidth", "figclass", "language", "linenos", "lineno-start",
    "emphasize-lines", "dedent", "start-at", "start-after", "end-before",
    "end-at", "lines", "number-lines", "force", "encoding", "tab-width",
    "pyobject", "only", "hide", "include", "literal", "download",
}


def main(paths):
    changed = 0
    for p in map(Path, paths):
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        out = []
        i = 0
        n = len(lines)
        dirty = False
        while i < n:
            line = lines[i]
            m = DIR.match(line)
            if not m:
                out.append(line)
                i += 1
                continue
            base = len(m.group(1))
            out.append(line)
            i += 1
            last_opt = False
            while i < n:
                om = OPT.match(lines[i])
                if om and om.group("key") in KEYS and len(lines[i]) - len(lines[i].lstrip(" \t")) > base:
                    out.append(lines[i])
                    last_opt = True
                    i += 1
                    continue
                break
            if last_opt and i < n and lines[i].strip():
                out.append("\n")
                dirty = True
        new = "".join(out)
        if new != "".join(lines):
            p.write_text(new, encoding="utf-8")
            changed += 1
            print("fixed blanks in", p)
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main(sys.argv[1:])
