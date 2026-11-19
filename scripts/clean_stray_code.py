#!/usr/bin/env python3
"""Remove code fragments left outside literal blocks by an earlier bad edit."""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
EN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/yosys-docs-src/docs/source")
ZH_ROOT = REPO / "docs" / "source"

spec = importlib.util.spec_from_file_location("restore", REPO / "scripts" / "restore_blocks.py")
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)

PUNCT_ONLY = re.compile(r"^[`~\"'.=_*+#-]{3,}$")


def main() -> int:
    changed = 0
    for zh in sorted(ZH_ROOT.rglob("*.rst")):
        en = EN_ROOT / zh.relative_to(ZH_ROOT)
        if not en.exists():
            continue
        en_lines = en.read_text(encoding="utf-8").splitlines(keepends=True)
        zh_lines = zh.read_text(encoding="utf-8").splitlines(keepends=True)
        en_blocks = restore.extract(en_lines)
        zh_blocks = restore.extract(zh_lines)
        if len(en_blocks) != len(zh_blocks):
            continue
        code_lines = set()
        for content, _, _, _ in en_blocks:
            for line in restore.dedent(content):
                s = line.strip()
                if s:
                    code_lines.add(s)
        inside = [False] * len(zh_lines)
        for _, _, start, end in zh_blocks:
            for i in range(start, end):
                inside[i] = True
        out = []
        removed = 0
        for i, line in enumerate(zh_lines):
            if inside[i]:
                out.append(line)
                continue
            s = line.strip()
            if not s:
                out.append(line)
                continue
            if PUNCT_ONLY.match(s) or s in code_lines:
                removed += 1
                out.append("\n")
                continue
            out.append(line)
        # collapse runs of 3+ blank lines
        cleaned = []
        blanks = 0
        for line in out:
            if not line.strip():
                blanks += 1
                if blanks <= 2:
                    cleaned.append(line)
            else:
                blanks = 0
                cleaned.append(line)
        new = "".join(cleaned)
        if new != "".join(zh_lines):
            zh.write_text(new, encoding="utf-8")
            print(f"cleaned {zh.relative_to(REPO)}: {removed} stray line(s)")
            changed += 1
    print(f"{changed} file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
