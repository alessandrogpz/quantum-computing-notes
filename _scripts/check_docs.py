"""Verify COMMANDS.md still matches the code.

    uv run python _scripts/check_docs.py

Documentation goes stale silently: a flag gets renamed, a default changes, a
script moves, and the docs keep confidently describing the old thing. This
compares COMMANDS.md against the actual argparse definitions and fails if they
have diverged.

Three checks:

  1. Every flag documented for a script really exists on it.
  2. Every flag a script has is documented.
  3. Every default stated in the docs matches the parser's real default.

Then, for credentials: the .env variable names in ibm_account.py, .env.example and
the COMMANDS.md table must all agree, and anything the code requires must be
documented as required. Someone setting up a new machine has only the docs to go
on, so a variable named inconsistently there is a setup that silently fails.

Plus: every `uv run python <path>` command anywhere in the docs points at a file
that exists.

Exits non-zero on any mismatch. The scripts expose build_parser() for this.
"""

import argparse
import pathlib
import re
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "COMMANDS.md"

# Scripts whose flags COMMANDS.md documents, in the order they appear there.
DOCUMENTED = (
    "03_Protocols/bb84.py",
    "03_Protocols/bb84_ibm.py",
    "03_Protocols/e91.py",
    "03_Protocols/e91_ibm.py",
    "04_Algorithms/shors_15.py",
    "04_Algorithms/shors_15_ibm.py",
    "_scripts/build_figures.py",
)


def load_module(rel: str) -> types.ModuleType:
    """Compile the script from source, never from __pycache__.

    importlib will happily reuse a stale .pyc when a file is rewritten inside the
    same mtime tick, which for a checker is the worst possible failure: it
    validates the docs against code that is no longer there. Reading and
    compiling the source directly removes that whole class of wrongness.
    """
    path = ROOT / rel
    sys.path.insert(0, str(path.parent))
    module = types.ModuleType(path.stem)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


def load_parser(rel: str) -> argparse.ArgumentParser:
    return load_module(rel).build_parser()


def real_flags(parser: argparse.ArgumentParser) -> dict[str, object]:
    """Flag -> default, skipping --help."""
    out = {}
    for action in parser._actions:
        for opt in action.option_strings:
            if opt.startswith("--") and opt != "--help":
                out[opt] = action.default
    return out


def documented_section(text: str, rel: str) -> str:
    """The chunk of COMMANDS.md describing one script."""
    head = f"## `{rel}`"
    if head not in text:
        return ""
    rest = text.split(head, 1)[1]
    return rest.split("\n---", 1)[0]


# Values in the Default column that mean "no fixed default worth checking".
UNCHECKED = {"", "—", "-", "off", "all", "least busy", "none"}


def documented_flags(section: str) -> dict[str, str | None]:
    """Flag -> stated default, from the flag table.

    A script's section may contain more than one table (e.g. the --counting
    trade-off table), and a later one can repeat a flag in its header. The flag
    table always comes first, so the first mention of each flag wins.
    """
    out: dict[str, str | None] = {}
    for flag, default in re.findall(r"^\|\s*`(--[a-z-]+)[^`]*`\s*\|([^|]*)\|", section, re.M):
        if flag in out:
            continue
        d = default.strip().strip("`*").strip()
        out[flag] = None if d.lower() in UNCHECKED else d
    return out


def main() -> int:
    text = DOC.read_text(encoding="utf-8")
    problems: list[str] = []
    checked = 0

    for rel in DOCUMENTED:
        section = documented_section(text, rel)
        if not section:
            problems.append(f"{rel}: no `## \\`{rel}\\`` section in COMMANDS.md")
            continue

        real = real_flags(load_parser(rel))
        doc = documented_flags(section)
        checked += len(real)

        for flag in doc.keys() - real.keys():
            problems.append(f"{rel}: COMMANDS.md documents {flag}, which does not exist")
        for flag in real.keys() - doc.keys():
            problems.append(f"{rel}: {flag} exists but is not documented")

        for flag in real.keys() & doc.keys():
            stated, actual = doc[flag], real[flag]
            if stated is None or actual is None:
                continue
            if str(actual) != stated.strip("'\""):
                problems.append(
                    f"{rel}: {flag} documented default {stated!r}, actually {actual!r}"
                )

    # The .env variable names live in three places: the loader's REQUIRED and
    # OPTIONAL tuples, the .env.example template, and the COMMANDS.md table.
    # All three must agree, or someone setting up a new machine is misled.
    loader = load_module("_scripts/ibm_account.py")
    code_vars = set(loader.REQUIRED) | set(loader.OPTIONAL)
    example_vars = set(re.findall(r"^([A-Z][A-Z_]*)=", (ROOT / ".env.example").read_text(encoding="utf-8"), re.M))
    doc_vars = set(re.findall(r"^\|\s*`([A-Z][A-Z_]*)`\s*\|", text, re.M))
    checked += len(code_vars)

    for name, found in ((".env.example", example_vars), ("COMMANDS.md", doc_vars)):
        for var in code_vars - found:
            problems.append(f"{name}: missing env var {var}, which ibm_account.py expects")
        for var in found - code_vars:
            problems.append(f"{name}: documents env var {var}, which ibm_account.py ignores")

    for var in loader.REQUIRED:
        row = re.search(rf"^\|\s*`{var}`\s*\|([^|]*)\|", text, re.M)
        if row and "yes" not in row.group(1).lower():
            problems.append(f"COMMANDS.md: {var} is required by the code but not marked required")

    # Any command shown in any doc must point at a file that exists.
    for md in ROOT.glob("*.md"):
        for path in re.findall(r"uv run python (\S+\.py)", md.read_text(encoding="utf-8")):
            checked += 1
            if not (ROOT / path).exists():
                problems.append(f"{md.name}: references missing script {path}")

    for msg in problems:
        print(f"  {msg}")
    print(f"{len(DOCUMENTED)} scripts, {checked} flags and paths checked, "
          f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
