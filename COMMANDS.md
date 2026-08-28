# Command Reference

Every script in this vault, every flag, and when you would actually reach for it.

All of them take `--help`. Run them from anywhere — paths resolve relative to the
script, not your shell. If `python` alone fails with `ModuleNotFoundError`, see
[RUNNING.md](RUNNING.md).

## Quick answers

| I want to... | Command |
| :--- | :--- |
| Factor 15 on my laptop | `uv run python 04_Algorithms/shors_15.py` |
| See what a hardware run would cost | `uv run python 04_Algorithms/shors_15_ibm.py` |
| Actually run it on IBM | `uv run python 04_Algorithms/shors_15_ibm.py --submit` |
| Re-read a job I already submitted | `uv run python 04_Algorithms/shors_15_ibm.py --job <id>` |
| Prove a weak result is real | add `--shots 16384` |
| Check my IBM token works | `uv run python _scripts/ibm_account.py` |
| Rebuild the circuit images | `uv run python _scripts/build_figures.py` |
| Check nothing broke | `uv run python _scripts/build_figures.py --check` and `uv run python _scripts/check_links.py` |

---

## `04_Algorithms/shors_15.py` — factor 15, simulated

Exact simulation on your laptop. No IBM account, no noise, always works.

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--a {2,4,7,8,11,13}` | `2` | The base whose period is found. All six work; they differ in the period they produce (`4, 2, 4, 4, 2, 4`). Change it to see the algorithm is not special-cased to one number. |
| `--shots N` | `1024` | How many times the circuit is run and measured. More shots = smoother distribution. On a noiseless simulator this only smooths sampling randomness; the answer is already correct. |

```bash
uv run python 04_Algorithms/shors_15.py
uv run python 04_Algorithms/shors_15.py --a 7 --shots 4096
```

---

## `04_Algorithms/shors_15_ibm.py` — factor 15 on real hardware

Same circuit, plus authentication, transpilation and verification.
**Safe by default: without `--submit` it submits nothing.**

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--submit` | *off* | Actually queue a job and spend quota. Without it you get a dry run: transpiles against a local fake backend, reports depth, gate count and estimated fidelity, submits nothing. **Always dry-run first.** |
| `--counting N` | `3` | Counting qubits — the main cost and quality knob. See the table below; the default is the only value that is both runnable and provable. |
| `--shots N` | `4096` | Circuit repetitions. Raises *statistical confidence*, never signal quality. Doubling shots shrinks the error bar by √2. Use it to prove a marginal result is real, not to make a noisy device better. |
| `--a {2,4,7,8,11,13}` | `2` | Base, as above. |
| `--job ID` | — | Skip running; fetch a job you already submitted and re-analyse it. Use when a job is still queued, or to re-examine an old result. |
| `--backend NAME` | least busy | Pin a specific device, e.g. `--backend ibm_fez`. Default picks whichever is least busy. Useful when one device gave you a bad qubit. |
| `--opt-level {0,1,2,3}` | `3` | Transpiler effort. Higher means more optimisation and a shallower circuit, but slower compilation. Rarely worth lowering. |

### Choosing `--counting`

| `--counting` | Ideal outcomes | Random noise scores | Fidelity | Verdict |
| :-: | :-: | :-: | :-: | :--- |
| 2 | 4 of 4 | **100%** | ~37% | Cheapest, but **unfalsifiable** — noise scores as well as a working QPU |
| **3** | 4 of 8 | 50% | ~9% | **Default.** Runnable *and* provable |
| 4 | 4 of 16 | 25% | ~0.6% | Signal too weak to detect |
| 8 | 4 of 256 | 1.6% | ~0% | Textbook, pure noise on today's hardware |

```bash
uv run python 04_Algorithms/shors_15_ibm.py                      # dry run first
uv run python 04_Algorithms/shors_15_ibm.py --submit             # queue it
uv run python 04_Algorithms/shors_15_ibm.py --submit --shots 16384
uv run python 04_Algorithms/shors_15_ibm.py --job da8mnr4e74ec73airbdg
```

### Reading the output

| Section | What to look for |
| :--- | :--- |
| Provenance | `simulator False` proves it was real hardware. Cross-check the job id at [quantum.cloud.ibm.com/workloads](https://quantum.cloud.ibm.com/workloads) |
| On-support excess | The honest signal. Above 3σ is real, above 5σ is decisive |
| Implied fidelity | What the data says, versus what gate errors predicted. A big gap means readout or a bad qubit |
| Error by output bit | If one bit is `RANDOMISED` while others are fine, it is one bad qubit, not circuit depth. Retry on another backend |
| `pass the a^r = 1 check` | **Flattering.** Any multiple of the period passes, so noise passes too. Trust the on-support number instead |
| Classical verification | The one that actually matters. `3 x 5 == 15` is checkable without trusting the QPU |

---

## `_scripts/ibm_account.py` — check credentials

No flags. Prints a **masked** token, channel and instance, so it is safe to run in
front of anyone. Translates IBM's errors into what to do about them.

```bash
uv run python _scripts/ibm_account.py
```

If IBM answers at all, `.env` is working — being *rejected* is an account problem,
not a local one.

---

## `_scripts/build_figures.py` — regenerate circuit images

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--check` | *off* | Regenerate into a temp directory and compare byte for byte with what is committed. Touches nothing, exits non-zero on drift. **Run after `uv lock --upgrade`** — a new matplotlib can silently change every image |
| `--only TEXT` | all | Only rebuild figures whose name contains `TEXT`, e.g. `--only shor` |
| `--scale N` | `1.0` | Gate box size relative to the wires. Raise if labels look cramped |
| `--dpi N` | `200` | Image resolution. Affects sharpness when zoomed, and file size |

To resize a figure **in a note**, edit its `width` attribute instead — no rebuild
needed, and both Obsidian and GitHub honour it.

```bash
uv run python _scripts/build_figures.py
uv run python _scripts/build_figures.py --check
uv run python _scripts/build_figures.py --only teleport --scale 1.4
```

---

## `_scripts/check_links.py` — verify every link

No flags. Checks that link targets exist, heading anchors exist in the target file,
and image sources resolve. Flags Obsidian `[[wikilinks]]`, which render as literal
brackets on GitHub. Exits non-zero if anything is broken.

```bash
uv run python _scripts/check_links.py
```

---

## Dependencies

| Command | What it does |
| :--- | :--- |
| `uv add PKG` | Add a package; updates `pyproject.toml` and `uv.lock` |
| `uv remove PKG` | Drop one |
| `uv sync` | Rebuild `.venv` to match `uv.lock` exactly |
| `uv lock --upgrade` | Bump everything to the newest allowed versions |

Commit `pyproject.toml` and `uv.lock` together. Never edit the lock by hand. After
an upgrade, run `build_figures.py --check`.
