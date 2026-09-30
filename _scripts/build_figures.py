"""Regenerate the circuit diagrams used in the notes.

    python _scripts/build_figures.py

Figures are drawn from the same circuits the scripts run, so a diagram in a note
cannot drift from the code. Images land in _assets/ and notes embed them with
<img src="../_assets/name.png" width="...">.
"""

import math
import pathlib
import sys

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_assets"
sys.path[:0] = [str(ROOT / "03_Protocols"), str(ROOT / "04_Algorithms")]

import bb84  # noqa: E402
import e91  # noqa: E402
import shors  # noqa: E402
import superdense_coding  # noqa: E402
import teleportation  # noqa: E402

STYLE = {"backgroundcolor": "#ffffff"}   # readable in both Obsidian themes


def save(qc: QuantumCircuit, name: str, **kw) -> None:
    fig = qc.draw("mpl", style=STYLE, **kw)
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight", facecolor="#ffffff")
    plt.close(fig)
    print("wrote", name)


def gate(name: str, build) -> None:
    qc = QuantumCircuit(3 if name in ("gate_toffoli", "gate_fredkin") else 2)
    build(qc)
    save(qc, name)


OUT.mkdir(exist_ok=True)

# Gates
gate("gate_cnot", lambda qc: qc.cx(0, 1))
gate("gate_toffoli", lambda qc: qc.ccx(0, 1, 2))
gate("gate_fredkin", lambda qc: qc.cswap(0, 1, 2))

boxes = QuantumCircuit(1)
boxes.h(0), boxes.y(0), boxes.z(0)
save(boxes, "gate_single_qubit_boxes")

bell = QuantumCircuit(2)
bell.h(0), bell.cx(0, 1)
save(bell, "circuit_bell_prep")

involution = QuantumCircuit(2)
involution.h(0), involution.cx(0, 1), involution.barrier(), involution.cx(0, 1), involution.h(0)
save(involution, "circuit_bell_involution")

# Protocols and algorithms, drawn from the circuits the scripts actually run
save(superdense_coding.circuit("00"), "circuit_superdense_00")
save(superdense_coding.circuit("01"), "circuit_superdense_01")
save(teleportation.circuit(math.pi / 3), "circuit_teleportation", fold=-1)
save(shors.circuit(2, 3), "circuit_shor_qpe", fold=-1)

# BB84 and E91 rounds, clean and with Eve. The barriers separate the parties;
# they are in the circuit to stop the transpiler folding Alice's rotation into
# Bob's, and happen to be where a reader wants a divider too.
save(bb84.round_circuit((1, "X", None, "X")), "circuit_bb84_round")
save(bb84.round_circuit((1, "X", "Z", "X")), "circuit_bb84_eve")
save(e91.round_circuit((0, 0, None)), "circuit_e91_round")
save(e91.round_circuit((0, 0, "Z")), "circuit_e91_eve")
