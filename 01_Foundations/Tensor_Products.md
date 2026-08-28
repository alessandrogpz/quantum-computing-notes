# Tensor Products

Two separate qubits are combined into a single two-qubit state with the **tensor
product** $\otimes$ (vector multiplication).

## Setup

Alice and Bob each hold one qubit:

- Alice: $|v\rangle = c_0|a_0\rangle + c_1|a_1\rangle$, with $c_0^2 + c_1^2 = 1$
- Bob: $|w\rangle = d_0|b_0\rangle + d_1|b_1\rangle$, with $d_0^2 + d_1^2 = 1$

## Expanding the product

$$|v\rangle \otimes |w\rangle = \big(c_0|a_0\rangle + c_1|a_1\rangle\big)\big(d_0|b_0\rangle + d_1|b_1\rangle\big)$$

Expanding:

$$= c_0d_0\,|a_0\rangle|b_0\rangle + c_0d_1\,|a_0\rangle|b_1\rangle + c_1d_0\,|a_1\rangle|b_0\rangle + c_1d_1\,|a_1\rangle|b_1\rangle$$

## Naming the amplitudes

Replace the four products with single letters:

| | |
| :--- | :--- |
| $r = c_0 d_0$ | amplitude of $\vert a_0\rangle\vert b_0\rangle$ |
| $s = c_0 d_1$ | amplitude of $\vert a_0\rangle\vert b_1\rangle$ |
| $t = c_1 d_0$ | amplitude of $\vert a_1\rangle\vert b_0\rangle$ |
| $u = c_1 d_1$ | amplitude of $\vert a_1\rangle\vert b_1\rangle$ |

## The combined state is still normalized

Since $c_0^2 + c_1^2 = 1$ and $d_0^2 + d_1^2 = 1$:

$$\underbrace{(c_0^2 + c_1^2)}_{1}\underbrace{(d_0^2 + d_1^2)}_{1} = 1$$

and expanding that product gives exactly $r^2 + s^2 + t^2 + u^2$. So:

$$\boxed{\;r^2 + s^2 + t^2 + u^2 = 1\;}$$

which confirms $|v\rangle \otimes |w\rangle$ is a valid two-qubit state.

## Basis of a two-qubit system

Tensoring the standard basis with itself gives the four basis vectors of a
two-qubit system:

$$\left(\begin{bmatrix}1\\0\end{bmatrix} \otimes \begin{bmatrix}1\\0\end{bmatrix},\;
\begin{bmatrix}1\\0\end{bmatrix} \otimes \begin{bmatrix}0\\1\end{bmatrix},\;
\begin{bmatrix}0\\1\end{bmatrix} \otimes \begin{bmatrix}1\\0\end{bmatrix},\;
\begin{bmatrix}0\\1\end{bmatrix} \otimes \begin{bmatrix}0\\1\end{bmatrix}\right)$$

$$= \big(|0\rangle|0\rangle,\; |0\rangle|1\rangle,\; |1\rangle|0\rangle,\; |1\rangle|1\rangle\big)
= \big(|00\rangle,\; |01\rangle,\; |10\rangle,\; |11\rangle\big)$$

The shorthand $|00\rangle$ means $|0\rangle \otimes |0\rangle$.

---

Next: [[Entanglement_Criterion]] — when a two-qubit state *cannot* be written as a
tensor product.
