# Protocols

Things entanglement lets you do that classical bits cannot. Both protocols below
are built from the same two pieces: a shared Bell pair
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

## Shared gate mapping

Both protocols use the same 4-way mapping between two classical bits and a gate:

| Bits | Gate |
| :-: | :-: |
| 00 | $I$ |
| 01 | $X$ |
| 10 | $Z$ |
| 11 | $Y$ (or $ZX$) |

Prerequisites: [Entanglement_Criterion](../01_Foundations/Entanglement_Criterion.md), [Single_Qubit_Gates](../02_Gates/Single_Qubit_Gates.md), [Involutions](../02_Gates/Involutions.md)
