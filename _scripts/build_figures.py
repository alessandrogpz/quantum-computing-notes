"""Regenerate every circuit figure embedded in the vault.

    uv run python _scripts/build_figures.py                 # all figures
    uv run python _scripts/build_figures.py --only teleport # just matching ones
    uv run python _scripts/build_figures.py --dpi 300       # sharper files
    uv run python _scripts/build_figures.py --scale 1.4     # bigger gate boxes
    uv run python _scripts/build_figures.py --check         # has anything drifted?

--check regenerates every figure into a temporary directory and compares it byte
for byte with what is committed, without touching _assets/. It exits non-zero on
any difference. Run it after `uv lock --upgrade`: a matplotlib or qiskit release
can change font metrics or gate rendering, which would silently alter every image
in the vault. Nothing else in the repo would catch that.

There are three independent size knobs. Reach for them in this order:

1. DISPLAY WIDTH -- how large the image looks in a note.
   Set per figure by the `width=` argument below; it is written into the embed as
   <img src="../_assets/name.png" width="480">. Both Obsidian and GitHub honour
   that width. Change it in the note directly and nothing needs regenerating --
   this is the knob for "this looks too big on my screen".

2. SCALE -- how large the gate boxes are relative to the wires, i.e. the shape of
   the drawing rather than its size. Qiskit's own `draw(scale=...)`. Raise it when
   labels feel cramped on a busy circuit. Regeneration required.

3. DPI -- raster resolution of the PNG on disk. Only affects sharpness when zoomed
   in, and file size. Regeneration required.

Adding a figure: write a builder function, decorate it with @figure(...), re-run.
Embed snippets for every figure are listed in _assets/00_Figures.md.
Run _scripts/check_links.py afterwards to confirm every embed still resolves.
"""

import argparse
import pathlib
import sys
import tempfile

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_assets"

# --- defaults, overridable from the command line -----------------------------
DPI = 200
SCALE = 1.0
DEFAULT_WIDTH = 480

# White card background: readable in both Obsidian light and dark themes.
STYLE = {"backgroundcolor": "#ffffff"}

# Qiskit escapes barrier labels and truncates them around 15 characters, so they
# cannot carry LaTeX. Keep them short and plain; put any real maths in the note
# beneath the figure, where Obsidian's MathJax renders it properly.
MAX_LABEL = 15

FIGURES: list[tuple] = []


def figure(name: str, *, width: int = DEFAULT_WIDTH, scale: float | None = None, **draw_kw):
    """Register a circuit builder as a named figure."""

    def deco(fn):
        FIGURES.append((name, fn, width, scale, draw_kw))
        return fn

    return deco


def barrier(qc: QuantumCircuit, label: str) -> None:
    """Add a labelled barrier, failing loudly if the label would be truncated."""
    assert len(label) <= MAX_LABEL, f"barrier label too long ({len(label)}): {label!r}"
    qc.barrier(label=label)


# =============================================================================
# 02_Gates -- reversible classical gates
# =============================================================================

@figure("gate_cnot", width=300)
def _cnot():
    qc = QuantumCircuit(QuantumRegister(1, "x"), QuantumRegister(1, "y"))
    qc.cx(0, 1)
    return qc


@figure("gate_toffoli", width=320)
def _toffoli():
    qc = QuantumCircuit(QuantumRegister(1, "x"), QuantumRegister(1, "y"), QuantumRegister(1, "z"))
    qc.ccx(0, 1, 2)
    return qc


@figure("gate_fredkin", width=320)
def _fredkin():
    qc = QuantumCircuit(QuantumRegister(1, "x"), QuantumRegister(1, "y"), QuantumRegister(1, "z"))
    qc.cswap(0, 1, 2)
    return qc


# =============================================================================
# 02_Gates -- single-qubit gates
# =============================================================================

@figure("gate_single_qubit_boxes", width=340)
def _boxes():
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.y(0)
    qc.z(0)
    return qc


@figure("circuit_bell_prep", width=300)
def _bell_prep():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


@figure("circuit_bell_involution", width=420)
def _bell_involution():
    # Deliberately an *unlabelled* barrier: it marks the midpoint of the circuit,
    # and the state at that point is written as LaTeX in Involutions.md.
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    qc.cx(0, 1)
    qc.h(0)
    return qc


# =============================================================================
# 03_Protocols -- superdense coding
# =============================================================================

def _superdense(bits: str) -> QuantumCircuit:
    a, b = QuantumRegister(1, "alice"), QuantumRegister(1, "bob")
    qc = QuantumCircuit(a, b)
    qc.h(a)
    qc.cx(a, b)
    barrier(qc, "Bell prep")
    if bits == "00":
        qc.id(a)
    if bits in ("01", "11"):
        qc.x(a)
    if bits in ("10", "11"):
        qc.z(a)
    barrier(qc, "Alice encodes")
    qc.cx(a, b)
    qc.h(a)
    return qc


for _bits in ("00", "01", "10", "11"):
    figure(f"circuit_superdense_{_bits}", width=560)(
        lambda bits=_bits: _superdense(bits)
    )


# =============================================================================
# 03_Protocols -- teleportation
# =============================================================================

@figure("circuit_teleportation", width=760, fold=-1)
def _teleportation():
    psi = QuantumRegister(1, "psi")
    a, b = QuantumRegister(1, "alice"), QuantumRegister(1, "bob")
    c0, c1 = ClassicalRegister(1, "c0"), ClassicalRegister(1, "c1")
    qc = QuantumCircuit(psi, a, b, c0, c1)
    qc.h(a)
    qc.cx(a, b)
    barrier(qc, "shared pair")
    qc.cx(psi, a)
    qc.h(psi)
    qc.measure(psi, c0)
    qc.measure(a, c1)
    barrier(qc, "send 2 bits")
    with qc.if_test((c1, 1)):
        qc.x(b)
    with qc.if_test((c0, 1)):
        qc.z(b)
    return qc


# =============================================================================
# 04_Algorithms -- Shor
# =============================================================================

@figure("circuit_shor_qpe", width=820, fold=-1)
def _shor_qpe():
    """The phase-estimation skeleton, with 3 counting qubits so it stays legible.

    The runnable version in 04_Algorithms/shors_15.py uses 8.
    """
    import sys
    sys.path.insert(0, str(ROOT / "04_Algorithms"))
    from shors_15 import c_amod15, qft_dagger  # noqa: E402

    n_count, n_work = 3, 4
    qc = QuantumCircuit(n_count + n_work, n_count)
    for q in range(n_count):
        qc.h(q)
    qc.x(n_count)
    barrier(qc, "superpose")
    for q in range(n_count):
        qc.append(c_amod15(2, q), [q] + list(range(n_count, n_count + n_work)))
    barrier(qc, "a^x mod 15")
    qc.compose(qft_dagger(n_count), range(n_count), inplace=True)
    qc.measure(range(n_count), range(n_count))
    return qc


# =============================================================================

def render(entry, outdir: pathlib.Path, args) -> pathlib.Path:
    """Draw one registered figure into outdir and return the path written."""
    name, fn, _width, scale, draw_kw = entry
    fig = fn().draw("mpl", style=STYLE, scale=scale or args.scale, **draw_kw)
    path = outdir / f"{name}.png"
    fig.savefig(path, dpi=args.dpi, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dpi", type=int, default=DPI, help=f"PNG resolution (default {DPI})")
    ap.add_argument("--scale", type=float, default=SCALE,
                    help=f"gate box size relative to wires (default {SCALE})")
    ap.add_argument("--only", default=None, help="only build figures whose name contains this")
    ap.add_argument("--check", action="store_true",
                    help="compare against the committed figures instead of overwriting them")
    args = ap.parse_args()

    selected = [f for f in FIGURES if not args.only or args.only in f[0]]
    if not selected:
        sys.exit(f"no figures match --only {args.only!r}")

    if args.check:
        sys.exit(check(selected, args))

    OUT.mkdir(exist_ok=True)
    built = []
    for entry in selected:
        render(entry, OUT, args)
        built.append((entry[0], entry[2]))
        print(f"wrote {entry[0]}.png  (embed width {entry[2]})")

    if not args.only:
        write_manifest(built, args)


def check(selected, args) -> int:
    """Regenerate into a temp dir and diff against _assets/. Returns an exit code."""
    drifted, missing = [], []
    with tempfile.TemporaryDirectory() as td:
        for entry in selected:
            fresh = render(entry, pathlib.Path(td), args)
            committed = OUT / fresh.name
            if not committed.exists():
                missing.append(fresh.name)
            elif committed.read_bytes() != fresh.read_bytes():
                drifted.append(fresh.name)

    for name in missing:
        print(f"MISSING  {name}  (registered but not in {OUT.name}/)")
    for name in drifted:
        print(f"DRIFTED  {name}  (committed image differs from a fresh render)")

    if not drifted and not missing:
        print(f"{len(selected)} figures match the committed images.")
        return 0

    print(f"\n{len(drifted)} drifted, {len(missing)} missing, "
          f"{len(selected) - len(drifted) - len(missing)} unchanged.")
    print("Rebuild and review the diff:  uv run python _scripts/build_figures.py")
    return 1


def write_manifest(built: list[tuple[str, int]], args) -> None:
    rows = "\n".join(
        f'| `{name}.png` | {width} | '
        f'`<img src="../_assets/{name}.png" width="{width}" alt="{name.replace("_", " ")}">` |'
        for name, width in built
    )
    (OUT / "00_Figures.md").write_text(f"""# Figures

Generated by `_scripts/build_figures.py` — **do not edit these images by hand.**
Built at dpi {args.dpi}, scale {args.scale}.

Embeds are plain HTML rather than Obsidian `![[wikilink]]` syntax, because GitHub
does not render wikilinks. Both Obsidian and GitHub honour the `width` attribute.

To resize one in a note, change its `width`. No regeneration needed.

| File | Default width | Embed snippet |
| :--- | :-: | :--- |
{rows}

Rebuild everything:

```bash
uv run python _scripts/build_figures.py
```
""")
    print(f"wrote 00_Figures.md ({len(built)} figures)")


if __name__ == "__main__":
    main()
