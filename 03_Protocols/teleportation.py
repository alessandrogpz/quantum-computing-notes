"""Quantum teleportation: move one qubit's state using two classical bits.

    python teleportation.py            # local simulator
    python teleportation.py --ibm      # real IBM hardware

Alice has a qubit in the state Ry(theta)|0>. She entangles it with her half of a
shared Bell pair, measures both, and sends the two bits to Bob, who applies a
correction. To check it worked we rotate Bob's qubit back by -theta: if the state
really arrived, he measures 0 every time.
"""

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_scripts"))
from backend import run  # noqa: E402

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister  # noqa: E402

# One classical register, so local and hardware runs report bits identically.
MA, MB, OUT = 0, 1, 2


def circuit(theta: float) -> QuantumCircuit:
    psi = QuantumRegister(1, "psi")     # the state to teleport
    a = QuantumRegister(1, "alice")     # Alice's half of the pair
    b = QuantumRegister(1, "bob")       # Bob's half
    c = ClassicalRegister(3, "c")       # Alice's two bits, then Bob's check

    qc = QuantumCircuit(psi, a, b, c)
    qc.ry(theta, psi)                   # the state we want to send
    qc.h(a)                             # shared Bell pair
    qc.cx(a, b)
    qc.barrier()

    qc.cx(psi, a)                       # Alice's reverse Bell circuit
    qc.h(psi)
    qc.measure(psi, c[MA])
    qc.measure(a, c[MB])
    qc.barrier()

    with qc.if_test((c[MB], 1)):        # Bob corrects using Alice's two bits
        qc.x(b)
    with qc.if_test((c[MA], 1)):
        qc.z(b)

    qc.ry(-theta, b)                    # undo the rotation: should leave |0>
    qc.measure(b, c[OUT])
    return qc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ibm", action="store_true", help="run on real IBM hardware")
    ap.add_argument("--shots", type=int, default=1024)
    args = ap.parse_args()

    for name, theta in (("|0>", 0.0), ("pi/3", math.pi / 3),
                        ("|+>", math.pi / 2), ("|1>", math.pi)):
        counts = run(circuit(theta), shots=args.shots, ibm=args.ibm)
        # Bits print highest-index first, so Bob's check is the leftmost character.
        zeros = sum(n for bits, n in counts.items() if bits[0] == "0")
        print(f"  teleported {name:>5}: recovered correctly in "
              f"{zeros / args.shots:.1%} of shots")


if __name__ == "__main__":
    main()
