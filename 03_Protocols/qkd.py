"""Machinery shared by the two key-distribution protocols in this folder.

Nothing here is specific to BB84 or E91. What they have in common is a shape:

    draw N rounds  ->  each round has a *configuration*  ->  sample each distinct
    configuration  ->  deal the samples back out to the rounds that wanted them

and that shape is what this module implements. Both protocols import it; neither
imports the other.

THE TRICK THIS MODULE EXISTS FOR. A round's outcome depends on nothing except its
configuration -- which bit or which angles, and whose bases. There are only a
handful of distinct configurations (16 for BB84 with an eavesdropper, 18 for E91),
so N rounds do not need N circuit executions. Run one circuit per configuration,
ask for as many shots as there are rounds wanting that configuration, and hand the
shots out. Every shot is an i.i.d. sample of exactly the distribution those rounds
need, so what comes out is a genuine N-round protocol run, at a sixteenth of the
cost or better.

That is valid only because the rounds really are independent and identically
distributed given their configuration, which is true of both protocols as
implemented here: Eve is fixed intercept-resend, and she does not adapt to what she
has already seen. A cleverer attacker, one who chose her basis in round n based on
rounds 1..n-1, would break the assumption and would need N genuine circuits.
"""

import argparse

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import StatevectorSampler


def positive_int(text: str) -> int:
    """argparse type for a count that is meaningless at zero.

    A protocol with no rounds has no sifting, no test and no key, and every
    percentage below is a division by zero. Better to say so at the command line
    than to raise somewhere in the middle of the report.
    """
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


def pools_from(datas, groups: list[list[tuple]], fields: tuple[str, ...]) -> dict:
    """Turn measured registers into one pool of samples per configuration.

    `groups` says which configurations were packed into each result, in slot order.
    `fields` names the classical registers to read, and fixes the order of the
    tuple each sample comes back as. A register the run does not have -- Eve's,
    on a clean channel -- comes back as None in its slot rather than being missing,
    so the shape of a sample does not depend on who was listening.

    Qiskit prints a register with its highest-index bit leftmost, so every
    bitstring is reversed before being indexed by clbit.
    """
    pools: dict[tuple, list] = {}
    for data, configs in zip(datas, groups):
        columns = {}
        for name in fields:
            register = getattr(data, name, None)
            columns[name] = ([s[::-1] for s in register.get_bitstrings()]
                             if register is not None else None)
        shots = len(next(c for c in columns.values() if c is not None))
        for slot, config in enumerate(configs):
            pools[config] = [
                tuple(int(columns[f][shot][slot]) if columns[f] is not None else None
                      for f in fields)
                for shot in range(shots)
            ]
    return pools


def simulate(need: dict[tuple, int], rng, build, fields: tuple[str, ...]) -> dict:
    """Sample each distinct configuration exactly as many times as it is wanted.

    One exactly-simulated circuit per configuration, `build(config)` wide, with
    no noise anywhere. The hardware scripts replace this function and nothing else.
    """
    pools: dict[tuple, list] = {}
    for config, k in need.items():
        sampler = StatevectorSampler(seed=rng.randrange(2**32))
        result = sampler.run([build(config)], shots=k).result()[0]
        pools.update(pools_from([result.data], [[config]], fields))
    return pools


def deal(rounds: list[tuple], pools: dict[tuple, list]) -> list[tuple]:
    """Hand every round one unused sample of its own configuration."""
    remaining = {config: list(samples) for config, samples in pools.items()}
    dealt = []
    for config in rounds:
        if not remaining.get(config):
            raise ValueError(f"ran out of samples for configuration {config} after "
                             f"{len(dealt)} rounds -- raise the shot count")
        dealt.append(remaining[config].pop())
    return dealt


def pack(configs: list[tuple], emit, width: int, measured: dict[str, int]) -> QuantumCircuit:
    """Lay every configuration side by side on its own qubits, in one circuit.

    The rounds of a QKD protocol are independent, so there is no reason to run them
    one at a time. Each configuration needs `width` qubits, and a 127-qubit device
    has room for all of them at once, so one shot of this circuit is one
    independent sample of every configuration simultaneously -- and N shots supply
    every round of an N-round protocol from a single circuit execution. On hardware,
    where per-circuit overhead dwarfs these two-gate circuits, that is most of the
    cost of the job.

    `emit(qc, config, qubits)` writes one round; `measured` maps each classical
    register name to the offset, within a round's qubits, of the qubit it reads.

    The caveat is physical rather than statistical. Side by side means genuinely
    side by side on the chip, so the configurations stop failing independently:
    crosstalk couples neighbours, and one bad qubit spoils exactly one
    configuration rather than smearing over all of them.
    """
    n = len(configs)
    q = QuantumRegister(n * width, "q")
    registers = {name: ClassicalRegister(n, name) for name in measured}
    qc = QuantumCircuit(q, *registers.values())

    for slot, config in enumerate(configs):
        emit(qc, config, [q[slot * width + k] for k in range(width)])
    for slot in range(n):
        for name, offset in measured.items():
            qc.measure(q[slot * width + offset], registers[name][slot])
    return qc


def chunk(configs: list[tuple], per_circuit: int) -> list[list[tuple]]:
    """Split the configurations across circuits if they will not all fit at once."""
    return [configs[i:i + per_circuit] for i in range(0, len(configs), per_circuit)]


def as_hex(bits: list[int]) -> str:
    """A key as bytes, so it reads like a key instead of a list of digits."""
    octets = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    return "".join(f"{int(''.join(str(b) for b in o).ljust(8, '0'), 2):02x}" for o in octets)
