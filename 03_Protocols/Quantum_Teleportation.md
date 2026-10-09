# Quantum Teleportation

Code: [`teleportation.py`](teleportation.py) — runs locally or on IBM hardware with `--ibm`.

The protocol that can transfer **1 qubit** by physically transferring **2 classical
bits**. It is the opposite of [Superdense_Coding](Superdense_Coding.md): there, Bob applies the reverse
Bell circuit and Alice applies the gate; here, **Alice applies the reverse Bell
circuit and Bob applies the gate**.

## Setup

For the initial step, 2 particles need to be in an entangled state:

$$\tfrac{1}{\sqrt2}|00\rangle + \tfrac{1}{\sqrt2}|11\rangle$$

- **Alice owns `psi` and `alice`; Bob owns `bob`** — and they are far apart.
- Alice has **another** particle in the state $a|0\rangle + b|1\rangle$.
- Alice wants to change Bob's particle to be in the state $a|0\rangle + b|1\rangle$.
- Alice runs CNOT then $H$ on her two qubits.
- Alice measures both.
- Alice sends the 2 bits she decoded to Bob.
- Bob applies one of the 4 gates to his qubit.

| Bits received | Bob applies |
| :-: | :-: |
| 00 | $I$ |
| 01 | $X$ |
| 10 | $Z$ |
| 11 | $Y$ (or $ZX$) |

## Circuit — Alice's side

<img src="../_assets/circuit_teleportation.png" width="760" alt="circuit teleportation">

The `psi` wire carries $a|0\rangle + b|1\rangle$; `alice` and `bob` start as the shared pair. Alice's part is everything left of the second barrier.

## Walking through the state

We have 3 qubits at the initial stage:

$$\big(a|0\rangle + b|1\rangle\big)\left(\tfrac{1}{\sqrt2}|00\rangle + \tfrac{1}{\sqrt2}|11\rangle\right)$$

Alice will act on her qubits, so write it with emphasis on hers (first two kets
are Alice's, last is Bob's):

$$\tfrac{a}{\sqrt2}|000\rangle + \tfrac{a}{\sqrt2}|011\rangle + \tfrac{b}{\sqrt2}|100\rangle + \tfrac{b}{\sqrt2}|111\rangle$$

$$= \tfrac{a}{\sqrt2}(|00\rangle)(|0\rangle) + \tfrac{a}{\sqrt2}(|01\rangle)(|1\rangle) + \tfrac{b}{\sqrt2}(|10\rangle)(|0\rangle) + \tfrac{b}{\sqrt2}(|11\rangle)(|1\rangle)$$

Alice applies the **reverse Bell circuit**. Passing through CNOT (control = qubit 1,
target = qubit 2) flips the last two terms' second qubit:

$$= \tfrac{a}{\sqrt2}(|00\rangle)(|0\rangle) + \tfrac{a}{\sqrt2}(|01\rangle)(|1\rangle) + \tfrac{b}{\sqrt2}(|11\rangle)(|0\rangle) + \tfrac{b}{\sqrt2}(|10\rangle)(|1\rangle)$$

Alice now acts on the **first qubit only**, with a Hadamard:

$$|0\rangle \to \tfrac{1}{\sqrt2}\big(|0\rangle + |1\rangle\big), \qquad |1\rangle \to \tfrac{1}{\sqrt2}\big(|0\rangle - |1\rangle\big)$$

This results in the state:

$$\tfrac{a}{2}|000\rangle + \tfrac{a}{2}|100\rangle + \tfrac{a}{2}|011\rangle + \tfrac{a}{2}|111\rangle + \tfrac{b}{2}|010\rangle - \tfrac{b}{2}|110\rangle + \tfrac{b}{2}|001\rangle - \tfrac{b}{2}|101\rangle$$

## Alice measures

Measuring her two qubits in the standard basis, she gets one of four outcomes, and
Bob's qubit jumps to the matching state:

| Alice measures | Bob's qubit jumps to |
| :-: | :--- |
| $\vert 00\rangle$ | $a\vert 0\rangle + b\vert 1\rangle$ |
| $\vert 01\rangle$ | $a\vert 1\rangle + b\vert 0\rangle$ |
| $\vert 10\rangle$ | $a\vert 0\rangle - b\vert 1\rangle$ |
| $\vert 11\rangle$ | $a\vert 1\rangle - b\vert 0\rangle$ |

All four have amplitude $\tfrac12$, so each outcome is equally likely — which is why
Alice's measurement alone transmits nothing until the classical bits arrive.

Alice sends her bits to Bob. Say her qubits were in the state $|01\rangle$: she
sends **01** to Bob.

## Bob corrects

| Bob receives | Action |
| :-: | :--- |
| 00 | does nothing, qubit is already in $a\vert 0\rangle + b\vert 1\rangle$ |
| 01 | applies $X$ |
| 10 | applies $Z$ |
| 11 | applies $Y$ |

## Full circuit

The `If` boxes at the end are Bob's correction gate $G$ — $X$ when `c1` is 1,
$Z$ when `c0` is 1, both (i.e. $ZX \sim Y$) when both are. See the figure at the
top of this note.

## On hardware

Teleportation is the only protocol here that needs a **dynamic circuit** — Bob's
correction depends on a measurement taken moments earlier, so the decision happens
on the device rather than when the circuit is built.

That has a cost: IBM does not allow dynamical decoupling or gate twirling on
circuits with control flow, so a `--ibm` run of teleportation gets **no error
suppression** while the other protocols do. Expect it to be noisier.

## Use cases

- **Quantum repeaters** — the same as a signal amplifier for classical bits, but
  for quantum.
- **Distributed quantum computing.**
- **Inside error-corrected computers** — the biggest practical use.

---

Compare with the forward direction: [Superdense_Coding](Superdense_Coding.md).
