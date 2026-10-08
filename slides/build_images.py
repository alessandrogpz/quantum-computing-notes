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

# --- Ry rotations by concrete angles ----------------------------------------
fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.6))
for ax, (theta, name) in zip(axes, [(0, "0"), (math.pi / 3, r"\pi/3"),
                                    (math.pi / 2, r"\pi/2"), (math.pi, r"\pi")]):
    unit_circle(ax)
    arrow(ax, 0, "", "#cfcfcf", lw=1.6)
    arrow(ax, theta / 2, "", ACCENT)
    a0, a1 = math.cos(theta / 2), math.sin(theta / 2)
    ax.set_title(rf"$R_y({name})$", fontsize=14, color=INK, pad=4)
    ax.text(0, -1.28, rf"$P(0)={a0**2:.2f}\quad P(1)={a1**2:.2f}$",
            ha="center", fontsize=11, color=INK)
save_fig(fig, "circle_rotations")

# --- gates -------------------------------------------------------------------
g = QuantumCircuit(1); g.h(0); g.x(0); g.y(0); g.z(0)
save_circuit(g, "gates_single")

bell = QuantumCircuit(2); bell.h(0); bell.cx(0, 1)
save_circuit(bell, "circuit_bell")

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
