"""Superdense coding: send two classical bits by transmitting one qubit.

    python superdense_coding.py            # local simulator
    python superdense_coding.py --ibm      # real IBM hardware

Alice owns qubit 0 and Bob owns qubit 1. They share the entangled pair
(|00> + |11>)/sqrt(2), one qubit each.

Alice acts on HER qubit alone with one of four gates, then physically sends it to
Bob. He now holds both, undoes the Bell circuit, and reads two bits out.

The diagram cannot draw a qubit travelling across a room, so the hand-over is the
second barrier: gates before it are Alice's, gates after it are Bob's -- and he is
entitled to touch both wires because by then he has both qubits.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_scripts"))
from backend import run  # noqa: E402

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister  # noqa: E402

# Which gate Alice applies for each pair of bits she wants to send.
ENCODING = {"00": "I", "01": "X", "10": "Z", "11": "ZX"}


def circuit(bits: str) -> QuantumCircuit:
    alice = QuantumRegister(1, "alice")   # Alice's qubit -- the one she sends
    bob = QuantumRegister(1, "bob")       # Bob's qubit -- stays with him throughout
    c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(alice, bob, c)

    qc.h(alice)                # prepare the shared Bell pair, one qubit each
    qc.cx(alice, bob)
    qc.barrier(label="shared")

    if bits in ("01", "11"):   # Alice encodes on HER qubit only
        qc.x(alice)
    if bits in ("10", "11"):
        qc.z(alice)
    qc.barrier(label="Alice sends")   # her qubit travels to Bob here

    qc.cx(alice, bob)          # Bob now holds both and undoes the Bell circuit
    qc.h(alice)
    qc.measure([alice[0], bob[0]], [0, 1])
    return qc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ibm", action="store_true", help="run on real IBM hardware")
    ap.add_argument("--shots", type=int, default=1024)
    args = ap.parse_args()

    for bits in ("00", "01", "10", "11"):
        counts = run(circuit(bits), shots=args.shots, ibm=args.ibm)
        # Qiskit prints bitstrings little-endian, so reverse to read (Alice, Bob).
        got = max(counts, key=counts.get)[::-1]
        rate = counts[max(counts, key=counts.get)] / args.shots
        mark = "ok" if got == bits else "WRONG"
        print(f"  sent {bits} via {ENCODING[bits]:<2} -> received {got}  "
              f"({rate:.0%} of shots)  [{mark}]")


if __name__ == "__main__":
    main()
