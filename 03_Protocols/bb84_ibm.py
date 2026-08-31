"""BB84 key distribution, targeted at real IBM Quantum hardware.

    uv run python 03_Protocols/bb84_ibm.py                 # dry run, no job
    uv run python 03_Protocols/bb84_ibm.py --eve           # dry run, Eve on the line
    uv run python 03_Protocols/bb84_ibm.py --submit        # really queue a job
    uv run python 03_Protocols/bb84_ibm.py --job <id>      # re-read a past job

The protocol is identical to bb84.py -- the round is imported from it, so the two
cannot drift apart. What is added here is what hardware needs: authentication,
backend selection, transpilation, error suppression, and one packing trick that
turns the whole protocol into a single circuit.

SAFETY: a dry run is the default. It transpiles against a local fake backend with
a real device's topology and gate set, reports the cost, and submits nothing. Only
--submit queues a job against your account's quota.

CREDENTIALS: kept in the vault's .env file, which is gitignored. Set it up once:

    cp .env.example .env        # then paste your token into .env
    uv run python _scripts/ibm_account.py    # verify it is read correctly

WHAT IS DIFFERENT ABOUT DOING THIS ON HARDWARE: a real channel is noisy, and BB84
cannot tell a noisy photon from an eavesdropped one. Both show up as the same
thing -- errors in the sifted bits. The protocol's honest answer is to blame all of
them on Eve, so a device with a 3% error floor has already spent 3% of its 11%
budget before Eve arrives. Run once without --eve on the backend you intend to use;
that measured floor is the number every later run has to be read against.
"""

import argparse
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "_scripts"))
from bb84 import (  # noqa: E402
    EVE_QBER, FIELDS, SHOR_PRESKILL, analyse, draw_rounds, emit_round, sift,
)
from qkd import chunk, deal, pack, pools_from, positive_int  # noqa: E402

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: E402


def pack_bb84(configs: list[tuple]):
    """Pack these configurations into one wide circuit, Eve's probe included.

    One qubit per round, or two when Eve is on the line and needs a probe to keep.
    See qkd.pack for why the whole protocol is worth collapsing into one circuit.
    """
    eve = configs[0][2] is not None
    return pack(
        configs,
        lambda qc, config, qubits: emit_round(qc, config, qubits[0],
                                              qubits[1] if eve else None),
        width=2 if eve else 1,
        measured={"bob": 0, "eve": 1} if eve else {"bob": 0},
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
    print(f"  shots             {shots}   (one per round wanting the busiest config)")
    print(f"  ISA depth         {depth}")
    print(f"  two-qubit gates   {two_q}")

    gate = median_error(backend, "cz", "ecr", "cx")
    readout = median_error(backend, "measure")
    if gate:
        print(f"\n  median 2q error   {gate:.2e}")
    if readout:
        print(f"  median readout    {readout:.2e}")

    # Unlike Shor, these circuits are two gates deep, so gate error is a rounding
    # error and readout dominates. A misread bit of Bob's IS a sifted-key error,
    # one for one, so his readout error is a direct floor under the QBER. Eve's
    # probe is measured too, but her readout cannot corrupt Bob's bit, so it does
    # not raise the floor -- what she costs is the 25%, which is not noise.
    if readout:
        print(f"\n  expected QBER floor, clean channel  ~{readout:.1%}  (Bob's readout)")
        print(f"  abort threshold                      {SHOR_PRESKILL:.1%}")
        if configs[0][2]:
            print(f"  with Eve on the line, expect roughly {EVE_QBER:.0%} on top of that.")
        if readout > SHOR_PRESKILL:
            print("  -> this device is too noisy: it would abort its own clean channel.")
        elif readout > SHOR_PRESKILL / 2:
            print("  -> marginal. Eve is still detectable, but the margin is thin.")
        else:
            print("  -> fine. Plenty of headroom between the noise floor and 11%.")


def per_config_error(pools: dict[tuple, list]) -> None:
    """Error rate of each configuration whose outcome should be deterministic.

    When Alice and Bob picked the same basis and nobody interfered, Bob's bit is
    forced to equal Alice's -- so on a clean channel these rows read 0%. Every one
    of them lives on its own qubits, which is what makes this table worth printing:
    uniform noise raises all the rows together, while a single bad qubit or a
    crosstalk pair raises exactly one. The first is the device, the second is a
    placement you can escape by rerunning on another backend.

    "slot" is the position in the packed circuit, not a physical qubit -- the
    transpiler chooses the physical layout. It is enough to tell the two failure
    shapes apart, which is all this table is for.
    """
    matched = sorted((c for c in pools if c[1] == c[3]), key=lambda c: (c[1], c[0], c[2]))
    if not matched:
        return
    eve = matched[0][2] is not None
    order = sorted(pools)
    print("\nDisturbance per configuration (matched bases, ideally 0% without Eve):")
    header = f"  {'a.bit':>5} {'basis':>5}"
    if eve:
        header += f" {'e.base':>6}"
    print(header + f"  {'slot':>4}  {'errors':>12}  rate")

    rates = []
    for config in matched:
        samples = pools[config]
        wrong = sum(1 for bob, _ in samples if bob != config[0])
        rate = wrong / len(samples)
        rates.append(rate)
        row = f"  {config[0]:>5} {config[1]:>5}"
        if eve:
            row += f" {config[2]:>6}"
        print(row + f"  {order.index(config):>4}"
                    f"  {f'{wrong}/{len(samples)}':>12}  {rate:>5.1%}")

    spread = max(rates) - min(rates)
    print(f"\n  spread across configurations  {spread:.1%}")
    if spread > 0.15:
        print("  -> one configuration is much worse than the others. That is a bad")
        print("     qubit or a crosstalk pair, not the protocol. Try --backend.")


def hardware_verdict(stats: dict, eve: bool) -> None:
    """Which hypothesis does the measured error rate actually support?

    On a simulator this section would be trivial -- the clean channel gives exactly
    0% and Eve gives exactly 25%. On hardware both hypotheses predict a range, and
    the measured rate has an error bar of its own, so the honest thing is to report
    the distance to each in sigma and let the numbers say which is closer.
    """
    n, qber = stats["checked"], stats["qber"]
    if not n:
        return
    # Binomial standard error on the measured rate itself.
    sigma = max((qber * (1 - qber) / n) ** 0.5, 1e-9)

    print("\nNoise or an eavesdropper?")
    print(f"  measured QBER     {qber:.1%} +/- {sigma:.1%}  ({n} bits compared)")
    for label, predicted in (("clean channel  ", 0.0), ("intercept-resend", EVE_QBER)):
        gap = abs(qber - predicted) / max((predicted * (1 - predicted) / n) ** 0.5, sigma)
        print(f"  vs {label}  predicted {predicted:>5.1%}, measured is {gap:>5.1f} sigma away")

    print(f"\n  Eve was actually {'PRESENT' if eve else 'ABSENT'} in this run "
          f"(--eve {'on' if eve else 'off'}), which is the one thing")
    print("  a real Alice and Bob would not know. Everything above is what they")
    print("  could work out for themselves.")
    if not eve:
        print(f"\n  This run measures the device's own error floor: {qber:.1%}. Any later")
        print("  run on this backend has to beat that before it means anything.")
    elif qber < EVE_QBER / 2:
        print("\n  Well below 25%: either the noise is masking Eve, or too few bits")
        print("  were compared. Raise --rounds.")


# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Exposed so _scripts/check_docs.py can verify COMMANDS.md against it."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rounds", type=positive_int, default=512, help="qubits Alice sends")
    ap.add_argument("--eve", action="store_true",
                    help="put an intercept-resend eavesdropper on the channel")
    ap.add_argument("--check", type=float, default=0.5,
                    help="fraction of the sifted bits spent detecting Eve (default 0.5)")
    ap.add_argument("--threshold", type=float, default=SHOR_PRESKILL,
                    help=f"error rate above which the key is discarded "
                         f"(default {SHOR_PRESKILL})")
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
    per_config_error(pools)
    stats = analyse(rounds, deal(rounds, pools), check=args.check,
                    threshold=args.threshold, table=args.table,
                    rng=random.Random(args.seed + 1),
                    floor="is what a perfect device would give; this one will not")
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

    print(f"BB84 over {args.rounds} rounds, eavesdropper: {'yes' if args.eve else 'no'}")
    print(f"{len(configs)} distinct configurations, {shots} shots each "
          f"-> {len(rounds)} rounds, {len(sift(rounds))} of them sifted")
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
        groups = chunk(configs, max(job.backend().num_qubits // (2 if args.eve else 1), 1))
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

    width = 2 if args.eve else 1
    groups = chunk(configs, max(backend.num_qubits // width, 1))
    pm = generate_preset_pass_manager(backend=backend, optimization_level=args.opt_level)
    isas = [pm.run(pack_bb84(group)) for group in groups]
    report_cost(isas, backend, configs, shots)

    if not args.submit:
        print("\nRe-run with --submit to queue this on real hardware.")
        return

    sampler = Sampler(mode=backend)
    # Dynamical decoupling idles qubits with pulse sequences that cancel low-frequency
    # noise; twirling randomises coherent errors into incoherent ones, which average
    # out over shots. Measurement twirling matters most here -- readout is the
    # dominant error in a circuit this shallow, and it is exactly what a QBER floor
    # is made of.
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
