# Foundations

The vector-space language for describing qubits, combining them, and reading off
what a measurement does.

| Note | Contents |
| :--- | :--- |
| [Dirac_Notation](Dirac_Notation.md) | Kets and bras, probability amplitudes, the standard basis |
| [Tensor_Products](Tensor_Products.md) | Combining two qubits, the $r,s,t,u$ amplitudes, normalization |
| [Entanglement_Criterion](Entanglement_Criterion.md) | The $ru$ vs $st$ test, worked separable example |
| [Measurement_and_Perspective](Measurement_and_Perspective.md) | Grouping by Alice or by Bob, conditional collapse |

## Reading order

1. [Dirac_Notation](Dirac_Notation.md) — the notation everything else is written in.
2. [Tensor_Products](Tensor_Products.md) — how two one-qubit states become one two-qubit state.
3. [Entanglement_Criterion](Entanglement_Criterion.md) — when that process cannot be run backwards.
4. [Measurement_and_Perspective](Measurement_and_Perspective.md) — what entanglement means operationally.

> [!note] These notes use **real** probability amplitudes
> That is a deliberate simplification, not a gap — real-amplitude quantum computing
> is computationally universal. What it costs, and when to drop it, is parked in
> [Real_vs_Complex_Amplitudes](../99_TODO/Real_vs_Complex_Amplitudes.md) under [99_TODO](../99_TODO/00_TODO.md).

## Key results

$$r^2 + s^2 + t^2 + u^2 = 1 \qquad \text{(a tensor product is always normalized)}$$

$$ru = st \iff \text{separable} \qquad ru \neq st \iff \text{entangled}$$
