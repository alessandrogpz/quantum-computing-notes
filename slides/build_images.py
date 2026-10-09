"""Render every image used in slides.md.

    uv run python slides/build_images.py

Circuit diagrams come from the protocol scripts in 03_Protocols and 04_Algorithms,
so a slide cannot drift from the code it is describing.
"""

import math
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)
sys.path[:0] = [str(ROOT / "03_Protocols"), str(ROOT / "04_Algorithms")]

STYLE = {"backgroundcolor": "#ffffff"}
INK, ACCENT = "#1a1a1a", "#c2185b"


def save_circuit(qc, name, **kw):
    fig = qc.draw("mpl", style=STYLE, **kw)
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    print("  ", name)


def save_fig(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    print("  ", name)


def unit_circle(ax):
    """The 2D state space: every real qubit lives on this circle."""
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), color="#cccccc", lw=1.2, zorder=1)
    ax.axhline(0, color="#e8e8e8", lw=1, zorder=0)
    ax.axvline(0, color="#e8e8e8", lw=1, zorder=0)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-1.35, 1.35)


def arrow(ax, angle, label, color=INK, lw=2.4, dx=0.0, dy=0.0):
    x, y = math.cos(angle), math.sin(angle)
    ax.annotate("", xy=(x, y), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=16), zorder=3)
    ax.text(x * 1.2 + dx, y * 1.2 + dy, label, color=color, ha="center", va="center",
            fontsize=13, zorder=4)


# --- the 2D state space ------------------------------------------------------
fig, ax = plt.subplots(figsize=(5.0, 4.4))
unit_circle(ax)
arrow(ax, 0, r"$|0\rangle$")
arrow(ax, math.pi / 2, r"$|1\rangle$")
arrow(ax, math.pi / 4, r"$|+\rangle$", ACCENT)
arrow(ax, -math.pi / 4, r"$|-\rangle$", ACCENT)
ax.set_title("Real qubit states live on a circle", fontsize=13, color=INK, pad=2)
save_fig(fig, "circle_basis")

# --- the three Pauli axes, each with its own pair of outcomes ---
from matplotlib.patches import Ellipse  # noqa: E402

def bloch(ax, axis, poles, title):
    """A sphere silhouette with one axis picked out."""
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), color="#d8d8d8", lw=1.2)
    ax.add_patch(Ellipse((0, 0), 2, 0.62, fill=False, color="#e6e6e6", lw=1))

    ends = {"z": ((0, 1), (0, -1)), "x": ((-0.78, -0.26), (0.78, 0.26)),
            "y": ((0.80, -0.22), (-0.80, 0.22))}
    for name, (p1, p2) in ends.items():
        hot = name == axis
        ax.plot(*zip(p1, p2), color=ACCENT if hot else "#dcdcdc",
                lw=2.6 if hot else 1.2, zorder=3 if hot else 1)
        if hot:
            for (x, y), lab in zip((p1, p2), poles):
                ax.plot([x], [y], "o", color=ACCENT, ms=7, zorder=4)
                off = 0.22 if y >= 0 else -0.22
                ax.text(x * 1.1, y * 1.1 + off, lab, color=ACCENT,
                        ha="center", va="center", fontsize=13, zorder=5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-1.5, 1.5); ax.set_ylim(-1.5, 1.5)
    ax.set_title(title, fontsize=13, color=INK, pad=2)

# one sphere on its own, to sit beside the Z slide
fig, ax = plt.subplots(figsize=(3.4, 3.6))
bloch(ax, "z", (r"$|0\rangle$", r"$|1\rangle$"), r"$Z$ measures along $z$")
save_fig(fig, "sphere_z")

# two stacked, to sit beside the X and Y slide
fig, axes = plt.subplots(2, 1, figsize=(3.4, 7.0))
bloch(axes[0], "x", (r"$|-\rangle$", r"$|+\rangle$"), r"$X$ measures along $x$")
bloch(axes[1], "y", (r"$|{+}i\rangle$", r"$|{-}i\rangle$"), r"$Y$ measures along $y$")
save_fig(fig, "sphere_xy")

# --- what the gates do, on the circle ---
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))

ax = axes[0]
unit_circle(ax)
arrow(ax, 0, r"$|0\rangle$", "#b0b0b0", lw=1.8)
arrow(ax, math.pi / 2, r"$|1\rangle$", "#b0b0b0", lw=1.8)
arrow(ax, -math.pi / 2, r"$-|1\rangle$", ACCENT)
ax.annotate("", xy=(0.08, -0.92), xytext=(0.08, 0.92),
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.6,
                            connectionstyle="arc3,rad=-0.45", mutation_scale=14))
ax.set_title(r"$Z$ leaves $|0\rangle$, flips the sign of $|1\rangle$",
             fontsize=12, color=INK, pad=2)

ax = axes[1]
unit_circle(ax)
arrow(ax, 0, r"$|0\rangle$", "#b0b0b0", lw=1.8)
arrow(ax, math.pi / 2, r"$|1\rangle$", "#b0b0b0", lw=1.8)
arrow(ax, math.pi / 4, r"$|+\rangle$", ACCENT)
arrow(ax, -math.pi / 4, r"$|-\rangle$", ACCENT)
ax.set_title(r"$H$ sends $|0\rangle \to |+\rangle$ and $|1\rangle \to |-\rangle$",
             fontsize=12, color=INK, pad=2)
save_fig(fig, "gates_action")

# --- gates -------------------------------------------------------------------
g = QuantumCircuit(1); g.h(0); g.x(0); g.y(0); g.z(0)
save_circuit(g, "gates_single")

bell = QuantumCircuit(2); bell.h(0); bell.cx(0, 1)
save_circuit(bell, "circuit_bell")

# the Bell circuit run forwards then backwards: its own inverse
inv = QuantumCircuit(2)
inv.h(0); inv.cx(0, 1); inv.barrier(); inv.cx(0, 1); inv.h(0)
save_circuit(inv, "circuit_bell_involution")

# --- Bell measurement histogram ---------------------------------------------
m = QuantumCircuit(2); m.h(0); m.cx(0, 1); m.measure_all()
counts = StatevectorSampler().run([m], shots=1024).result()[0].data.meas.get_counts()
fig, ax = plt.subplots(figsize=(4.4, 3.2))
keys = ["00", "01", "10", "11"]
ax.bar(keys, [counts.get(k, 0) for k in keys], color=[ACCENT, "#dddddd", "#dddddd", ACCENT])
ax.set_ylabel("shots out of 1024", fontsize=10)
ax.set_title("Bell pair, measured", fontsize=12)
ax.spines[["top", "right"]].set_visible(False)
save_fig(fig, "hist_bell")

# --- protocols, drawn from the real scripts ---------------------------------
import bb84, e91, superdense_coding, teleportation  # noqa: E402

save_circuit(superdense_coding.circuit("01"), "circuit_superdense_01")
save_circuit(teleportation.circuit(math.pi / 3), "circuit_teleportation", fold=-1)
save_circuit(bb84.round_circuit((1, "X", None, "X")), "circuit_bb84_clean")
save_circuit(bb84.round_circuit((1, "X", "Z", "X")), "circuit_bb84_eve")
save_circuit(e91.round_circuit((0, 0, None)), "circuit_e91")

print(f"\n{len(list(OUT.glob('*.png')))} images in {OUT}")
