"""Shor's algorithm for N = 15, targeted at real IBM Quantum hardware.

    uv run python 04_Algorithms/shors_15_ibm.py                  # dry run, no job
    uv run python 04_Algorithms/shors_15_ibm.py --counting 4     # shallower circuit
    uv run python 04_Algorithms/shors_15_ibm.py --submit         # really queue a job

The algorithm is identical to shors_15.py -- the circuit is imported from it, so
the two cannot drift apart. What is added here is everything hardware needs:
authentication, backend selection, transpilation to the backend's ISA, and error
suppression.

SAFETY: --dry-run is the default. It transpiles against a local fake backend with
the same topology and gate set as a real device, reports the cost, and submits
nothing. Only --submit queues a job against your account's quota.

CREDENTIALS: kept in the vault's .env file, which is gitignored. Set it up once:

    cp .env.example .env        # then paste your token into .env
    uv run python _scripts/ibm_account.py    # verify it is read correctly

The token is passed straight to QiskitRuntimeService and never written anywhere
else, so it lives in exactly one file that git will not touch.
"""

import argparse
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "_scripts"))
from shors_15 import (  # noqa: E402
    N, N_WORK, VALID_A, c_amod15, factors_from_period, qft_dagger,
)

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: E402


def period_circuit(a: int, n_count: int) -> QuantumCircuit:
    """Same construction as shors_15.py, with the counting register size exposed.

    On hardware the counting register is the main cost knob: each extra counting
    qubit doubles the modular-exponentiation work and adds another controlled
    permutation, so depth grows fast. Fewer counting qubits means a coarser phase
    estimate, but a circuit that might actually survive the noise.
    """
    qc = QuantumCircuit(n_count + N_WORK, n_count)
    for q in range(n_count):
        qc.h(q)
    qc.x(n_count)
    for q in range(n_count):
        qc.append(c_amod15(a, q), [q] + list(range(n_count, n_count + N_WORK)))
    qc.compose(qft_dagger(n_count), range(n_count), inplace=True)
    qc.measure(range(n_count), range(n_count))
    return qc


def median_2q_error(backend) -> float | None:
    """Median two-qubit gate error from the backend's calibration data."""
    errs = []
    for name in ("cz", "ecr", "cx"):
        if name in backend.target:
            errs += [p.error for p in backend.target[name].values()
                     if p is not None and p.error is not None]
    if not errs:
        return None
    errs.sort()
    return errs[len(errs) // 2]


def report_cost(isa, backend, n_count: int) -> None:
    ops = isa.count_ops()
    two_q = sum(n for g, n in ops.items() if g in ("cz", "cx", "ecr", "cy"))
    print(f"  backend          {backend.name} ({backend.num_qubits} qubits)")
    print(f"  counting qubits  {n_count}  ->  {n_count + N_WORK} logical qubits")
    print(f"  ISA depth        {isa.depth()}")
    print(f"  two-qubit gates  {two_q}")
    print(f"  total gates      {sum(ops.values())}")
    print(f"  op breakdown     {dict(sorted(ops.items(), key=lambda kv: -kv[1]))}")

    err = median_2q_error(backend)
    if err:
        survival = (1 - err) ** two_q
        print(f"\n  median 2q error  {err:.2e}")
        print(f"  rough fidelity   (1 - {err:.1e})^{two_q} = {survival:.2%}")
        if survival < 0.01:
            print("  -> essentially pure noise. Reduce --counting.")
        elif survival < 0.25:
            print("  -> marginal. Expect a weak signal above a noisy floor.")
        else:
            print("  -> plausible. The period may well be recoverable.")


def ideal_support(a: int, n_count: int) -> set[str]:
    """Bitstrings a noiseless run can produce, from exact simulation."""
    from qiskit.primitives import StatevectorSampler
    qc = period_circuit(a, n_count)
    counts = StatevectorSampler().run([qc], shots=8192).result()[0].data.c.get_counts()
    return {k for k, v in counts.items() if v > 8192 * 0.01}


def provenance(job, backend) -> None:
    """Everything that proves where this ran. None of it comes from us."""
    cfg = getattr(backend, "configuration", lambda: None)()
    is_sim = getattr(cfg, "simulator", None)
    print("\nProvenance -- reported by IBM, not by this script:")
    print(f"  job id      {job.job_id()}")
    print(f"  backend     {backend.name}")
    print(f"  simulator   {is_sim if is_sim is not None else 'unknown'}"
          f"{'   <-- NOT real hardware!' if is_sim else ''}")
    print(f"  qubits      {backend.num_qubits}")
    print(f"  status      {job.status()}")
    for label, value in (("created", getattr(job, "creation_date", None)),
                         ("instance", getattr(job, "instance", None)),
                         ("primitive", getattr(job, "primitive_id", None))):
        if value:
            print(f"  {label:<11} {value}")
    try:
        usage = job.usage()
        print(f"  usage       {usage}")
    except Exception:
        pass
    print(f"\n  Cross-check independently at https://quantum.cloud.ibm.com/workloads")
    print(f"  by searching for job {job.job_id()}. If it is not listed there,")
    print(f"  it did not run on IBM hardware.")


def verify_quantum(counts: dict[str, int], a: int, n_count: int) -> None:
    """Did the device do something a coin flip could not?

    A noiseless run only ever produces bitstrings in the 'ideal support'. Uniform
    noise spreads over all 2^n. So the fraction of shots landing on the support,
    compared against what uniform noise would give, measures whether anything
    quantum actually happened.
    """
    support = ideal_support(a, n_count)
    total = sum(counts.values())
    on = sum(v for k, v in counts.items() if k in support)
    frac = on / total
    baseline = len(support) / 2**n_count

    print("\nDid the hardware actually compute anything?")
    print(f"  ideal outcomes    {sorted(support)}")
    print(f"  on-support shots  {on}/{total} = {frac:.1%}")
    print(f"  uniform noise     would give {baseline:.1%}")

    if baseline >= 0.999:
        print("\n  INCONCLUSIVE. With this few counting qubits every bitstring is a")
        print("  valid outcome, so random noise scores 100% too. This run cannot")
        print("  distinguish a quantum computer from a coin flip. Use --counting 3")
        print("  or more if you want the result to be evidence of anything.")
        return

    sigma = (baseline * (1 - baseline) / total) ** 0.5
    z = (frac - baseline) / sigma if sigma else 0.0
    print(f"  excess            {frac - baseline:+.1%}  ({z:.1f} sigma)")

    # Back out the fidelity the data implies: f*1 + (1-f)*baseline = frac.
    eff = (frac - baseline) / (1 - baseline)
    print(f"  implied fidelity  {eff:.1%} of shots were coherent")

    # Uniform depolarising noise spreads evenly. If instead the errors pile onto
    # one output bit, a single qubit or its readout is the culprit, which is a
    # far more fixable problem than "the circuit is too deep".
    n_bits = len(next(iter(counts)))
    ideal_bit = [{k[i] for k in support} for i in range(n_bits)]
    print("\n  error by output bit (leftmost first):")
    for i in range(n_bits):
        ones = sum(v for k, v in counts.items() if k[i] == "1") / total
        if len(ideal_bit[i]) == 1:                      # this bit is fixed ideally
            want = float(ideal_bit[i].pop())
            print(f"    bit {i}: P(1) = {ones:5.1%}   should be {want:.0%}"
                  f"   {'<-- RANDOMISED' if abs(ones - want) > 0.35 else ''}")
        else:
            print(f"    bit {i}: P(1) = {ones:5.1%}   should be ~50% (free)")
    if z > 5:
        print("\n  Decisive: far more concentrated than noise could explain.")
    elif z > 3:
        print("\n  Significant: the device is doing real work, though noisily.")
    else:
        print("\n  Not distinguishable from noise. The circuit is too deep for this")
        print("  device; try fewer counting qubits or more shots.")


def verify_answer(a: int, r: int, f1: int, f2: int) -> bool:
    """Check the answer classically. This is why you never have to trust the QPU."""
    print("\nVerifying the answer classically -- no trust in the QPU required:")
    checks = [
        (f"{a}^{r} mod {N} == 1", pow(a, r, N) == 1),
        (f"{f1} x {f2} == {N}", f1 * f2 == N),
        ("both factors non-trivial", 1 not in (f1, f2) and N not in (f1, f2)),
        (f"{f1} divides {N}", N % f1 == 0),
    ]
    for label, ok in checks:
        print(f"  [{'ok' if ok else 'FAIL'}] {label}")
    return all(ok for _, ok in checks)


def analyse(counts: dict[str, int], a: int, n_count: int) -> int | None:
    """Identical post-processing to the simulator version."""
    support = ideal_support(a, n_count)
    print(f"\n  {'measured':>12}  {'phase':>8}  {'~ s/r':>7}  {'r':>3}  {'a^r=1':>6}  "
          f"{'ideal':>6}  shots")
    candidates: dict[int, int] = {}
    signal = 0
    for bits, n in sorted(counts.items(), key=lambda kv: -kv[1])[:16]:
        phase = int(bits, 2) / 2**n_count
        frac = Fraction(phase).limit_denominator(N)
        r = frac.denominator
        ok = r > 1 and pow(a, r, N) == 1
        real = bits in support
        print(f"  {bits:>12}  {phase:>8.4f}  {str(frac):>7}  {r:>3}  {str(ok):>6}  "
              f"{str(real):>6}  {n}")
        if ok:
            candidates[r] = candidates.get(r, 0) + n
            if real:
                signal += n
    if not candidates:
        return None

    total = sum(counts.values())
    passed = sum(candidates.values())
    print(f"\n  {passed}/{total} ({100*passed/total:.1f}%) pass the a^r = 1 check,")
    print(f"  but only {signal}/{total} ({100*signal/total:.1f}%) of those are on the "
          f"ideal support.")
    if passed > signal * 1.3:
        print("\n  Careful: a^r = 1 holds for any MULTIPLE of the true period, so pure\n"
              "  noise passes it too. The on-support figure is the honest one; the\n"
              "  first number flatters the run.")
    return min(candidates)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a", type=int, default=2, choices=VALID_A, help="base (default 2)")
    ap.add_argument("--counting", type=int, default=3,
                    help="counting qubits. 8 is textbook but pure noise on hardware; "
                         "2 is cheapest but unverifiable (noise scores 100%%); 3 is the "
                         "sweet spot, cheap enough to run and still falsifiable "
                         "(default 3)")
    ap.add_argument("--job", default=None,
                    help="fetch a previously submitted job by id instead of running one")
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--opt-level", type=int, default=3, choices=range(4),
                    help="transpiler optimization level (default 3)")
    ap.add_argument("--submit", action="store_true",
                    help="actually queue a job on real hardware; without it this is a dry run")
    ap.add_argument("--backend", default=None, help="backend name; default is least busy")
    args = ap.parse_args()

    if args.job:
        from ibm_account import get_service
        service = get_service()
        job = service.job(args.job)
        print(f"Retrieved job {args.job}: status {job.status()}")
        if not job.done():
            print("Not finished yet. Run again when it is.")
            return
        provenance(job, job.backend())
        counts = job.result()[0].data.c.get_counts()
        n_count = len(next(iter(counts)))
        verify_quantum(counts, args.a, n_count)
        finish(counts, args.a, n_count)
        return

    qc = period_circuit(args.a, args.counting)
    print(f"Shor for N = {N}, a = {args.a}, {args.counting} counting qubits")
    print(f"Logical circuit depth {qc.depth()}\n")

    if not args.submit:
        from qiskit_ibm_runtime.fake_provider import FakeTorino
        backend = FakeTorino()
        print("DRY RUN -- transpiling against a local fake backend, submitting nothing.\n")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=args.opt_level)
        report_cost(pm.run(qc), backend, args.counting)
        print("\nRe-run with --submit to queue this on real hardware.")
        return

    from ibm_account import describe, get_service
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    print("Credentials:")
    describe()
    print()
    service = get_service()
    backend = (service.backend(args.backend) if args.backend
               else service.least_busy(simulator=False, operational=True))
    print(f"Authenticated. Connected to: {backend.name}\n")

    pm = generate_preset_pass_manager(backend=backend, optimization_level=args.opt_level)
    isa = pm.run(qc)
    report_cost(isa, backend, args.counting)

    sampler = Sampler(mode=backend)
    # Error suppression. Dynamical decoupling idles qubits with pulse sequences that
    # cancel low-frequency noise; twirling randomises coherent gate errors into
    # incoherent ones, which average out over shots.
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.dynamical_decoupling.sequence_type = "XY4"
    sampler.options.twirling.enable_gates = True
    sampler.options.twirling.enable_measure = True

    print(f"\nSubmitting {args.shots} shots...")
    job = sampler.run([(isa, None, args.shots)])
    print(f"  job id: {job.job_id()}   (re-read later with --job {job.job_id()})")
    counts = job.result()[0].data.c.get_counts()

    provenance(job, backend)
    verify_quantum(counts, args.a, args.counting)
    finish(counts, args.a, args.counting)


def finish(counts: dict[str, int], a: int, n_count: int) -> None:
    r = analyse(counts, a, n_count)
    if r is None:
        print("\nNo usable period survived the noise. Try fewer counting qubits.")
        return
    print(f"\nPeriod r = {r}")
    result = factors_from_period(a, r)
    if result is None:
        print(f"r = {r} is unusable for a = {a}; pick another base.")
        return
    f1, f2 = result
    if verify_answer(a, r, f1, f2):
        print(f"\n{N} = {f1} x {f2}   -- verified")
    else:
        print(f"\nGot {f1} x {f2}, but it does not check out. Treat as noise.")


if __name__ == "__main__":
    main()
