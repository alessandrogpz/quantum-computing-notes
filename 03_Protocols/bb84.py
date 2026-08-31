"""BB84 quantum key distribution, with an optional eavesdropper.

    uv run python 03_Protocols/bb84.py                    # clean channel
    uv run python 03_Protocols/bb84.py --eve              # Eve on the line
    uv run python 03_Protocols/bb84.py --rounds 4096 --check 0.25

Companion to BB84.md. Everything here is simulated exactly with Qiskit's built-in
statevector sampler -- no Aer, no hardware, no account.

BB84 does not hide the key. It detects anyone who looks at it: measuring a qubit in
the wrong basis randomises it, and no-cloning forbids keeping a copy while
forwarding the original. So an eavesdropper necessarily leaves errors in bits Alice
and Bob would otherwise agree on, and counting those errors is the whole security
check.
"""

import argparse
import random
from collections import Counter

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qkd import as_hex, deal, positive_int, simulate

# The classical registers every round reports, and the order a dealt sample
# arrives in. Eve's slot is None on a clean channel rather than absent.
FIELDS = ("bob", "eve")

# Z is the rectilinear basis {|0>, |1>}, X the diagonal basis {|+>, |->}. They are
# conjugate: a state that is definite in one is maximally uncertain in the other,
# and that single fact is what the whole protocol rests on.
BASES = ("Z", "X")

# Intercept-resend by an eavesdropper guessing the basis at random corrupts a
# quarter of the sifted bits. BB84's security proof stops working above 11%.
EVE_QBER = 0.25
SHOR_PRESKILL = 0.11


# --------------------------------------------------------------------------
# One round of the protocol
# --------------------------------------------------------------------------
# A "configuration" is everything that decides a round's outcome distribution:
#     (bit, alice_basis, eve_basis, bob_basis)
# with eve_basis = None when the channel is clean.

def emit_round(qc: QuantumCircuit, config: tuple, channel, probe=None) -> None:
    """Write one BB84 round onto the given qubits. Measurement is the caller's job.

    Eve is modelled by the principle of deferred measurement: rather than measuring
    the qubit in flight and re-sending what she found, she copies it onto a probe
    she keeps, and that probe is measured at the end along with everything else. A
    mid-circuit measurement that nothing later depends on gives exactly the same
    statistics, so these are the same attack -- but this version needs no dynamic
    circuits, runs on any backend, and is simulable (StatevectorSampler refuses
    mid-circuit measurements outright).

    It is also the stronger model of an attacker. Eve holding a quantum memory and
    deciding what to do with it later is more powerful than Eve committing to an
    answer immediately, and BB84 survives either way.

    The barriers are load-bearing on hardware. Alice's basis rotation and Bob's are
    both a Hadamard on the same qubit, so a transpiler asked to optimise would
    happily cancel them against each other and measure a qubit nothing was ever
    done to. That is the protocol's algebra, not the protocol: in a real run these
    are three parties separated in space and time, and each rotation is a pulse
    that really happens and can really go wrong. The barriers forbid the shortcut.
    """
    bit, a_basis, e_basis, b_basis = config
    span = [channel] if probe is None else [channel, probe]

    if bit:                          # Alice: |0> or |1> ...
        qc.x(channel)
    if a_basis == "X":               # ... rotated into the diagonal basis if she said X
        qc.h(channel)
    qc.barrier(*span, label="Alice sends")

    if e_basis:                      # Eve: copy the value out in her own basis
        if e_basis == "X":
            qc.h(channel)
        qc.cx(channel, probe)
        if e_basis == "X":
            qc.h(channel)
        qc.barrier(*span, label="Eve")

    if b_basis == "X":               # Bob: bring his basis onto the measurement axis
        qc.h(channel)


def round_circuit(config: tuple) -> QuantumCircuit:
    """One round as a standalone circuit: one qubit, plus Eve's probe if she is on."""
    eve = config[2] is not None
    channel = QuantumRegister(1, "channel")
    probe = QuantumRegister(1, "probe") if eve else None
    c_bob = ClassicalRegister(1, "bob")
    c_eve = ClassicalRegister(1, "eve") if eve else None

    qc = QuantumCircuit(*[r for r in (channel, probe, c_bob, c_eve) if r is not None])
    emit_round(qc, config, channel[0], probe[0] if eve else None)
    qc.measure(channel[0], c_bob[0])
    if eve:
        qc.measure(probe[0], c_eve[0])
    return qc


# --------------------------------------------------------------------------
# Running the rounds
# --------------------------------------------------------------------------

def draw_rounds(n: int, eve: bool, rng: random.Random) -> list[tuple]:
    """Alice's bits and everyone's bases: all the classical randomness of a run."""
    return [(rng.randrange(2),
             rng.choice(BASES),
             rng.choice(BASES) if eve else None,
             rng.choice(BASES))
            for _ in range(n)]


# --------------------------------------------------------------------------
# The classical half: sift, check, keep
# --------------------------------------------------------------------------

def sift(rounds: list[tuple]) -> list[int]:
    """Rounds where Alice and Bob happened to choose the same basis. Half of them."""
    return [i for i, (_, a_basis, _, b_basis) in enumerate(rounds) if a_basis == b_basis]


def print_table(rounds: list[tuple], outcomes: list[tuple], kept: set, n: int) -> None:
    """The textbook picture: a few rounds, spelled out column by column."""
    eve = rounds[0][2] is not None
    print(f"\nFirst {min(n, len(rounds))} rounds:")
    head = f"  {'#':>4}  {'a.bit':>5} {'a.base':>6}"
    if eve:
        head += f"  {'e.base':>6} {'e.bit':>5}"
    print(head + f"  {'b.base':>6} {'b.bit':>5}  {'sifted':>6} {'error':>5}")

    for i in range(min(n, len(rounds))):
        bit, a_basis, e_basis, b_basis = rounds[i]
        b_bit, e_bit = outcomes[i]
        row = f"  {i:>4}  {bit:>5} {a_basis:>6}"
        if eve:
            row += f"  {e_basis:>6} {e_bit:>5}"
        row += f"  {b_basis:>6} {b_bit:>5}  {('yes' if i in kept else 'no'):>6}"
        flag = ("yes" if b_bit != bit else "no") if i in kept else "-"
        print(row + f" {flag:>5}")


def analyse(rounds, outcomes, *, check, threshold, table, rng, floor) -> dict:
    """Print the whole run, and return the numbers the verdict rests on.

    `floor` describes the error rate a clean channel would show here, which is the
    one thing an exact simulator and a real device disagree about.
    """
    sifted = sift(rounds)
    checked = sorted(rng.sample(sifted, int(round(len(sifted) * check))))
    checked_set = set(checked)
    key_idx = [i for i in sifted if i not in checked_set]

    if table:
        print_table(rounds, outcomes, set(sifted), table)

    print("\nSifting -- bases are announced, mismatched rounds are dropped:")
    print(f"  transmitted        {len(rounds)}")
    print(f"  bases agreed       {len(sifted)}  "
          f"({len(sifted) / len(rounds):.1%}, expected 50%)")
    print(f"  sacrificed to test {len(checked)}")
    print(f"  left for the key   {len(key_idx)}")

    errors = sum(1 for i in checked if outcomes[i][0] != rounds[i][0])
    qber = errors / len(checked) if checked else 0.0

    print("\nError check -- the sacrificed bits are announced and compared:")
    print(f"  mismatches         {errors}/{len(checked)} = {qber:.1%}")
    print(f"  clean channel      {floor}")
    print(f"  intercept-resend   would give {EVE_QBER:.0%}")
    print(f"  abort threshold    {threshold:.1%}")
    if checked:
        # Every announced bit is an independent 3-in-4 chance for Eve to slip past.
        print(f"  an Eve who was there survives all {len(checked)} comparisons with "
              f"probability {(1 - EVE_QBER) ** len(checked):.1e}")

    accepted = qber <= threshold
    if accepted:
        print(f"\n  -> ACCEPT. {qber:.1%} is within tolerance, so the key is kept.")
    else:
        print(f"\n  -> ABORT. {qber:.1%} is too high. The key is thrown away and the run"
              f"\n     repeated. Nothing leaked, because nothing was used.")

    # What Eve actually holds. Neither Alice nor Bob can compute this in a real run;
    # it is printed because a demonstration is allowed to look at the answer.
    if rounds[0][2] is not None and key_idx:
        known = sum(1 for i in key_idx if outcomes[i][1] == rounds[i][0])
        print("\nWhat Eve came away with (an oracle's view, not Alice's or Bob's):")
        print(f"  bits of the surviving key she has right  {known}/{len(key_idx)} = "
              f"{known / len(key_idx):.1%}")
        print(f"  guessing at random would give            50.0%")
        print("  She knows a bit for certain whenever she guessed Alice's basis, and")
        print("  gets half of the rest by luck: 0.5 + 0.5 x 0.5 = 75%.")

    alice_key = [rounds[i][0] for i in key_idx]
    bob_key = [outcomes[i][0] for i in key_idx]
    disagree = sum(1 for a, b in zip(alice_key, bob_key) if a != b)

    print(f"\nThe key ({len(alice_key)} bits):")
    print(f"  Alice  {as_hex(alice_key)[:48]}{'...' if len(alice_key) > 192 else ''}")
    print(f"  Bob    {as_hex(bob_key)[:48]}{'...' if len(bob_key) > 192 else ''}")
    print(f"  bits where they disagree: {disagree}")
    if disagree:
        print("  Real BB84 would now run error correction and privacy amplification:")
        print("  classical post-processing that repairs those disagreements and shrinks")
        print("  the key until Eve's expected information about it is negligible. Not")
        print("  implemented here -- this stops where the accept/abort decision is made.")

    return {"sifted": len(sifted), "checked": len(checked), "errors": errors,
            "qber": qber, "accepted": accepted, "key_bits": len(key_idx),
            "disagree": disagree}


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
                    help="seed for every classical choice, so runs reproduce (default 0)")
    return ap


def main() -> None:
    args = build_parser().parse_args()
    rng = random.Random(args.seed)

    print(f"BB84 over {args.rounds} rounds, eavesdropper: {'yes' if args.eve else 'no'}")
    print(f"Simulated exactly. Seed {args.seed}, so the run reproduces.")

    rounds = draw_rounds(args.rounds, args.eve, rng)
    need = Counter(rounds)
    print(f"\n{len(need)} distinct round configurations, {args.rounds} rounds dealt "
          f"from them.")

    outcomes = deal(rounds, simulate(need, rng, round_circuit, FIELDS))
    analyse(rounds, outcomes, check=args.check, threshold=args.threshold,
            table=args.table, rng=rng,
            floor="would give 0% here -- nothing in this simulation is noisy")


if __name__ == "__main__":
    main()
