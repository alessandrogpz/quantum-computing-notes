"""Shor's algorithm factoring N = 15, end to end.

    uv run python 04_Algorithms/shors_15.py
    uv run python 04_Algorithms/shors_15.py --a 7 --shots 2048

Companion to Shors_Algorithm.md. Everything here is simulated exactly with
Qiskit's built-in statevector sampler -- no Aer, no hardware, no account.

The only quantum part is find_period(): given a and N it returns the period r of
f(x) = a^x mod N. Everything around it is ordinary number theory that a classical
computer does, and that is the honest shape of the algorithm.
"""

import argparse
import math
from fractions import Fraction

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

N = 15
N_WORK = 4        # qubits holding a^x mod 15, since 15 < 2^4
N_COUNT = 8       # counting qubits; more counting qubits = finer phase estimate

# a values coprime to 15 for which the modular multiplication below is defined.
VALID_A = (2, 4, 7, 8, 11, 13)


# --------------------------------------------------------------------------
# The quantum part
# --------------------------------------------------------------------------

def c_amod15(a: int, power: int) -> "QuantumCircuit":
    """Controlled multiplication by a^(2^power) mod 15.

    For N = 15 specifically, multiplying by a mod 15 permutes the four work
    qubits, so it is built entirely from SWAPs and Xs -- no adders needed. This
    is what makes 15 tractable to write out by hand, and also why it is a
    demonstration rather than a general factoring routine.
    """
    if a not in VALID_A:
        raise ValueError(f"a must be one of {VALID_A}")
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
    """Inverse quantum Fourier transform on n qubits.

    This is the step that cannot be done with real amplitudes: cp(theta) applies
    the phase e^(i*theta), and the angles here are not multiples of pi.
    """
    qc = QuantumCircuit(n)
    for q in range(n // 2):
        qc.swap(q, n - q - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / 2 ** (j - m), m, j)
        qc.h(j)
    qc.name = "QFT+"
    return qc


def period_circuit(a: int) -> QuantumCircuit:
    """Quantum phase estimation on the 'multiply by a mod 15' operator."""
    qc = QuantumCircuit(N_COUNT + N_WORK, N_COUNT)

    for q in range(N_COUNT):
        qc.h(q)                       # uniform superposition over all exponents x
    qc.x(N_COUNT)                     # work register starts at |1>

    for q in range(N_COUNT):          # |x> |1>  ->  |x> |a^x mod 15>
        qc.append(c_amod15(a, q), [q] + list(range(N_COUNT, N_COUNT + N_WORK)))

    qc.compose(qft_dagger(N_COUNT), range(N_COUNT), inplace=True)
    qc.measure(range(N_COUNT), range(N_COUNT))
    return qc


def find_period(a: int, shots: int, verbose: bool = True) -> int | None:
    """Run the circuit and turn measured phases into the period r."""
    result = StatevectorSampler().run([period_circuit(a)], shots=shots).result()
    counts = result[0].data.c.get_counts()

    candidates: dict[int, int] = {}
    if verbose:
        print(f"  {'measured':>10}  {'decimal':>7}  {'phase':>8}  {'~ s/r':>7}  {'r':>3}  shots")
    for bits, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        decimal = int(bits, 2)
        phase = decimal / 2**N_COUNT
        frac = Fraction(phase).limit_denominator(N)   # continued fractions
        r = frac.denominator
        if verbose:
            print(f"  {bits:>10}  {decimal:>7}  {phase:>8.4f}  {str(frac):>7}  {r:>3}  {n}")
        if r > 1 and pow(a, r, N) == 1:
            candidates[r] = candidates.get(r, 0) + n

    return min(candidates) if candidates else None


# --------------------------------------------------------------------------
# The classical part
# --------------------------------------------------------------------------

def factors_from_period(a: int, r: int) -> tuple[int, int] | None:
    """r must be even and a^(r/2) must not be -1 mod N, else this a is useless."""
    if r % 2:
        return None
    root = pow(a, r // 2, N)
    if root == N - 1:
        return None
    f1, f2 = math.gcd(root - 1, N), math.gcd(root + 1, N)
    return (f1, f2) if f1 * f2 == N and 1 not in (f1, f2) else None


def shor(a: int, shots: int) -> None:
    print(f"Factoring N = {N} using a = {a}\n")

    g = math.gcd(a, N)
    if g != 1:
        print(f"gcd({a}, {N}) = {g} -- a lucky classical hit, no quantum needed.")
        return
    print(f"gcd({a}, {N}) = 1, so we need the period of {a}^x mod {N}.\n")

    print("Quantum phase estimation:")
    r = find_period(a, shots)
    if r is None:
        print("\nNo usable period found. Try more shots or a different a.")
        return

    print(f"\nPeriod r = {r}   (check: {a}^{r} mod {N} = {pow(a, r, N)})")

    result = factors_from_period(a, r)
    if result is None:
        print(f"r is odd or a^(r/2) = -1 mod {N}: this a fails, pick another.")
        return

    f1, f2 = result
    half = pow(a, r // 2, N)
    print(f"\n  {a}^({r}/2) mod {N} = {half}")
    print(f"  gcd({half} - 1, {N}) = {f1}")
    print(f"  gcd({half} + 1, {N}) = {f2}")
    print(f"\n{N} = {f1} x {f2}")


def build_parser() -> argparse.ArgumentParser:
    """Exposed so _scripts/check_docs.py can verify COMMANDS.md against it."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a", type=int, default=2, choices=VALID_A,
                    help="the base whose period we find (default 2)")
    ap.add_argument("--shots", type=int, default=1024, help="measurement repetitions")
    return ap


def main() -> None:
    args = build_parser().parse_args()
    shor(args.a, args.shots)


if __name__ == "__main__":
    main()
