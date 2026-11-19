#!/usr/bin/env python3
"""Rewrite :ref:/:numref: targets after section headings were translated.

``autosectionlabel`` labels are derived from section titles, so translating a
heading changes the label other files reference. Pair the English and Chinese
headings in order (the translation preserves section order) and rewrite every
``doc:section title`` target to the translated title's normalized label.
"""

from __future__ import annotations

import pathlib
import re
import sys

from docutils import nodes

REPO = pathlib.Path(__file__).resolve().parent.parent
EN_ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/yosys-docs-src/docs/source")
ZH_ROOT = REPO / "docs" / "source"

UNDER = set("=-~^\"'`#*+_:.")
ROLE_RE = re.compile(r":(ref|numref):`([^`]+)`")
TARGET_RE = re.compile(r"^(?P<display>.*<)?(?P<target>[^<>]*?)(?P<close>>)?$", re.S)


def headings(path: pathlib.Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for i in range(len(lines) - 1):
        title, underline = lines[i].strip(), lines[i + 1].strip()
        if (
            title
            and underline
            and len(set(underline)) == 1
            and underline[0] in UNDER
            and len(underline) >= len(title)
        ):
            out.append(title)
    return out


def build_map() -> dict[str, tuple[str, str]]:
    mapping: dict[str, tuple[str, str]] = {}
    for zh in sorted(ZH_ROOT.rglob("*.rst")):
        rel = zh.relative_to(ZH_ROOT)
        en = EN_ROOT / rel
        if not en.exists():
            continue
        old_titles = headings(en)
        new_titles = headings(zh)
        if len(old_titles) != len(new_titles):
            print(f"SKIP {rel}: heading count {len(old_titles)} -> {len(new_titles)}")
            continue
        doc = rel.with_suffix("").as_posix()
        for old, new in zip(old_titles, new_titles):
            old_label = nodes.fully_normalize_name(f"{doc}:{old}")
            new_label = nodes.fully_normalize_name(f"{doc}:{new}")
            if old_label != new_label:
                mapping[old_label] = (old_label, new_label)
    return mapping


def main() -> int:
    mapping = build_map()
    changed = 0
    for zh in sorted(ZH_ROOT.rglob("*.rst")):
        text = zh.read_text(encoding="utf-8")

        def repl(m: re.Match[str]) -> str:
            role, inner = m.group(1), m.group(2)
            tm = TARGET_RE.match(inner)
            if not tm or tm.group("target") is None:
                return m.group(0)
            target = tm.group("target")
            normalized = nodes.fully_normalize_name(target)
            hit = mapping.get(normalized)
            if not hit:
                return m.group(0)
            nonlocal changed
            changed += 1
            display = tm.group("display")
            close = tm.group("close") or ""
            if display:
                return f":{role}:`{display}{hit[1]}{close}`"
            return f":{role}:`{hit[1]}`"

        new = ROLE_RE.sub(repl, text)
        if new != text:
            zh.write_text(new, encoding="utf-8")
            print("updated", zh.relative_to(REPO))
    print(f"rewrote {changed} reference(s) from {len(mapping)} translated section(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
