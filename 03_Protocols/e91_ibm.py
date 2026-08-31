"""E91 key distribution, targeted at real IBM Quantum hardware.

    uv run python 03_Protocols/e91_ibm.py                  # dry run, no job
    uv run python 03_Protocols/e91_ibm.py --eve            # dry run, Eve on the line
    uv run python 03_Protocols/e91_ibm.py --submit         # really queue a job
    uv run python 03_Protocols/e91_ibm.py --job <id>       # re-read a past job

The protocol is identical to e91.py -- the round is imported from it, so the two
cannot drift apart. What is added here is what hardware needs: authentication,
backend selection, transpilation, error suppression, and the packing that turns
all nine (or eighteen) configurations into a single circuit.

SAFETY: a dry run is the default. It transpiles against a local fake backend with
a real device's topology and gate set, reports the cost, and submits nothing. Only
--submit queues a job against your account's quota.

CREDENTIALS: kept in the vault's .env file, which is gitignored. Set it up once:

    cp .env.example .env        # then paste your token into .env
    uv run python _scripts/ibm_account.py    # verify it is read correctly

WHY THIS ONE ACTUALLY WORKS ON HARDWARE. Shor's algorithm needs thousands of
two-qubit gates and today's devices deliver noise. An E91 round needs one
entangling gate and two rotations, so it is about the shallowest useful circuit
there is, and the CHSH violation is one of the few textbook quantum effects a
current machine reproduces convincingly. Expect S somewhere around 2.4 to 2.7
rather than 2.83 -- comfortably past the classical bound of 2, and visibly short of
what a perfect device would give.

That gap is the honest difficulty of QKD on real hardware: noise pushes S down in
exactly the direction an eavesdropper does. The protocol cannot tell them apart,
and answers by blaming all of it on Eve. Run once without --eve to see where the
device sits on its own; that is the number every later run is read against.
"""

import argparse
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "_scripts"))
from e91 import (  # noqa: E402
    CHSH_TERMS, CLASSICAL_BOUND, EVE_S, FIELDS, KEY_SETTINGS, TSIRELSON,
    analyse, correlation, draw_rounds, emit_round, ideal_correlation,
)
from qkd import chunk, deal, pack, pools_from, positive_int  # noqa: E402

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: E402


def pack_e91(configs: list[tuple]):
    """Pack these configurations into one wide circuit.

    Two qubits per round for the entangled pair, three when Eve is on the line and
    needs a probe to keep. See qkd.pack for why this is worth doing at all; the
    saving is larger here than for BB84, because 18 configurations at 3 qubits each
    still fit comfortably on one 127-qubit device.
    """
    eve = configs[0][2] is not None
    return pack(
        configs,
        lambda qc, config, qubits: emit_round(qc, config, qubits[0], qubits[1],
                                              qubits[2] if eve else None),
        width=3 if eve else 2,
        measured={"alice": 0, "bob": 1, "eve": 2} if eve else {"alice": 0, "bob": 1},
    )


# --------------------------------------------------------------------------
# Cost and diagnostics
# --------------------------------------------------------------------------

def report_cost(isas, backend, configs, shots: int) -> None:
    from ibm_account import median_error

    depth = max(isa.depth() for isa in isas)
    two_q = sum(n for isa in isas for g, n in isa.count_ops().items()
                if g in ("cz", "cx", "ecr", "cy"))
    print(f"  backend           {backend.name} ({backend.num_qubits} qubits)")
    print(f"  configurations    {len(configs)} packed into {len(isas)} circuit(s)")
    print(f"  qubits used       {len(configs) * (3 if configs[0][2] else 2)}")
    print(f"  shots             {shots}   (one per round wanting the busiest config)")
    print(f"  ISA depth         {depth}")
    print(f"  two-qubit gates   {two_q}")

    gate = median_error(backend, "cz", "ecr", "cx")
    readout = median_error(backend, "measure")
    if gate:
        print(f"\n  median 2q error   {gate:.2e}")
    if readout:
        print(f"  median readout    {readout:.2e}")

    # Each correlation is the product of two measured bits, so either one being
    # misread flips it. To first order every E is scaled by (1-2p)^2 for readout
    # error p, and S scales with it -- which is a real prediction the run tests.
    if readout is not None and gate is not None:
        shrink = (1 - 2 * readout) ** 2 * (1 - gate)
        print(f"\n  predicted S       {TSIRELSON:.3f} x {shrink:.3f} = "
              f"{TSIRELSON * shrink:.3f}")
        print(f"  classical bound   {CLASSICAL_BOUND:.3f}")
        if TSIRELSON * shrink > CLASSICAL_BOUND + 0.15:
            print("  -> the violation should survive comfortably on this device.")
        elif TSIRELSON * shrink > CLASSICAL_BOUND:
            print("  -> marginal. The violation may not clear the bound significantly.")
        else:
            print("  -> this device would fail its own clean channel. Try --backend.")


def pair_quality(pools: dict[tuple, list]) -> None:
    """How good is each entangled pair, measured setting by setting?

    Every configuration sits on its own qubits, so a single bad pair or a badly
    routed two-qubit gate shows up as one bad row rather than a uniformly low S.
    The rightmost column is what matters: a large gap between measured and ideal
    on one row is a placement problem, and the same gap on every row is the device.
    """
    order = sorted(pools)
    eve = order[0][2] is not None
    print("\nCorrelation per configuration, against what it should be:")
    header = f"  {'setting':>9}"
    if eve:
        header += f" {'e.base':>6}"
    print(header + f"  {'slot':>4}  {'rounds':>6}  {'measured':>8}  {'ideal':>7}  gap")

    gaps = []
    for config in order:
        samples = pools[config]
        measured = correlation(samples)
        ideal = ideal_correlation(config[0], config[1], eve)
        gap = abs(measured - ideal)
        gaps.append(gap)
        row = f"  {f'A{config[0] + 1},B{config[1] + 1}':>9}"
        if eve:
            row += f" {config[2]:>6}"
        print(row + f"  {order.index(config):>4}  {len(samples):>6}  {measured:>+8.3f}"
                    f"  {ideal:>+7.3f}  {gap:>5.3f}")

    print(f"\n  worst gap {max(gaps):.3f}, median {sorted(gaps)[len(gaps) // 2]:.3f}")
    if max(gaps) > 3 * (sorted(gaps)[len(gaps) // 2] + 0.02):
        print("  -> one configuration is far worse than the rest: a bad qubit pair,")
        print("     not the protocol. Retry with --backend on another device.")


def hardware_verdict(stats: dict, eve: bool) -> None:
    """Noise and Eve both push S down. Which one is this?"""
    s, sigma = stats["s"], stats["sigma"]
    print("\nNoise or an eavesdropper?")
    print(f"  measured S        {s:.3f} +/- {sigma:.3f}")
    for label, predicted in (("perfect pairs   ", TSIRELSON),
                             ("classical bound ", CLASSICAL_BOUND),
                             ("Eve on the line ", EVE_S)):
        print(f"  vs {label}  {predicted:.3f}, measured is "
              f"{abs(s - predicted) / sigma:>5.1f} sigma away")

    print(f"\n  Eve was actually {'PRESENT' if eve else 'ABSENT'} in this run "
          f"(--eve {'on' if eve else 'off'}), which is the")
    print("  one thing a real Alice and Bob would not know.")

    if not eve and stats["violated"]:
        print(f"\n  S = {s:.3f} on real hardware is this device's honest ceiling. Any")
        print("  later run has to be read against it, not against 2.828.")
    elif not eve:
        print("\n  The device could not violate the inequality even with nobody")
        print("  listening. Nothing can be concluded from an --eve run on it.")
    elif not stats["violated"]:
        print("\n  Correctly rejected. Note that the protocol did not need to know")
        print("  whether the drop came from Eve or from noise -- it refuses either way,")
        print("  which is what makes the refusal safe.")


# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Exposed so _scripts/check_docs.py can verify COMMANDS.md against it."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rounds", type=positive_int, default=2048,
                    help="entangled pairs distributed. Only 2/9 become key bits and "
                         "4/9 test the inequality (default 2048)")
    ap.add_argument("--eve", action="store_true",
                    help="let an eavesdropper entangle herself with Alice's qubit")
    ap.add_argument("--table", type=int, default=12,
                    help="how many individual rounds to print, 0 for none (default 12)")
    ap.add_argument("--seed", type=int, default=0,
                    help="seed for every classical choice. The same seed reproduces "
                         "the same run, which is what makes --job re-readable "
                         "(default 0)")
    ap.add_argument("--job", default=None,
                    help="fetch a previously submitted job by id instead of running one")
    ap.add_argument("--submit", action="store_true",
                    help="actually queue a job on real hardware; without it this is "
                         "a dry run")
    ap.add_argument("--backend", default=None, help="backend name; default is least busy")
    ap.add_argument("--opt-level", type=int, default=3, choices=range(4),
                    help="transpiler optimization level (default 3)")
    return ap


def finish(pools, rounds, args) -> None:
    """Everything after the quantum part, identical to the simulated version."""
    pair_quality(pools)
    stats = analyse(rounds, deal(rounds, pools), table=args.table,
                    eve_present=args.eve,
                    floor="a real device lands short of 2.828 even with nobody listening")
    hardware_verdict(stats, args.eve)


def main() -> None:
    args = build_parser().parse_args()

    # Every classical choice comes from the seed, so the rounds drawn here are the
    # same ones the submitted job was built for. That is what lets --job re-read a
    # result days later and still deal the shots to the rounds that asked for them.
    rng = random.Random(args.seed)
    rounds = draw_rounds(args.rounds, args.eve, rng)
    need = Counter(rounds)
    configs = sorted(need)
    shots = max(need.values())
    width = 3 if args.eve else 2

    key_rounds = sum(1 for r in rounds if (r[0], r[1]) in KEY_SETTINGS)
    test_rounds = sum(1 for r in rounds if (r[0], r[1]) in CHSH_TERMS)
    print(f"E91 over {args.rounds} pairs, eavesdropper: {'yes' if args.eve else 'no'}")
    print(f"{len(configs)} distinct configurations, {shots} shots each "
          f"-> {key_rounds} key rounds and {test_rounds} test rounds")
    print(f"Seed {args.seed}; pass the same --seed and --eve to re-read this with --job.")

    if args.job:
        from ibm_account import get_service, provenance
        job = get_service().job(args.job)
        print(f"\nRetrieved job {args.job}: status {job.status()}")
        if not job.done():
            print("Not finished yet. Run again when it is.")
            return
        provenance(job, job.backend())
        result = job.result()
        # Regroup exactly as submission did, so slot i of circuit k is the same
        # configuration it was when the job was built.
        groups = chunk(configs, max(job.backend().num_qubits // width, 1))
        finish(pools_from([r.data for r in result], groups, FIELDS), rounds, args)
        return

    if not args.submit:
        from qiskit_ibm_runtime.fake_provider import FakeTorino
        backend = FakeTorino()
        print("\nDRY RUN -- transpiling against a local fake backend, submitting "
              "nothing.\n")
    else:
        from ibm_account import describe, get_service
        from qiskit_ibm_runtime import SamplerV2 as Sampler

        print("\nCredentials:")
        describe()
        service = get_service()
        backend = (service.backend(args.backend) if args.backend
                   else service.least_busy(simulator=False, operational=True))
        print(f"\nAuthenticated. Connected to: {backend.name}\n")

    groups = chunk(configs, max(backend.num_qubits // width, 1))
    pm = generate_preset_pass_manager(backend=backend, optimization_level=args.opt_level)
    isas = [pm.run(pack_e91(group)) for group in groups]
    report_cost(isas, backend, configs, shots)

    if not args.submit:
        print("\nRe-run with --submit to queue this on real hardware.")
        return

    sampler = Sampler(mode=backend)
    # Dynamical decoupling idles qubits with pulse sequences that cancel low-frequency
    # noise; twirling randomises coherent errors into incoherent ones, which average
    # out over shots. Measurement twirling earns its keep here: a correlation is a
    # product of two measured bits, so readout bias hits S twice over.
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.dynamical_decoupling.sequence_type = "XY4"
    sampler.options.twirling.enable_gates = True
    sampler.options.twirling.enable_measure = True

    print(f"\nSubmitting {shots} shots...")
    job = sampler.run([(isa, None, shots) for isa in isas])
    print(f"  job id: {job.job_id()}   (re-read later with --job {job.job_id()})")
    result = job.result()

    from ibm_account import provenance
    provenance(job, backend)
    finish(pools_from([r.data for r in result], groups, FIELDS), rounds, args)


if __name__ == "__main__":
    main()
