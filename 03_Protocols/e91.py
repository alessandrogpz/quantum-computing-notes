"""E91 quantum key distribution, with an optional eavesdropper.

    uv run python 03_Protocols/e91.py                    # clean channel
    uv run python 03_Protocols/e91.py --eve              # Eve on the line
    uv run python 03_Protocols/e91.py --rounds 8192

Companion to E91.md. Everything here is simulated exactly with Qiskit's built-in
statevector sampler -- no Aer, no hardware, no account.

Where BB84 detects Eve by noticing that measurement disturbs a state, E91 detects
her by noticing that entanglement has gone missing. Alice and Bob share Bell pairs
and each measure along one of three axes chosen at random. Two of the nine
combinations point along the same axis and give perfectly correlated bits: those
are the key. Four of the others feed the CHSH inequality, whose value no theory in
which the bits existed before they were measured can push past 2. Entanglement
reaches 2*sqrt(2). Any eavesdropper has to break the entanglement to learn
anything, and breaking it drops the number.

The elegant part is that the test costs nothing. BB84 buys its security by
sacrificing key bits; E91's test rounds are ones whose bases disagreed and which
were going to be discarded anyway.
"""

import argparse
import math
import random
from collections import Counter

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qkd import as_hex, deal, positive_int, simulate

# Ekert's three axes per side, in the plane. Alice at 0, 45, 90 degrees; Bob at
# 45, 90, 135. Two pairs line up exactly (A2=B1 and A3=B2) and make the key; the
# outer combinations are 45 degrees apart, which is where CHSH is maximal.
ALICE_ANGLES = (0.0, math.pi / 4, math.pi / 2)
BOB_ANGLES = (math.pi / 4, math.pi / 2, 3 * math.pi / 4)
ANGLE_NAMES = (("A1", 0), ("A2", 45), ("A3", 90)), (("B1", 45), ("B2", 90), ("B3", 135))

# Same axis on both sides: outcomes agree every time, so these rounds are the key.
KEY_SETTINGS = ((1, 0), (2, 1))

# S = E(A1,B1) - E(A1,B3) + E(A3,B1) + E(A3,B3)
CHSH_TERMS = {(0, 0): +1, (0, 2): -1, (2, 0): +1, (2, 2): +1}

CLASSICAL_BOUND = 2.0
TSIRELSON = 2 * math.sqrt(2)

# What Eve costs: she halves every correlation, so S falls from 2*sqrt(2) to
# sqrt(2) and the perfectly-correlated key rounds pick up a 25% error rate.
EVE_S = math.sqrt(2)
EVE_QBER = 0.25

FIELDS = ("alice", "bob", "eve")


# --------------------------------------------------------------------------
# One round of the protocol
# --------------------------------------------------------------------------
# A configuration is (alice_setting, bob_setting, eve_basis), with eve_basis None
# on a clean channel. Settings are indices into ALICE_ANGLES / BOB_ANGLES.

def emit_round(qc: QuantumCircuit, config: tuple, alice, bob, probe=None) -> None:
    """Write one E91 round onto the given qubits. Measurement is the caller's job.

    Measuring along an axis at angle theta from the computational axis is the same
    as rotating the state by -theta and then measuring along Z, so each party's
    setting is one Ry. That is the whole of "choosing a measurement basis" here.

    Eve, as in BB84, is deferred rather than mid-circuit: she copies Alice's
    travelling qubit onto a probe she keeps in her own basis, and the probe is
    measured at the end. Copying is enough to do the damage. She does not need to
    look at the probe for the entanglement between Alice and Bob to be destroyed --
    entangling with a third system is exactly what destroys it, which is why this
    attack shows up in the CHSH value whether or not she ever reads her result.

    The barriers are load-bearing on hardware: without them a transpiler is free to
    cancel the Bell pair's Hadamard against Eve's, or to fold both parties'
    rotations into the state preparation, and then the device is no longer running
    the protocol, only computing its answer.
    """
    a_setting, b_setting, e_basis = config
    span = [alice, bob] if probe is None else [alice, bob, probe]

    qc.h(alice)                      # the source: |00> + |11>, one qubit to each side
    qc.cx(alice, bob)
    qc.barrier(*span, label="pair sent")

    if e_basis:                      # Eve copies Alice's half out in her own basis
        if e_basis == "X":
            qc.h(alice)
        qc.cx(alice, probe)
        if e_basis == "X":
            qc.h(alice)
        qc.barrier(*span, label="Eve")

    qc.ry(-ALICE_ANGLES[a_setting], alice)
    qc.ry(-BOB_ANGLES[b_setting], bob)


def round_circuit(config: tuple) -> QuantumCircuit:
    """One round as a standalone circuit: the pair, plus Eve's probe if she is on."""
    eve = config[2] is not None
    pair = QuantumRegister(2, "pair")
    probe = QuantumRegister(1, "probe") if eve else None
    c_alice, c_bob = ClassicalRegister(1, "alice"), ClassicalRegister(1, "bob")
    c_eve = ClassicalRegister(1, "eve") if eve else None

    regs = [r for r in (pair, probe, c_alice, c_bob, c_eve) if r is not None]
    qc = QuantumCircuit(*regs)
    emit_round(qc, config, pair[0], pair[1], probe[0] if eve else None)
    qc.measure(pair[0], c_alice[0])
    qc.measure(pair[1], c_bob[0])
    if eve:
        qc.measure(probe[0], c_eve[0])
    return qc


def draw_rounds(n: int, eve: bool, rng: random.Random) -> list[tuple]:
    """Each side picks one of its three axes at random, independently, every round."""
    return [(rng.randrange(3), rng.randrange(3),
             rng.choice(("Z", "X")) if eve else None)
            for _ in range(n)]


# --------------------------------------------------------------------------
# Reading the results
# --------------------------------------------------------------------------

def correlation(samples: list[tuple]) -> float:
    """E = <A.B> with outcome 0 read as +1 and outcome 1 as -1.

    +1 means the two sides always agreed, -1 always disagreed, 0 no relationship.
    """
    if not samples:
        return 0.0
    agree = sum(1 for alice, bob, _ in samples if alice == bob)
    return (2 * agree - len(samples)) / len(samples)


def ideal_correlation(a_setting: int, b_setting: int, eve: bool) -> float:
    """cos of the angle between the two axes -- halved if Eve is entangled to one."""
    delta = ALICE_ANGLES[a_setting] - BOB_ANGLES[b_setting]
    return math.cos(delta) * (0.5 if eve else 1.0)


def role(setting: tuple) -> str:
    if setting in KEY_SETTINGS:
        return "key"
    return "test" if setting in CHSH_TERMS else "-"


def by_setting(rounds: list[tuple], outcomes: list[tuple]) -> dict[tuple, list]:
    """Group the outcomes by which pair of axes was used."""
    grouped: dict[tuple, list] = {}
    for r, o in zip(rounds, outcomes):
        grouped.setdefault((r[0], r[1]), []).append(o)
    return grouped


def print_grid(grouped: dict[tuple, list], total: int) -> None:
    (a_names, b_names) = ANGLE_NAMES
    print(f"\nHow the {total} rounds fell across the nine setting pairs:")
    print("            " + "".join(f"{f'{n} ({d})':>14}" for n, d in b_names))
    for i, (a_name, a_deg) in enumerate(a_names):
        cells = ""
        for j in range(3):
            n = len(grouped.get((i, j), []))
            cells += f"{f'{n} {role((i, j))}':>14}"
        print(f"  {a_name} ({a_deg:>2}) {cells}")
    print("\n  key  = both axes identical, outcomes always agree -> key bits")
    print("  test = 45 degrees apart, the four terms of the CHSH sum")
    print("  -    = discarded, as in BB84")


def print_table(rounds, outcomes, n: int) -> None:
    eve = rounds[0][2] is not None
    print(f"\nFirst {min(n, len(rounds))} rounds:")
    head = f"  {'#':>4}  {'a.set':>5} {'b.set':>5}  {'a.bit':>5} {'b.bit':>5}"
    if eve:
        head += f"  {'e.base':>6} {'e.bit':>5}"
    print(head + f"  {'used for':>8}")
    for i in range(min(n, len(rounds))):
        a_setting, b_setting, e_basis = rounds[i]
        alice, bob, eve_bit = outcomes[i]
        row = (f"  {i:>4}  {ANGLE_NAMES[0][a_setting][0]:>5} "
               f"{ANGLE_NAMES[1][b_setting][0]:>5}  {alice:>5} {bob:>5}")
        if eve:
            row += f"  {e_basis:>6} {eve_bit:>5}"
        print(row + f"  {role((a_setting, b_setting)):>8}")


def chsh(grouped: dict[tuple, list], eve: bool) -> tuple[float, float]:
    """The CHSH sum and its standard error, from the four test settings."""
    print("\nCorrelations on the four test settings:")
    print(f"  {'setting':>9}  {'rounds':>6}  {'sign':>4}  {'E measured':>10}  "
          f"{'E ideal':>8}")
    s, variance = 0.0, 0.0
    for setting, sign in CHSH_TERMS.items():
        samples = grouped.get(setting, [])
        e = correlation(samples)
        s += sign * e
        if samples:
            # var(E) for a +/-1 valued mean, from n independent rounds.
            variance += (1 - e**2) / len(samples)
        label = f"{ANGLE_NAMES[0][setting[0]][0]},{ANGLE_NAMES[1][setting[1]][0]}"
        print(f"  {label:>9}  {len(samples):>6}  {sign:>+4}  {e:>+10.3f}  "
              f"{ideal_correlation(*setting, eve):>+8.3f}")
    return s, math.sqrt(variance)


def analyse(rounds, outcomes, *, table, eve_present: bool, floor: str) -> dict:
    """Print the whole run, and return the numbers the verdict rests on."""
    grouped = by_setting(rounds, outcomes)
    if table:
        print_table(rounds, outcomes, table)
    print_grid(grouped, len(rounds))

    s, sigma = chsh(grouped, eve_present)
    excess = (s - CLASSICAL_BOUND) / sigma if sigma else 0.0

    print("\nCHSH:")
    print("  S = E(A1,B1) - E(A1,B3) + E(A3,B1) + E(A3,B3)")
    print(f"    = {s:.3f} +/- {sigma:.3f}")
    print(f"  no local hidden variables can exceed  {CLASSICAL_BOUND:.3f}")
    print(f"  quantum mechanics cannot exceed       {TSIRELSON:.3f}   (Tsirelson)")
    print(f"  an entangled pair Eve has touched     {EVE_S:.3f}")
    print(f"  {floor}")

    if s > TSIRELSON:
        # Worth saying out loud, because it looks alarming and is not.
        print(f"\n  ({s:.3f} sits above Tsirelson's bound. That is a finite-sample")
        print("   fluctuation in the estimate of S, not a violation of quantum")
        print("   mechanics -- the error bar covers it. More rounds shrink it.)")

    violated = s > CLASSICAL_BOUND
    if violated and excess > 3:
        print(f"\n  -> VIOLATED by {excess:.1f} sigma. Whatever produced these bits, they")
        print("     did not have values before they were measured, and nothing was")
        print("     entangled to them but each other. The channel is clean.")
    elif violated:
        print(f"\n  -> above 2, but only by {excess:.1f} sigma. Not enough to conclude"
              f"\n     anything. Raise --rounds.")
    else:
        print(f"\n  -> NOT VIOLATED ({s:.3f} <= 2). The correlations are reproducible by")
        print("     bits that were simply decided in advance -- which is exactly what")
        print("     an eavesdropper leaves behind. ABORT: the key is not secret.")

    # Key rounds: same axis on both sides, so the outcomes should be identical.
    key_rounds = [(r, o) for r, o in zip(rounds, outcomes)
                  if (r[0], r[1]) in KEY_SETTINGS]
    alice_key = [o[0] for _, o in key_rounds]
    bob_key = [o[1] for _, o in key_rounds]
    disagree = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    qber = disagree / len(key_rounds) if key_rounds else 0.0

    print(f"\nThe key -- rounds where both axes pointed the same way:")
    print(f"  key rounds         {len(key_rounds)}  "
          f"({len(key_rounds) / len(rounds):.1%} of the run, expected 22.2% = 2/9)")
    print(f"  Alice and Bob differ in {disagree} = {qber:.1%}")
    print(f"  a clean pair would give 0%, an intercepted one {EVE_QBER:.0%}")
    print("\n  Note what did NOT happen: no key bits were spent on the security")
    print("  check. The CHSH test used the mismatched rounds, which BB84 throws")
    print("  away. That is E91's structural advantage.")

    if eve_present and key_rounds:
        known = sum(1 for (_, o) in key_rounds if o[2] == o[0])
        print("\nWhat Eve came away with (an oracle's view, not Alice's or Bob's):")
        print(f"  key bits she has right  {known}/{len(key_rounds)} = "
              f"{known / len(key_rounds):.1%}")
        print(f"  guessing would give     50.0%")
        print(f"  prediction              {eve_prediction():.1%}  (see E91.md)")

    print(f"\n  Alice  {as_hex(alice_key)[:48]}{'...' if len(alice_key) > 192 else ''}")
    print(f"  Bob    {as_hex(bob_key)[:48]}{'...' if len(bob_key) > 192 else ''}")

    return {"s": s, "sigma": sigma, "excess": excess, "violated": violated,
            "qber": qber, "key_bits": len(key_rounds), "disagree": disagree}


def eve_prediction() -> float:
    """How often Eve's probe agrees with Alice's outcome, on the key settings.

    Her copy collapses Alice's qubit onto her own axis; Alice then measures at
    angle theta to it and agrees with probability cos^2(theta/2). Averaged over
    Eve's two bases and the two key settings.
    """
    return sum(math.cos((ALICE_ANGLES[a] - e) / 2) ** 2
               for a, _ in KEY_SETTINGS for e in (0.0, math.pi / 2)) / 4


def build_parser() -> argparse.ArgumentParser:
    """Exposed so _scripts/check_docs.py can verify COMMANDS.md against it."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rounds", type=positive_int, default=2048,
                    help="entangled pairs distributed. Only 2/9 become key bits and "
                         "4/9 test the inequality, so this needs to be large "
                         "(default 2048)")
    ap.add_argument("--eve", action="store_true",
                    help="let an eavesdropper entangle herself with Alice's qubit")
    ap.add_argument("--table", type=int, default=12,
                    help="how many individual rounds to print, 0 for none (default 12)")
    ap.add_argument("--seed", type=int, default=0,
                    help="seed for every classical choice, so runs reproduce (default 0)")
    return ap


def main() -> None:
    args = build_parser().parse_args()
    rng = random.Random(args.seed)

    print(f"E91 over {args.rounds} entangled pairs, "
          f"eavesdropper: {'yes' if args.eve else 'no'}")
    print(f"Simulated exactly. Seed {args.seed}, so the run reproduces.")

    rounds = draw_rounds(args.rounds, args.eve, rng)
    need = Counter(rounds)
    print(f"\n{len(need)} distinct round configurations, {args.rounds} rounds dealt "
          f"from them.")

    outcomes = deal(rounds, simulate(need, rng, round_circuit, FIELDS))
    analyse(rounds, outcomes, table=args.table, eve_present=args.eve,
            floor="nothing here is noisy, so the only thing that can lower S is Eve")


if __name__ == "__main__":
    main()
