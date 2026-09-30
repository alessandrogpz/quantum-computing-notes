"""The gates from these notes, built in Qiskit.

    python gates.py            # all of them
    python gates.py --gate H   # just one

Each gate is printed as its matrix, checked against the matrix written in the
notes, and shown acting on a state. Simulator only -- none of this needs IBM.
"""

import argparse

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

R2 = 1 / np.sqrt(2)

# The matrices as written in the notes, to check Qiskit against.
EXPECTED = {
    "I": np.array([[1, 0], [0, 1]]),
    "X": np.array([[0, 1], [1, 0]]),
    "Y": np.array([[0, -1j], [1j, 0]]),          # complex Pauli Y, not the real one
    "Z": np.array([[1, 0], [0, -1]]),
    "H": R2 * np.array([[1, 1], [1, -1]]),
    "CNOT": np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]]),
    "SWAP": np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]),
}

# How to build each gate, and how wide a circuit it needs.
BUILD = {
    "I": (1, lambda qc: qc.id(0)),
    "X": (1, lambda qc: qc.x(0)),
    "Y": (1, lambda qc: qc.y(0)),
    "Z": (1, lambda qc: qc.z(0)),
    "H": (1, lambda qc: qc.h(0)),
    "CNOT": (2, lambda qc: qc.cx(0, 1)),
    "SWAP": (2, lambda qc: qc.swap(0, 1)),
    "Toffoli": (3, lambda qc: qc.ccx(0, 1, 2)),
    "Fredkin": (3, lambda qc: qc.cswap(0, 1, 2)),
}


def matrix(name: str) -> np.ndarray:
    n, build = BUILD[name]
    qc = QuantumCircuit(n)
    build(qc)
    return np.asarray(Operator(qc))


def show_matrix(m: np.ndarray) -> str:
    def cell(z):
        z = complex(z)
        if abs(z.imag) < 1e-9:
            return f"{z.real:6.3f}".rstrip("0").rstrip(".").rjust(6)
        return f"{z.real:+.2f}{z.imag:+.2f}j".rjust(6)
    return "\n".join("      [" + "  ".join(cell(z) for z in row) + "]" for row in m)


def truth_table(name: str) -> None:
    """The classical truth table, written in the notes' bit order.

    Qiskit is little-endian, so its bitstrings read q_{n-1}...q_0 while the notes
    write the control first, as (x, y, z). Both the input and the output are
    reversed here so the table matches the notes rather than Qiskit's display.
    """
    n, build = BUILD[name]
    labels = "xyz"[:n]
    print(f"      {labels}  ->  out")
    for i in range(2**n):
        bits = format(i, f"0{n}b")          # x, y, z left to right
        qc = QuantumCircuit(n)
        for q, bit in enumerate(bits):      # qubit 0 is x
            if bit == "1":
                qc.x(q)
        build(qc)
        probs = Statevector(qc).probabilities_dict()
        out = max(probs, key=probs.get)[::-1]
        print(f"      {bits}  ->  {out}")


def report(name: str) -> None:
    print(f"\n{name}")
    m = matrix(name)
    print(show_matrix(m))

    if name in EXPECTED:
        same = np.allclose(m, EXPECTED[name])
        print(f"      matches the notes: {'yes' if same else 'NO'}")

    n, _ = BUILD[name]
    if n == 1:
        for label, state in (("|0>", [1, 0]), ("|1>", [0, 1])):
            out = m @ np.array(state)
            print(f"      {name}{label} = {np.round(out, 3).tolist()}")
    else:
        truth_table(name)

    # An involution returns its input when applied twice.
    print(f"      involution (U^2 = I): "
          f"{'yes' if np.allclose(m @ m, np.eye(len(m))) else 'no'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--gate", choices=list(BUILD), help="show only this gate")
    args = ap.parse_args()

    for name in ([args.gate] if args.gate else BUILD):
        report(name)

    print("\nNote: Qiskit's Y is the complex Pauli Y. The real-valued Y used in")
    print("these notes squares to -I, so it is not an involution. See")
    print("01_Foundations/Real_vs_Complex_Amplitudes.md")


if __name__ == "__main__":
    main()
