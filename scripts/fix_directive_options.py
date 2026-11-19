#!/usr/bin/env python3
"""Deduplicate directive option lines and keep a blank line before content."""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIR = re.compile(r"^([ \t]*)\.\. [A-Za-z][A-Za-z0-9_-]*::")
OPT = re.compile(r"^[ \t]+:(?P<key>[A-Za-z][A-Za-z0-9_-]*):")


def main(paths):
    changed = 0
    for p in map(Path, paths):
        lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
        out = []
        i = 0
        n = len(lines)
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
            seen = set()
            last_opt_idx = None
            # consume option lines, allowing blank lines between duplicated option groups
            while i < n:
                s = lines[i].strip()
                opt = OPT.match(lines[i])
                if opt and len(lines[i]) - len(lines[i].lstrip(" \t")) > base:
                    key = opt.group("key")
                    if key not in seen:
                        seen.add(key)
                        out.append(lines[i])
                        last_opt_idx = len(out) - 1
                    i += 1
                    continue
                if not s:
                    # look ahead: if the next non-blank is another option, skip this blank
                    j = i + 1
                    while j < n and not lines[j].strip():
                        j += 1
                    if j < n and OPT.match(lines[j]) and len(lines[j]) - len(lines[j].lstrip(" \t")) > base:
                        i += 1
                        continue
                break
            if last_opt_idx is not None and i < n and lines[i].strip():
                out.append("\n")
            continue
        new = "".join(out)
        if new != "".join(lines):
            p.write_text(new, encoding="utf-8")
            changed += 1
            print("fixed options in", p)
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main(sys.argv[1:])
