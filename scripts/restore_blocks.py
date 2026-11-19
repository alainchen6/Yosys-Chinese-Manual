#!/usr/bin/env python3
"""Restore literal/code block contents from the English source, robustly."""
from __future__ import annotations

import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
EN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/yosys-docs-src/docs/source")
ZH_ROOT = REPO / "docs" / "source"

DIR_RE = re.compile(r"^([ \t]*)\.\. (code-block|code|sourcecode|parsed-literal)::")
LIT_RE = re.compile(r"^(.*?)::\s*$")


def indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def extract(lines: list[str]) -> list[tuple[list[str], int, int, int]]:
    """Return (content lines, base indent, start index, end index)."""
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = DIR_RE.match(line)
        literal = None
        if m:
            base = len(m.group(1))
            if m.group(2) == "parsed-literal":
                literal = True
            else:
                literal = True
        else:
            lm = LIT_RE.match(line.rstrip("\n"))
            if lm and not line.lstrip().startswith("..") and not lm.group(1).strip().endswith("\\"):
                base = indent(line)
                literal = True
        if not literal:
            i += 1
            continue
        # skip directive options and blank lines
        j = i + 1
        while j < n:
            s = lines[j].strip()
            if not s:
                j += 1
                continue
            if s.startswith(":") and indent(lines[j]) > base:
                j += 1
                continue
            break
        start = j
        while j < n:
            if not lines[j].strip():
                j += 1
                continue
            if indent(lines[j]) <= base:
                break
            j += 1
        # trim trailing blank lines from content
        end = j
        while end > start and not lines[end - 1].strip():
            end -= 1
        if end > start:
            out.append((lines[start:end], base, start, end))
        i = max(j, i + 1)
    return out


def common_indent(content: list[str]) -> int:
    vals = [indent(l) for l in content if l.strip()]
    return min(vals) if vals else 0


def dedent(content: list[str]) -> list[str]:
    ci = common_indent(content)
    return [l[ci:] if l.strip() else "" for l in content]


def main() -> int:
    changed_files = 0
    changed_blocks = 0
    for zh in sorted(ZH_ROOT.rglob("*.rst")):
        en = EN_ROOT / zh.relative_to(ZH_ROOT)
        if not en.exists():
            continue
        en_lines = en.read_text(encoding="utf-8").splitlines(keepends=True)
        zh_lines = zh.read_text(encoding="utf-8").splitlines(keepends=True)
        en_blocks = extract(en_lines)
        zh_blocks = extract(zh_lines)
        if len(en_blocks) != len(zh_blocks):
            print(f"SKIP {zh.relative_to(REPO)}: {len(en_blocks)} vs {len(zh_blocks)} blocks")
            continue
        out = []
        cursor = 0
        for (en_content, _, _, _), (zh_content, base, start, end) in zip(en_blocks, zh_blocks):
            wanted = dedent(en_content)
            have = dedent(zh_content)
            if wanted == have:
                continue
            delta = common_indent(zh_content) - common_indent(en_content)
            replacement = []
            for line in en_content:
                if not line.strip():
                    replacement.append("\n")
                else:
                    replacement.append(" " * max(0, common_indent(zh_content)) + line[common_indent(en_content):])
            out.extend(zh_lines[cursor:start])
            out.extend(replacement)
            cursor = end
            changed_blocks += 1
        out.extend(zh_lines[cursor:])
        new = "".join(out)
        if new != "".join(zh_lines):
            zh.write_text(new, encoding="utf-8")
            changed_files += 1
            print("restored blocks in", zh.relative_to(REPO))
    print(f"{changed_files} file(s), {changed_blocks} block(s) restored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
