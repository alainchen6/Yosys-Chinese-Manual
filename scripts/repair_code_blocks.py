#!/usr/bin/env python3
"""Restore literal blocks from the English source after translation.

Translations must keep every code/literal block byte-identical.  If a block in
the translated file differs from the English source, copy the English block
back (translated prose is untouched).
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
EN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/yosys-docs-src/docs/source")
ZH_ROOT = REPO / "docs" / "source"

DIRECTIVE = ("code-block", "code", "sourcecode", "literalinclude", "parsed-literal")


def extract_blocks(lines: list[str]) -> list[list[str]]:
    blocks: list[list[str]] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.rstrip()
        is_directive = any(stripped.lstrip().startswith(f".. {d}::") for d in DIRECTIVE)
        is_literal = stripped.endswith("::") and not stripped.lstrip().startswith("..")
        if is_directive or is_literal:
            base = len(line) - len(line.lstrip(" "))
            j = i + 1
            # skip directive options / blank lines until the first indented line
            while j < n and (not lines[j].strip() or lines[j].startswith(" " * (base + 1)) is False and lines[j].strip().startswith(":")):
                j += 1
            # real content starts at the first line indented deeper than base
            while j < n and not lines[j].strip():
                j += 1
            start = j
            while j < n:
                if not lines[j].strip():
                    j += 1
                    continue
                indent = len(lines[j]) - len(lines[j].lstrip(" "))
                if indent <= base:
                    break
                j += 1
            if start < j:
                blocks.append(lines[start:j])
            i = j
            continue
        i += 1
    return blocks


def main() -> int:
    changed = 0
    for zh in sorted(ZH_ROOT.rglob("*.rst")):
        en = EN_ROOT / zh.relative_to(ZH_ROOT)
        if not en.exists():
            continue
        en_lines = en.read_text(encoding="utf-8").splitlines(keepends=True)
        zh_lines = zh.read_text(encoding="utf-8").splitlines(keepends=True)
        en_blocks = extract_blocks(en_lines)
        zh_blocks = extract_blocks(zh_lines)
        if len(en_blocks) != len(zh_blocks):
            print(f"SKIP {zh.relative_to(REPO)}: block count {len(en_blocks)}->{len(zh_blocks)}")
            continue
        # walk through the Chinese file and replace mismatching blocks in place
        idx = 0
        out: list[str] = []
        i = 0
        n = len(zh_lines)
        while i < n:
            line = zh_lines[i]
            stripped = line.rstrip()
            is_directive = any(stripped.lstrip().startswith(f".. {d}::") for d in DIRECTIVE)
            is_literal = stripped.endswith("::") and not stripped.lstrip().startswith("..")
            if is_directive or is_literal:
                base = len(line) - len(line.lstrip(" "))
                j = i + 1
                while j < n and (not zh_lines[j].strip() or (zh_lines[j].strip().startswith(":") and len(zh_lines[j]) - len(zh_lines[j].lstrip(" ")) > base)):
                    j += 1
                while j < n and not zh_lines[j].strip():
                    j += 1
                start = j
                while j < n:
                    if not zh_lines[j].strip():
                        j += 1
                        continue
                    indent = len(zh_lines[j]) - len(zh_lines[j].lstrip(" "))
                    if indent <= base:
                        break
                    j += 1
                if start < j and idx < len(en_blocks):
                    candidate = zh_lines[start:j]
                    if candidate != en_blocks[idx]:
                        out.extend(zh_lines[i:start])
                        out.extend(en_blocks[idx])
                        i = j
                        idx += 1
                        changed += 1
                        continue
                idx += 1
            out.append(line)
            i += 1
        new = "".join(out)
        if new != "".join(zh_lines):
            zh.write_text(new, encoding="utf-8")
            print("repaired", zh.relative_to(REPO))
    print(f"{changed} literal block(s) restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
