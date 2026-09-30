"""Superdense coding: send two classical bits by transmitting one qubit.

    python superdense_coding.py            # local simulator
    python superdense_coding.py --ibm      # real IBM hardware

Alice and Bob share the entangled pair (|00> + |11>)/sqrt(2). Alice acts on her
qubit alone with one of four gates, sends it to Bob, and Bob recovers both bits.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_scripts"))
from backend import run  # noqa: E402

from qiskit import QuantumCircuit  # noqa: E402

# Which gate Alice applies for each pair of bits she wants to send.
ENCODING = {"00": "I", "01": "X", "10": "Z", "11": "ZX"}


def circuit(bits: str) -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)

    qc.h(0)                    # prepare the shared Bell pair
    qc.cx(0, 1)
    qc.barrier()

    if bits in ("01", "11"):   # Alice encodes on her qubit only
        qc.x(0)
    if bits in ("10", "11"):
        qc.z(0)
    qc.barrier()

    qc.cx(0, 1)                # Bob undoes the Bell circuit and measures
    qc.h(0)
    qc.measure([0, 1], [0, 1])
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
