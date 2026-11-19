#!/usr/bin/env python3
"""Remove blank lines between a directive's option lines; keep one blank after."""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIR = re.compile(r"^([ \t]*)\.\. [A-Za-z][A-Za-z0-9_-]*::")
OPT = re.compile(r"^[ \t]+:(?P<key>[A-Za-z][A-Za-z0-9_-]*):")
KEYS = {
    "name", "class", "alt", "align", "height", "width", "scale", "target",
    "caption", "figwidth", "figclass", "language", "linenos", "lineno-start",
    "emphasize-lines", "dedent", "start-at", "start-after", "end-before",
    "end-at", "lines", "number-lines", "force", "encoding", "tab-width", "lineno-match", "prepend", "append", "diff", "stub-columns", "widths", "width", "class", "align",
    "pyobject", "only", "hide", "include", "literal", "download",
    "maxdepth", "titlesonly", "includehidden", "glob", "reversed", "numbered",
    "hidden",
}


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
            # find the first non-blank line after the directive
            k = i
            while k < n and not lines[k].strip():
                k += 1
            if k >= n:
                i = k
                continue
            om = OPT.match(lines[k])
            if not (om and om.group("key") in KEYS and len(lines[k]) - len(lines[k].lstrip(" \t")) > base):
                # no options: leave the original lines untouched
                continue
            options = []
            seen = set()
            j = i
            while j < n:
                if not lines[j].strip():
                    j += 1
                    continue
                om2 = OPT.match(lines[j])
                if om2 and om2.group("key") in KEYS and len(lines[j]) - len(lines[j].lstrip(" \t")) > base:
                    key = om2.group("key")
                    if key not in seen:
                        seen.add(key)
                        options.append(lines[j])
                    j += 1
                    continue
                break
            out.extend(options)
            if j < n:
                out.append("\n")
            i = j
        new = "".join(out)
        if new != "".join(lines):
            p.write_text(new, encoding="utf-8")
            changed += 1
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    main(sys.argv[1:])
