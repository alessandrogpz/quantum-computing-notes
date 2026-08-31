# Protocols

Things entanglement lets you do that classical bits cannot, and the two protocols
that turn those tricks into working cryptography.

## Moving information

Both are built from the same two pieces: a shared Bell pair
$\tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)$, and the Bell circuit ($H$ then CNOT)
run forwards to prepare it or backwards to read it out.

| Note | Sends | By transferring |
| :--- | :--- | :--- |
| [Superdense_Coding](Superdense_Coding.md) | 2 classical bits | 1 qubit |
| [Quantum_Teleportation](Quantum_Teleportation.md) | 1 qubit | 2 classical bits |

They are duals of each other:

| | Prepares / encodes | Applies the correcting gate | Runs the reverse Bell circuit |
| :--- | :--- | :--- | :--- |
| Superdense coding | Alice | Alice | Bob |
| Teleportation | Alice | Bob | Alice |

### Shared gate mapping

Both protocols use the same 4-way mapping between two classical bits and a gate:

| Bits | Gate |
| :-: | :-: |
| 00 | $I$ |
| 01 | $X$ |
| 10 | $Z$ |
| 11 | $Y$ (or $ZX$) |

## Distributing a key

The two quantum key distribution protocols, each with a runnable implementation and
an active eavesdropper. Neither hides a message: both build a shared random key and
guarantee that anyone who listened is **detected**, so the key can be thrown away
before it is used.

| Note | Code | Detects Eve by |
| :--- | :--- | :--- |
| [BB84](BB84.md) | [`bb84.py`](bb84.py) | measurement disturbance and no-cloning |
| [↳ on hardware](BB84.md#running-it-on-real-ibm-hardware) | [`bb84_ibm.py`](bb84_ibm.py) | the same rounds, packed and transpiled for an IBM device |
| [E91](E91.md) | [`e91.py`](e91.py) | the loss of a Bell inequality violation |
| [↳ on hardware](E91.md#running-it-on-real-ibm-hardware) | [`e91_ibm.py`](e91_ibm.py) | the same rounds, packed and transpiled for an IBM device |

[`qkd.py`](qkd.py) holds what the two share: neither protocol imports the other.

The two arrive at the same number from opposite directions. An intercept-resend
eavesdropper corrupts exactly a quarter of the bits Alice and Bob should agree on —
in BB84 because she guesses the wrong basis half the time and then randomises Bob's
result half of *those*; in E91 because entangling herself with Alice's qubit halves
every correlation, and a correlation of $\tfrac12$ is a 25% error rate.

| | [BB84](BB84.md) | [E91](E91.md) |
| :--- | :--- | :--- |
| Resource | single qubits, prepared and sent | entangled pairs from a shared source |
| Cost of the security check | **sacrificed key bits** | free — rounds that were discarded anyway |
| Key yield | $\tfrac12$ of rounds, minus the check | $\tfrac29$ of rounds |
| Attack signature | QBER $0 \to 25\%$ | $S: 2\sqrt2 \to \sqrt2$, QBER $0 \to 25\%$ |
| Runs on today's hardware | yes — 1 qubit per round | yes — the CHSH violation survives real noise |

Prerequisites: [Entanglement_Criterion](../01_Foundations/Entanglement_Criterion.md), [Single_Qubit_Gates](../02_Gates/Single_Qubit_Gates.md), [Involutions](../02_Gates/Involutions.md), [Measurement_and_Perspective](../01_Foundations/Measurement_and_Perspective.md)
