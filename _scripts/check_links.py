"""Verify every link in the vault resolves, and that none are GitHub-broken.

    uv run python _scripts/check_links.py

Checks three things across all markdown files:

  1. Markdown link targets exist          [text](path.md)
  2. Heading anchors exist in the target  [text](path.md#some-heading)
  3. Image sources exist                  <img src="...">

and flags any leftover Obsidian [[wikilinks]] or ![[embeds]]. Those render fine
in Obsidian but appear as literal brackets on GitHub, so the vault uses plain
markdown links, which both understand.

Exits non-zero if anything is broken.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

FENCE = re.compile(r"^```.*?^```", re.S | re.M)
INLINE = re.compile(r"`[^`\n]*`")
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
IMG_SRC = re.compile(r'<img\s[^>]*src="([^"]+)"')
WIKI = re.compile(r"!?\[\[[^\]]+\]\]")


def strip_code(text: str) -> str:
    """Blank out code so examples inside it are not treated as real links."""
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return INLINE.sub("", text)


def anchors(path: pathlib.Path) -> set[str]:
    """GitHub-style slugs for every heading in a file.

    Only fenced blocks are removed here, not inline code: a heading like
    ``## The `.env` file`` still anchors as `the-env-file`, so stripping code
    spans first would invent a slug GitHub never generates.
    """
    found = set()
    body = FENCE.sub("", path.read_text(encoding="utf-8"))
    for line in body.splitlines():
        if line.startswith("#"):
            h = line.lstrip("#").strip().lower().replace("`", "")
            h = re.sub(r"[^\w\s-]", "", h)
            found.add(re.sub(r"\s+", "-", h))
    return found


def main() -> int:
    notes = [p for p in ROOT.rglob("*.md") if ".venv" not in p.parts]
    problems: list[str] = []
    checked = 0

    for p in notes:
        body = strip_code(p.read_text(encoding="utf-8"))
        where = p.relative_to(ROOT)

        for stray in WIKI.findall(body):
            problems.append(f"{where}: wikilink will not render on GitHub: {stray}")

        for target in MD_LINK.findall(body):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            checked += 1
            file_part, _, anchor = target.partition("#")
            dest = (p.parent / file_part).resolve() if file_part else p
            if not dest.exists():
                problems.append(f"{where}: missing target {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                problems.append(f"{where}: no heading '{anchor}' in {file_part}")

        for src in IMG_SRC.findall(body):
            checked += 1
            if not (p.parent / src).exists():
                problems.append(f"{where}: missing image {src}")

    for msg in problems:
        print(f"  {msg}")
    print(f"{len(notes)} files, {checked} links checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
