# Real vs Complex Amplitudes

These notes (and *Quantum Computing for Everyone*) use **real** probability
amplitudes. That is a deliberate simplification. This note records what it costs
and how to avoid paying for it twice.

## The short version

Staying real is fine for now, and it costs nothing in the end — but **"add $i$
everywhere later" is not a mechanical patch**. Adopt the four habits at the bottom
of this note today and the retrofit is free.

## What real amplitudes already give you

Everything in this vault so far, and more:

- superposition, measurement, and collapse
- [[Tensor_Products]] and the [[Entanglement_Criterion]]
- Bell states, [[Superdense_Coding]], [[Quantum_Teleportation]]
- Bell-inequality / CHSH violation — the actual proof that quantum ≠ classical
- Deutsch–Jozsa and Grover's search

In fact **real-amplitude quantum computing is universal**: any complex-amplitude
circuit can be simulated by a real-amplitude one with a single extra qubit (the
"rebit" encoding). So no computational power is lost by starting real — this is a
notational and geometric simplification, not a weaker theory.

## Where it actually breaks

### 1. $Y$ is not an involution without $i$

This one is already in the vault. [[Single_Qubit_Gates]] uses
$Y = \begin{bmatrix}0&1\\-1&0\end{bmatrix}$, but:

$$\begin{bmatrix}0&1\\-1&0\end{bmatrix}^2 = \begin{bmatrix}-1&0\\0&-1\end{bmatrix} = -I \;\neq\; I$$

The real $Y$ is a $90°$ **rotation**, so applying it twice does not return the
input. Only the true Pauli $Y = -i\begin{bmatrix}0&1\\-1&0\end{bmatrix} = \begin{bmatrix}0&-i\\i&0\end{bmatrix}$
satisfies $Y^2 = I$, because $(-i)^2(-I) = I$. So the entry for $Y$ in the
[[Involutions]] table is *only* correct in the complex version — the table even
says "Pauli, with $-i$". $X$, $Z$ and $H$ are real, Hermitian and involutions with
no complex numbers needed; $Y$ is the odd one out.

### 2. Relative phase has only two values

With real amplitudes the "relative phase" of [[Single_Qubit_Gates]] is just a sign,
$\pm 1$. With complex amplitudes it is $e^{i\varphi}$ for any angle $\varphi$.
Geometrically: real amplitudes trace a **circle** through
$|0\rangle, |1\rangle, |{+}\rangle, |{-}\rangle$; complex amplitudes fill the whole
**Bloch sphere**. Everything on the sphere but off that circle is invisible in the
real picture.

### 3. Whole gates and algorithms do not exist yet

Unavailable until amplitudes go complex:

| Thing | Why it needs $i$ |
| :--- | :--- |
| $S$ and $T$ gates, $R_z(\theta)$, phase gate $P(\varphi)$ | they *are* phases: $\mathrm{diag}(1, e^{i\varphi})$ |
| Universal gate sets (e.g. Clifford + $T$) | $T$ is a complex phase |
| Quantum Fourier Transform, phase estimation, Shor | built on $\omega = e^{2\pi i/N}$ |
| Hamiltonian time evolution $e^{-iHt}$ | simulation, VQE, real hardware |
| General Hermitian observables | $A = A^\dagger$ is a complex-conjugate condition |

## Where the real picture is already right

The [[Entanglement_Criterion]] generalizes **verbatim**. Over $\mathbb{C}$ the test
$ru = st$ is exactly "the $2\times2$ matrix of amplitudes has determinant zero",
which is the separability condition for any two-qubit pure state. Nothing to redo.

## Habits to adopt now (so the retrofit is free)

1. **Write $|a_0|^2 + |a_1|^2 = 1$, never $a_0^2 + a_1^2 = 1$.** Identical for
   reals, correct forever. (The page-1 notes already do this in places.)
2. **A bra is the *conjugate* transpose of a ket**, not just the transpose.
   $\langle v| = |v\rangle^\dagger$.
3. **Say "unitary" ($U^\dagger U = I$), not "orthogonal."**
4. **Read a minus sign as a phase**, i.e. $e^{i\pi}$ — a special case of something
   continuous, not a separate species of thing.

## When to bring $i$ in

At the **Bloch sphere**, or at the latest when you meet the $S$/$T$ gates or phase
kickback. Everything before that point genuinely does not need it.

> [!note] Qiskit is complex from line one
> `Statevector` returns `complex128` regardless. Amplitudes will print as
> `0.7071+0j` while the notes say $\tfrac{1}{\sqrt2}$. That mismatch is expected —
> the `+0j` is the part the book has not introduced yet.

---

Related: [[Single_Qubit_Gates]], [[Involutions]], [[Entanglement_Criterion]], [[00_Open_Questions]]
