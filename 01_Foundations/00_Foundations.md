# Foundations

The vector-space language for describing qubits, combining them, and reading off
what a measurement does.

| Note | Contents |
| :--- | :--- |
| [Dirac_Notation](Dirac_Notation.md) | Kets and bras, probability amplitudes, the standard basis |
| [Tensor_Products](Tensor_Products.md) | Combining two qubits, the $r,s,t,u$ amplitudes, normalization |
| [Entanglement_Criterion](Entanglement_Criterion.md) | The $ru$ vs $st$ test, worked separable example |
| [Measurement_and_Perspective](Measurement_and_Perspective.md) | Grouping by Alice or by Bob, conditional collapse |
| [Real_vs_Complex_Amplitudes](Real_vs_Complex_Amplitudes.md) | Why the real-amplitude simplification works, and where it stops |

## Reading order

1. [Dirac_Notation](Dirac_Notation.md)
2. [Tensor_Products](Tensor_Products.md)
3. [Entanglement_Criterion](Entanglement_Criterion.md)
4. [Measurement_and_Perspective](Measurement_and_Perspective.md)

These notes use **real** probability amplitudes throughout, following the book.
That is a deliberate simplification rather than a gap — see
[Real_vs_Complex_Amplitudes](Real_vs_Complex_Amplitudes.md) for what it costs and
when it has to be dropped.

## Key Takeaway

$$r^2 + s^2 + t^2 + u^2 = 1 \qquad \text{(a tensor product is always normalized)}$$

$$ru = st \iff \text{separable} \qquad ru \neq st \iff \text{entangled}$$
