# Real vs Complex Amplitudes

These notes use **real** probability amplitudes, following
*Quantum Computing for Everyone*. This records what that simplification costs.

## It is a simplification, not a gap

Real-amplitude quantum computing is universal: any complex circuit can be
simulated by a real one with a single extra qubit. So nothing here becomes false
later — it is a lower-dimensional picture of the same theory.

Real amplitudes are enough for superposition, measurement,
[tensor products](Tensor_Products.md), the
[entanglement criterion](Entanglement_Criterion.md), Bell states,
[superdense coding](../03_Protocols/Superdense_Coding.md),
[teleportation](../03_Protocols/Quantum_Teleportation.md), Bell-inequality
violation, and Grover's search.

## Where it stops

**$Y$ is not an involution without $i$.** The real version squares to $-I$:

$$\begin{bmatrix}0&1\\-1&0\end{bmatrix}^2 = -I \neq I$$

It is a $90°$ rotation, so applying it twice does not return the input. Only
$Y = -i\begin{bmatrix}0&1\\-1&0\end{bmatrix} = \begin{bmatrix}0&-i\\i&0\end{bmatrix}$
satisfies $Y^2 = I$. $X$, $Z$ and $H$ need no complex numbers; $Y$ is the
exception. See [Involutions](../02_Gates/Involutions.md).

**Relative phase has only two values.** With real amplitudes the phase is a sign,
$\pm 1$; with complex ones it is $e^{i\varphi}$ for any angle. Geometrically, real
amplitudes trace a *circle* through $|0\rangle, |1\rangle, |{+}\rangle, |{-}\rangle$,
while complex amplitudes fill the whole *Bloch sphere*.

**Some gates and algorithms do not exist yet.** $S$, $T$ and $R_z$ *are* phases,
so there is no universal gate set without them. The quantum Fourier transform is
built on $e^{2\pi i/N}$, which rules out phase estimation and
[Shor's algorithm](../04_Algorithms/Shors_Algorithm.md) — the worked example of
this boundary.

## What carries over unchanged

The entanglement criterion $ru = st$ generalises verbatim. Over $\mathbb{C}$ it is
the statement that the $2\times2$ matrix of amplitudes has determinant zero, which
is the separability condition for any two-qubit pure state.

## Habits that make the switch free

- Write $|a_0|^2 + |a_1|^2 = 1$, not $a_0^2 + a_1^2 = 1$. Identical for reals.
- A bra is the *conjugate* transpose of a ket.
- Say "unitary" ($U^\dagger U = I$), not "orthogonal".
- Read a minus sign as the phase $e^{i\pi}$ — a special case of something
  continuous.

Qiskit is complex from the start regardless: `Statevector` returns `complex128`,
so amplitudes print as `0.7071+0j` while these notes say $\tfrac{1}{\sqrt2}$.
