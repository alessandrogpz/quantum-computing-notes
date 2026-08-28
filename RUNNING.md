# Running Things

How to actually execute the Python in this vault.

## The problem in one line

```bash
python 04_Algorithms/shors_15.py
```

```
ModuleNotFoundError: No module named 'qiskit'
```

Your **system** Python has no qiskit. The packages for this project live in a
`.venv/` folder inside the repo, and something has to point Python at them. That
is the only thing `uv run` is doing.

## Two ways to fix it

### A. Prefix with `uv run`

```bash
uv run python 04_Algorithms/shors_15.py
```

Means *"run this with the project's Python."* It also checks the environment
matches `uv.lock` before running and repairs it if not, so it works even on a
fresh clone with no `.venv` at all. Nothing to set up, nothing to forget.

### B. Activate once per terminal, then plain `python`

```bash
source .venv/bin/activate.fish
```

After that, `python` *means* the project's Python in that terminal:

```bash
python 04_Algorithms/shors_15.py     # no prefix needed
```

It lasts until you close the terminal. `deactivate` ends it early. Check it worked
with `which python` — it should print a path inside this repo.

> In bash or zsh the file is `.venv/bin/activate` instead. This project's shell is
> fish, hence `.fish`.

**Which to use:** A in documentation and scripts, because it cannot be forgotten.
B while you are working, if typing the prefix gets old. They are interchangeable.

## Every command in this vault

```bash
# Algorithms
uv run python 04_Algorithms/shors_15.py               # factor 15, exact simulation
uv run python 04_Algorithms/shors_15.py --a 7         # a different base
uv run python 04_Algorithms/shors_15_ibm.py           # what a hardware run would cost
uv run python 04_Algorithms/shors_15_ibm.py --submit  # really queue an IBM job

# Credentials
uv run python _scripts/ibm_account.py                 # verify .env is readable

# Figures
uv run python _scripts/build_figures.py               # rebuild circuit images
uv run python _scripts/build_figures.py --check       # have any figures drifted?

# Links
uv run python _scripts/check_links.py                 # do all links still resolve?
```

Every script accepts `--help`.

**Your working directory does not matter.** These all work from the repo root, from
inside `04_Algorithms/`, anywhere. Paths are resolved relative to the script file,
not your shell.

## Managing dependencies

```bash
uv add sympy          # add a package (updates pyproject.toml and uv.lock)
uv remove sympy       # drop one
uv sync               # rebuild .venv to match uv.lock exactly
uv lock --upgrade     # bump everything to the newest allowed versions
```

Commit `pyproject.toml` and `uv.lock` together. Never edit `uv.lock` by hand.

After `uv lock --upgrade`, run the figure check — a new matplotlib can silently
change every image in the vault:

```bash
uv run python _scripts/build_figures.py --check
```

## Checking IBM credentials

```bash
uv run python _scripts/ibm_account.py
```

Prints a **masked** token, the channel and the instance, so it is safe to run in
front of anyone. If IBM rejects the credentials, the loader translates the error
into what to actually do rather than raising a stack trace.

A key point when this fails: if IBM answers at all, `.env` is working. Reaching
IBM and being rejected is an *account* problem, not a local one.

## When something goes wrong

| Symptom | Fix |
| :--- | :--- |
| `ModuleNotFoundError` | You forgot `uv run`, or the venv is not activated |
| `command not found: uv` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `No credentials file at .../.env` | `cp .env.example .env` and paste your token in |
| Wrong Python version | `rm -rf .venv` then `uv sync`; `.python-version` pins it |
| `.venv` seems broken | Delete it. The next `uv run` rebuilds it from the lock |
| `Provided API key is disabled` | Account-side, not local. Create a new key at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) |
| `Unable to retrieve instances` | Usually the same thing — read the error above it, that one is the real cause |
| `InvalidAccountError` | Run `uv run python _scripts/ibm_account.py` for a plain-language diagnosis |

Deleting `.venv/` is always safe — it is a build output, gitignored, and rebuilt
from `pyproject.toml` + `uv.lock` in seconds.

---

More on how uv works and why `uv.lock` is committed: [README](README.md#setup).
