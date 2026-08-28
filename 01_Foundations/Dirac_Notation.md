# Dirac Notation

Notation for writing quantum states as vectors.

## Ket and bra

A **ket** $|k\rangle$ is a column vector:

$$|k\rangle = \begin{bmatrix} k_1 \\ k_2 \\ k_3 \end{bmatrix}$$

A **bra** $\langle b|$ is a row vector:

$$\langle b| = \begin{bmatrix} b_1 & b_2 & b_3 \end{bmatrix}$$

So a bra is the (conjugate) transpose of a ket — the two are written as the two
halves of a bracket, $\langle b | k \rangle$.

## Qubit states

A qubit is written in some orthonormal basis $\{|a_0\rangle, |a_1\rangle\}$:

$$|v\rangle = c_0|a_0\rangle + c_1|a_1\rangle, \qquad c_0^2 + c_1^2 = 1$$

The coefficients $c_0, c_1$ are the **probability amplitudes**. The normalization
condition $c_0^2 + c_1^2 = 1$ says the probabilities of the two outcomes sum to 1:
measuring gives $|a_0\rangle$ with probability $c_0^2$ and $|a_1\rangle$ with
probability $c_1^2$.

## Standard basis

Unless stated otherwise, the **standard basis** is used:

$$|0\rangle = \begin{bmatrix} 1 \\ 0 \end{bmatrix}, \qquad |1\rangle = \begin{bmatrix} 0 \\ 1 \end{bmatrix}$$

and a qubit has the form $a_0|0\rangle + a_1|1\rangle$ with $a_0^2 + a_1^2 = 1$.

---

Next: [Tensor_Products](Tensor_Products.md) — combining two qubits into one state.
