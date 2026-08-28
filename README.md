# Quantum Computing Notes

A structured knowledge base and Obsidian vault for quantum computing: theory notes
alongside runnable Qiskit code.

Primary source: *Quantum Computing for Everyone* — Chris Bernhardt.

---

## Directory Architecture & Quick Navigation

```text
quantum-comp-notes/
├── _assets/          generated circuit figures (do not edit by hand)
├── RUNNING.md             how to run the scripts
├── COMMANDS.md            every command and flag
├── .env.example           template for IBM credentials (.env is gitignored)
├── _scripts/
│   ├── build_figures.py   regenerates everything in _assets/
│   ├── check_docs.py      verifies COMMANDS.md matches the code
│   ├── check_links.py     verifies every link resolves
│   └── ibm_account.py     loads IBM credentials from .env
├── 01_Foundations/
│   ├── Dirac_Notation.md
│   ├── Tensor_Products.md
│   ├── Entanglement_Criterion.md
│   └── Measurement_and_Perspective.md
├── 02_Gates/
│   ├── Reversible_Classical_Gates.md
│   ├── From_Classical_To_Quantum.md
│   ├── Single_Qubit_Gates.md
│   └── Involutions.md
├── 03_Protocols/
│   ├── Superdense_Coding.md
│   └── Quantum_Teleportation.md
├── 04_Algorithms/
│   ├── Shors_Algorithm.md
│   ├── shors_15.py         exact simulation, no account needed
│   └── shors_15_ibm.py     transpiled for real IBM hardware
└── 99_TODO/
    ├── Open_Questions.md
    └── Real_vs_Complex_Amplitudes.md
```

| Section | Description |
| :--- | :--- |
| **[01_Foundations](01_Foundations/00_Foundations.md)** | Dirac notation, tensor products, the entanglement criterion, measurement from either party's perspective. |
| **[02_Gates](02_Gates/00_Gates.md)** | Reversible classical gates (CNOT, Toffoli, Fredkin), the move to qubits, single-qubit gates, involutions. |
| **[03_Protocols](03_Protocols/00_Protocols.md)** | Superdense coding and quantum teleportation. |
| **[04_Algorithms](04_Algorithms/00_Algorithms.md)** | Quantum algorithms with runnable implementations. Shor's algorithm factoring 15. |
| **[99_TODO](99_TODO/00_TODO.md)** | Parked: open questions, and the deferred move to complex amplitudes. |

---

## Navigation Convention

Every folder in this vault contains an index document starting with the **`00_`**
prefix, named after its folder (e.g. `01_Foundations/00_Foundations.md`).

These `00_` index files sort to the top of each folder and contain the reading
order, a summary of the topic, and relative links to all sub-topics and code stored
in that directory.

Qiskit snippets live next to the note they belong to, either fenced inside the
markdown or as a sibling `.py` / `.ipynb` file linked from the `00_` index.

Related: hands-on course work lives in [`../qiskit-fundamentals`](../qiskit-fundamentals).

---

## Setup

The vault carries its own Python environment, managed by [uv](https://docs.astral.sh/uv/).
After cloning, there is **no install step** — run anything with `uv run` and the
environment builds itself:

```bash
uv run python _scripts/build_figures.py
```

The first run creates `.venv/` and installs the pinned dependencies (a few
seconds); later runs reuse it. `uv sync` does the same thing explicitly, if you
prefer to see it happen before running anything.

If the pinned Python is not on the machine, uv downloads it — no system Python is
required and nothing outside this folder is touched.

### What controls it

| File | Committed | Role |
| :--- | :-: | :--- |
| `pyproject.toml` | yes | the dependencies you asked for (`qiskit`, `matplotlib`, `pylatexenc`) |
| `uv.lock` | yes | the exact versions resolved, so every clone gets the same ones |
| `.python-version` | yes | the Python version uv builds the environment against |
| `.venv/` | **no** | the built environment — local, disposable, gitignored |

Never edit `uv.lock` by hand. To change dependencies:

```bash
uv add sympy          # add one (updates pyproject.toml and uv.lock)
uv remove sympy       # drop one
uv lock --upgrade     # refresh everything to the newest allowed versions
```

Commit `pyproject.toml` and `uv.lock` together — that pair is what makes the vault
reproducible. If `.venv/` ever misbehaves, delete it; the next `uv run` rebuilds it.

Obsidian settings in `.obsidian/` are committed too, except `workspace.json`
(per-machine pane layout) and downloaded plugin bundles.

## Running Things

`python somefile.py` will not work — your system Python has no qiskit. Prefix with
`uv run`, which uses the project's own environment:

```bash
uv run python 04_Algorithms/shors_15.py
```

Or activate once per terminal (`source .venv/bin/activate.fish`) and drop the
prefix.

- **[COMMANDS.md](COMMANDS.md)** — every command and flag, and when to use it
- **[RUNNING.md](RUNNING.md)** — setup, dependencies, troubleshooting

## IBM Quantum Credentials

Scripts that reach real hardware read their credentials from **`.env`** at the
vault root, which is gitignored:

```bash
cp .env.example .env                      # paste your token into .env
uv run python _scripts/ibm_account.py     # verify (prints a masked token)
```

Never put a token in `.env.example` — that file is committed. `.gitignore` covers
`.env`, `.env.*`, `*.token`, `*.key`, `credentials.json` and `.qiskit/`. If a token
ever does land in a commit, rotate it rather than trying to delete it: it stays in
the git history.

## Circuit Diagrams

Circuit figures are **generated from Qiskit, not drawn by hand**. The circuit that
appears in a note is the same object that runs, so the picture cannot drift from
the physics. `_assets/00_Figures.md` lists every figure with its embed snippet.

To change or add one: edit `_scripts/build_figures.py`, then

```bash
uv run python _scripts/build_figures.py
```

They render on a white card so they stay readable in both the light and dark
Obsidian themes.

### Resizing

Three independent knobs, in the order you should reach for them:

| Knob | Where | Regenerate? | Use it when |
| :--- | :--- | :-: | :--- |
| **Display width** | the `width` attribute, e.g. `<img src="../_assets/gate_cnot.png" width="300">` | no | a figure is too big or small in a note |
| **Scale** | `width=`/`scale=` in `@figure(...)`, or `--scale` | yes | gate boxes feel cramped or sparse |
| **DPI** | `DPI` in the script, or `--dpi` | yes | it looks soft when zoomed, or files are too heavy |

Display width is the one you want almost every time — edit the `width` attribute
directly in the note and it rescales on the spot, no rebuild. Obsidian and GitHub
both honour it.

```bash
uv run python _scripts/build_figures.py --only teleport --scale 1.4
```

### Checking for drift

Figures are generated, so a dependency upgrade can silently change all of them —
a new matplotlib can shift font metrics or gate rendering without a single circuit
changing. To catch that:

```bash
uv run python _scripts/build_figures.py --check
```

It regenerates everything into a temporary directory, compares byte for byte
against what is committed, and exits non-zero on any difference. `_assets/` is not
touched. Run it after `uv lock --upgrade`; nothing else in the repo would notice.

Barrier labels are limited to 15 characters and cannot contain LaTeX (Qiskit
escapes and truncates them), so equations belonging to a figure go in the note
beneath it, where MathJax renders them properly. The script asserts on labels that
would be truncated.

## Workflow

| Layer | Lives in | Why |
| :--- | :--- | :--- |
| Understanding | `.md` notes | wikilinks, backlinks, graph view, search, clean git diffs |
| Computation | `.ipynb` / `.py` | run it, plot it, get the statevector back |
| Figures | `_assets/` via `_scripts/` | generated, never stale |

Notebooks are for *doing*; markdown notes are for *keeping*. When a notebook
produces something worth remembering, the conclusion goes in a note that links back
to it.
