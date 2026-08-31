# Command Reference

Every script in this vault, every flag, and when you would actually reach for it.

All of them take `--help`. Run them from anywhere — paths resolve relative to the
script, not your shell. If `python` alone fails with `ModuleNotFoundError`, see
[RUNNING.md](RUNNING.md).

## Quick answers

| I want to... | Command |
| :--- | :--- |
| Distribute a key with BB84 | `uv run python 03_Protocols/bb84.py` |
| Watch BB84 catch an eavesdropper | `uv run python 03_Protocols/bb84.py --eve` |
| Distribute a key with E91 | `uv run python 03_Protocols/e91.py` |
| Watch a Bell violation collapse | `uv run python 03_Protocols/e91.py --eve` |
| Run a protocol on real IBM hardware | `uv run python 03_Protocols/e91_ibm.py --submit` |
| Measure a backend's own error floor | run the `_ibm.py` script **without** `--eve` first |
| Factor 15 on my laptop | `uv run python 04_Algorithms/shors_15.py` |
| See what a hardware run would cost | `uv run python 04_Algorithms/shors_15_ibm.py` |
| Actually run it on IBM | `uv run python 04_Algorithms/shors_15_ibm.py --submit` |
| Re-read a job I already submitted | `uv run python 04_Algorithms/shors_15_ibm.py --job <id>` |
| Prove a weak result is real | add `--shots 16384` (Shor) or raise `--rounds` (QKD) |
| Check my IBM token works | `uv run python _scripts/ibm_account.py` |
| Rebuild the circuit images | `uv run python _scripts/build_figures.py` |
| Check nothing broke | `uv run python _scripts/build_figures.py --check` and `uv run python _scripts/check_links.py` |

> [!tip] The `_ibm.py` scripts never submit anything unless you pass `--submit`
> Without it you get a dry run: transpiled against a local fake backend, with the
> cost and the expected result quality reported, and nothing queued.

---

## `03_Protocols/bb84.py` — BB84 key distribution, simulated

Exact simulation on your laptop. No IBM account, no noise, always works.
Every number it prints is one the [BB84](03_Protocols/BB84.md) note derives.

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--rounds N` | `512` | Qubits Alice sends. Half survive sifting, then `--check` of those are spent on the test, so the key is roughly `N/4` bits. Raise it to tighten every percentage below. |
| `--eve` | *off* | Put an intercept-resend eavesdropper on the channel. She guesses a basis, copies the qubit, and passes it on — which corrupts 25% of the sifted bits. |
| `--check F` | `0.5` | Fraction of the sifted bits sacrificed to detect Eve. They are announced publicly and discarded. Lower it to keep more key at the cost of a weaker test; each compared bit is an independent 3-in-4 chance for Eve to slip past. |
| `--threshold F` | `0.11` | Error rate above which the key is thrown away. 11% is the Shor–Preskill bound, where the extractable key rate `1 - 2h(Q)` reaches zero. Lower it if you trust your channel; never raise it. |
| `--table N` | `12` | Print the first N rounds bit by bit — Alice's bit and basis, Eve's, Bob's, whether it survived sifting and whether it errored. `0` prints none. |
| `--seed N` | `0` | Seeds every classical choice, so a run reproduces exactly. Change it for a different key. |

```bash
uv run python 03_Protocols/bb84.py
uv run python 03_Protocols/bb84.py --eve
uv run python 03_Protocols/bb84.py --rounds 4096 --check 0.25 --table 0
```

### Reading the output

| Section | What to look for |
| :--- | :--- |
| Sifting | `bases agreed` should sit near 50%. It is a coin flip per round, nothing more |
| `mismatches` | **The whole protocol.** 0% clean, ~25% with Eve. Compare against the abort threshold, not against zero |
| `survives ... with probability` | How likely an eavesdropper was to get away with it. Falls off a cliff with the number of compared bits |
| What Eve came away with | ~75%, and unusable to her, because the key is discarded. Printed as an oracle's view — neither Alice nor Bob could compute it |
| `they differ in N places` | Errors left in the surviving key. Real BB84 removes these with error correction and privacy amplification, which this stops short of |

---

## `03_Protocols/bb84_ibm.py` — BB84 on real hardware

Same protocol, packed into a single circuit and transpiled for an IBM device.
**Safe by default: without `--submit` it submits nothing.**

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--submit` | *off* | Actually queue a job and spend quota. Without it you get a dry run: transpiles against a local fake backend, reports depth, gate count and the QBER floor the device's calibration implies. **Always dry-run first.** |
| `--rounds N` | `512` | As above. Sets the shot count: the busiest of the 16 configurations decides it. |
| `--eve` | *off* | As above. Costs one extra qubit per configuration, for Eve's probe. |
| `--check F` | `0.5` | As above. |
| `--threshold F` | `0.11` | As above. On hardware the device's own noise eats into this budget before Eve arrives. |
| `--table N` | `12` | As above. |
| `--seed N` | `0` | As above — and it is what makes `--job` work, since the same seed draws the same rounds for the shots to be dealt to. |
| `--job ID` | — | Skip running; fetch a job you already submitted and re-analyse it. Pass the same `--seed` and `--eve` it was submitted with. |
| `--backend NAME` | least busy | Pin a specific device, e.g. `--backend ibm_fez`. Useful when the per-configuration table fingers one bad qubit. |
| `--opt-level {0,1,2,3}` | `3` | Transpiler effort. The barriers between Alice, Eve and Bob survive every level — without them level 3 would cancel the two basis rotations against each other. |

```bash
uv run python 03_Protocols/bb84_ibm.py                    # dry run first
uv run python 03_Protocols/bb84_ibm.py --submit           # measure the noise floor
uv run python 03_Protocols/bb84_ibm.py --submit --eve     # then compare against it
```

> [!warning] Run without `--eve` first, and keep the number
> A real channel is noisy, and BB84 cannot tell noise from an eavesdropper — both
> are just errors in the sifted bits. The clean-channel run measures the device's
> own error floor, and every later run has to be read against that rather than
> against 0%.

---

## `03_Protocols/e91.py` — E91 key distribution, simulated

Exact simulation on your laptop. Detects the eavesdropper through a Bell inequality
violation rather than through disturbance. Derivations in [E91](03_Protocols/E91.md).

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--rounds N` | `2048` | Entangled pairs distributed. Only 2/9 become key bits and 4/9 feed the CHSH test, so this needs to be much larger than BB84's — the error bar on `S` is what decides whether a violation means anything. |
| `--eve` | *off* | Let an eavesdropper entangle herself with Alice's qubit. This halves every correlation, dropping `S` from 2.828 to 1.414 and putting 25% errors in the key. |
| `--table N` | `12` | Print the first N rounds: both settings, both outcomes, Eve's, and whether the round was used for key, for the test, or discarded. `0` prints none. |
| `--seed N` | `0` | Seeds every classical choice, so a run reproduces exactly. |

```bash
uv run python 03_Protocols/e91.py
uv run python 03_Protocols/e91.py --eve
uv run python 03_Protocols/e91.py --rounds 8192 --table 0
```

### Reading the output

| Section | What to look for |
| :--- | :--- |
| The 3×3 grid | Where the rounds fell. 2/9 key, 4/9 test, 3/9 discarded |
| `E measured` vs `E ideal` | Each correlation against `cos(θa − θb)`. Systematic gaps mean something is wrong; scatter is just sampling |
| `S = ... +/- ...` | **The security check.** Above 2 no pre-existing bits could have produced these correlations. 2.828 is Tsirelson's ceiling, 1.414 is what an intercepted pair gives |
| `VIOLATED by N sigma` | Below ~3σ the result is not evidence of anything. Raise `--rounds` |
| `Alice and Bob differ in` | 0% clean, ~25% intercepted — the same number BB84 produces, from different physics |
| No `--check` flag | Deliberate. E91's test uses rounds that were being discarded anyway, so it costs no key bits |

---

## `03_Protocols/e91_ibm.py` — E91 on real hardware

Same protocol, packed into a single circuit and transpiled for an IBM device.
**Safe by default: without `--submit` it submits nothing.**

This is the protocol in this vault that current hardware runs best — a round is one
entangling gate and two rotations, and the CHSH violation survives real noise.

| Flag | Default | What it does |
| :--- | :-- | :--- |
| `--submit` | *off* | Actually queue a job and spend quota. Without it, a dry run turns the backend's calibration into a predicted `S` before you spend anything. **Always dry-run first.** |
| `--rounds N` | `2048` | As above. Sets the shot count: the busiest of the 18 configurations decides it. |
| `--eve` | *off* | As above. Costs one extra qubit per configuration, for Eve's probe. |
| `--table N` | `12` | As above. |
| `--seed N` | `0` | As above — and what makes `--job` re-readable. |
| `--job ID` | — | Fetch a job you already submitted and re-analyse it. Pass the same `--seed` and `--eve`. |
| `--backend NAME` | least busy | Pin a specific device. Worth using when the per-configuration table shows one bad pair. |
| `--opt-level {0,1,2,3}` | `3` | Transpiler effort. Barriers keep the Bell preparation, Eve and the rotations from being folded together. |

```bash
uv run python 03_Protocols/e91_ibm.py                     # dry run, predicts S
uv run python 03_Protocols/e91_ibm.py --submit            # the device's own ceiling
uv run python 03_Protocols/e91_ibm.py --submit --eve      # then watch it collapse
```

| Section | What to look for |
| :--- | :--- |
| `predicted S` | What the backend's calibration says to expect, before spending anything. Below 2 means do not bother |
| Correlation per configuration | One row far off `ideal` is a bad qubit pair, not the protocol. Retry with `--backend` |
| `measured S` | 2.4–2.7 is a good real device. Anything above 2 by several sigma is a genuine violation |
| Noise or an eavesdropper? | Distance in sigma to each hypothesis. Noise and Eve push `S` the same way, so the clean-channel run is the only baseline that means anything |

---

## `04_Algorithms/shors_15.py` — factor 15, simulated

Exact simulation on your laptop. No IBM account, no noise, always works.

| Flag                  | Default | What it does                                                                                                                                                                       |
| :-------------------- | :------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--a {2,4,7,8,11,13}` | `2`     | The base whose period is found. All six work; they differ in the period they produce (`4, 2, 4, 4, 2, 4`). Change it to see the algorithm is not special-cased to one number.      |
| `--shots N`           | `1024`  | How many times the circuit is run and measured. More shots = smoother distribution. On a noiseless simulator this only smooths sampling randomness; the answer is already correct. |

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

## The `.env` file

Credentials live in a file called **`.env`**, in the **root of this repo** (beside
`README.md`). It is gitignored, so it never leaves the machine it is on — which
means **every machine you clone to needs its own**.

Create it from the committed template:

```bash
cp .env.example .env
```

Then fill in these variables:

| Variable | Required | Value | Where to get it |
| :--- | :-: | :--- | :--- |
| `QISKIT_API_KEY` | **yes** | IBM Cloud API key, ~44 mixed-case characters | [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) → Create → copy immediately, it is shown once |
| `INSTANCE` | no | Instance CRN, `crn:v1:bluemix:public:quantum-computing:...` | [quantum.cloud.ibm.com/instances](https://quantum.cloud.ibm.com/instances). Leave blank to use your account default |
| `CHANNEL` | no | Defaults to `ibm_quantum_platform` | Only set this if IBM tells you to |

Format is plain `KEY=value`, one per line. Blank lines and `#` comments are
ignored, and surrounding quotes are stripped:

```
QISKIT_API_KEY=your-key-here
INSTANCE=
CHANNEL=
```

> [!warning] Never put a real token in `.env.example`
> That file **is** committed. `.env` is the one that is ignored. If a token ever
> reaches a commit, rotate it at
> [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) — deleting it in a
> later commit does not remove it from history.

Verify it worked:

```bash
uv run python _scripts/ibm_account.py
```

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

## `_scripts/check_docs.py` — verify this file still matches the code

No flags. Compares COMMANDS.md against the scripts' actual argparse definitions:

1. Every flag documented here really exists.
2. Every flag a script has is documented here.
3. Every default stated here matches the parser's real default.

For credentials it also checks that the `.env` variable names agree across
`ibm_account.py`, `.env.example` and the table above, and that anything the code
requires is marked required. Someone setting up a new machine has only the docs to
go on, so an inconsistent name there is a setup that silently fails.

It also checks that every `uv run python <path>` shown in any doc points at a file
that exists. Exits non-zero on any mismatch.

```bash
uv run python _scripts/check_docs.py
```

The scripts expose `build_parser()` for this. If you add a flag and forget to
document it, this fails.

---

## Keeping everything honest

Three checks guard the things that rot silently. Run them together before
committing:

```bash
uv run python _scripts/check_docs.py && \
uv run python _scripts/check_links.py && \
uv run python _scripts/build_figures.py --check
```

| Check | Catches |
| :--- | :--- |
| `check_docs.py` | A flag renamed, removed, added, or its default changed, without this file being updated |
| `check_links.py` | A note renamed or moved, a dead heading anchor, a wikilink that would break on GitHub |
| `build_figures.py --check` | A dependency upgrade silently changing every circuit image |

All three exit non-zero on failure, so they work as a pre-commit hook or in CI.

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
