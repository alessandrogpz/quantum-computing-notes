# Quantum Gates Acting on One Qubit

All act on $a_0|0\rangle + a_1|1\rangle$ in the standard basis.

## $I$ and $Z$

$I$ is the **identity gate** — it leaves the qubit unchanged:

$$I = \begin{bmatrix}1 & 0\\ 0 & 1\end{bmatrix}, \qquad I\big(a_0|0\rangle + a_1|1\rangle\big) = a_0|0\rangle + a_1|1\rangle$$

$Z$ leaves the **magnitude** of the probability amplitudes unchanged, but changes
the sign of $a_1$ — i.e. it changes the **relative phase**:

$$Z = \begin{bmatrix}1 & 0\\ 0 & -1\end{bmatrix}, \qquad Z\big(a_0|0\rangle + a_1|1\rangle\big) = a_0|0\rangle - a_1|1\rangle$$

Measurement probabilities are unaffected ($|-a_1|^2 = |a_1|^2$), but the phase
matters once the qubit interferes with another, e.g. after a Hadamard.

## $X$ and $Y$

Both correspond to **NOT**, in the sense that they exchange $|0\rangle$ and $|1\rangle$.

$$X = \begin{bmatrix}0 & 1\\ 1 & 0\end{bmatrix}, \qquad Y = \begin{bmatrix}0 & 1\\ -1 & 0\end{bmatrix}$$

$$X\big(a_0|0\rangle + a_1|1\rangle\big) = a_1|0\rangle + a_0|1\rangle$$
$$Y\big(a_0|0\rangle + a_1|1\rangle\big) = a_1|0\rangle - a_0|1\rangle$$

So $X$ is a pure swap, and $Y$ inverts $|0\rangle \leftrightarrow |1\rangle$ **and**
changes the relative phase.

> [!note] Convention
> The **Pauli $Y$** is usually defined as $-i$ times the matrix used here:
> $$-i\begin{bmatrix}0 & 1\\ -1 & 0\end{bmatrix} = \begin{bmatrix}0 & -i\\ i & 0\end{bmatrix}$$
> The global factor $-i$ has no observable effect on its own, so the real-valued
> version above is used for the arithmetic in these notes. Qiskit's `qc.y(q)`
> applies the standard complex Pauli $Y$.

## Hadamard

Usually used to put a standard basis vector into **superposition**:

$$H = \begin{bmatrix} \tfrac{1}{\sqrt2} & \tfrac{1}{\sqrt2} \\[2pt] \tfrac{1}{\sqrt2} & -\tfrac{1}{\sqrt2} \end{bmatrix} = \tfrac{1}{\sqrt2}\begin{bmatrix}1 & 1\\ 1 & -1\end{bmatrix}$$

$$H|0\rangle = \tfrac{1}{\sqrt2}\big(|0\rangle + |1\rangle\big), \qquad H|1\rangle = \tfrac{1}{\sqrt2}\big(|0\rangle - |1\rangle\big)$$

## Diagram notation

Gates acting on one qubit are drawn as a square with the appropriate letter in the
centre:

![[gate_single_qubit_boxes.png|340]]

---

Related: [[Involutions]], [[From_Classical_To_Quantum]]
