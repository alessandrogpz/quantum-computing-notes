"""Shor's algorithm factoring N = 15.

    python shors.py                 # local simulator
    python shors.py --ibm           # real IBM hardware
    python shors.py --a 7           # a different base

Only the period-finding step is quantum. Picking a base, turning the period into
factors, and checking the answer are all ordinary arithmetic.
"""

import argparse
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "_scripts"))
from backend import run  # noqa: E402

from qiskit import QuantumCircuit  # noqa: E402

N = 15
N_WORK = 4              # qubits holding a^x mod 15, since 15 < 2^4
VALID_A = (2, 4, 7, 8, 11, 13)


def c_amod15(a: int, power: int):
    """Controlled multiplication by a^(2^power) mod 15.

    Multiplying by a mod 15 only permutes the four work qubits, so this needs
    nothing but SWAPs and Xs. That is what keeps N = 15 small enough to write by
    hand, and also why this is a demonstration rather than general factoring.
    """
    u = QuantumCircuit(N_WORK)
    for _ in range(2**power):
        if a in (2, 13):
            u.swap(2, 3), u.swap(1, 2), u.swap(0, 1)
        if a in (7, 8):
            u.swap(0, 1), u.swap(1, 2), u.swap(2, 3)
        if a in (4, 11):
            u.swap(1, 3), u.swap(0, 2)
        if a in (7, 11, 13):
            for q in range(N_WORK):
                u.x(q)
    gate = u.to_gate()
    gate.name = f"{a}^{2**power} mod 15"
    return gate.control()


def qft_dagger(n: int) -> QuantumCircuit:
    """Inverse quantum Fourier transform.

    The phases here are e^(-i.pi/2^k), which is why Shor's cannot be written with
    the real amplitudes used elsewhere in these notes.
    """
    qc = QuantumCircuit(n)
    for q in range(n // 2):
        qc.swap(q, n - q - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / 2 ** (j - m), m, j)
        qc.h(j)
    return qc


def circuit(a: int, n_count: int) -> QuantumCircuit:
    """Phase estimation on the "multiply by a mod 15" operator."""
    qc = QuantumCircuit(n_count + N_WORK, n_count)
    for q in range(n_count):
        qc.h(q)                       # every exponent x at once
    qc.x(n_count)                     # work register starts at |1>
    for q in range(n_count):
        qc.append(c_amod15(a, q), [q] + list(range(n_count, n_count + N_WORK)))
    qc.compose(qft_dagger(n_count), range(n_count), inplace=True)
    qc.measure(range(n_count), range(n_count))
    return qc


def find_period(counts: dict[str, int], a: int, n_count: int) -> int | None:
    """Turn measured phases into the period r using continued fractions."""
    print(f"  {'measured':>10} {'phase':>8} {'~ s/r':>7} {'r':>4}  shots")
    candidates = {}
    for bits, n in sorted(counts.items(), key=lambda kv: -kv[1])[:8]:
        phase = int(bits, 2) / 2**n_count
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        print(f"  {bits:>10} {phase:>8.3f} {str(frac):>7} {r:>4}  {n}")
        if r > 1 and pow(a, r, N) == 1:
            candidates[r] = candidates.get(r, 0) + n
    return min(candidates) if candidates else None


def factors(a: int, r: int) -> tuple[int, int] | None:
    """r must be even, and a^(r/2) must not be -1 mod N, or this base is useless."""
    if r % 2:
        return None
    root = pow(a, r // 2, N)
    if root == N - 1:
        return None
    f1, f2 = math.gcd(root - 1, N), math.gcd(root + 1, N)
    return (f1, f2) if f1 * f2 == N and 1 not in (f1, f2) else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a", type=int, default=2, choices=VALID_A, help="base (default 2)")
    ap.add_argument("--ibm", action="store_true", help="run on real IBM hardware")
    ap.add_argument("--counting", type=int, default=3,
                    help="counting qubits: more precision, deeper circuit (default 3)")
    ap.add_argument("--shots", type=int, default=2048)
    args = ap.parse_args()

    a = args.a
    print(f"Factoring {N} with a = {a}\n")

    g = math.gcd(a, N)
    if g != 1:
        print(f"gcd({a}, {N}) = {g}, a lucky classical hit. No quantum needed.")
        return

    counts = run(circuit(a, args.counting), shots=args.shots, ibm=args.ibm)
    r = find_period(counts, a, args.counting)
    if r is None:
        print("\nNo usable period found.")
        return
    print(f"\nPeriod r = {r}, since {a}^{r} mod {N} = {pow(a, r, N)}")

    result = factors(a, r)
    if result is None:
        print(f"r = {r} gives no useful factors for a = {a}. Try another base.")
        return

    f1, f2 = result
    half = pow(a, r // 2, N)
    print(f"gcd({half} - 1, {N}) = {f1} and gcd({half} + 1, {N}) = {f2}")
    print(f"\n{N} = {f1} x {f2}" + ("" if f1 * f2 == N else "  [WRONG]"))


if __name__ == "__main__":
    main()
