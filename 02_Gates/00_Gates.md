# Gates

Reversible logic gates, first as classical operations on bits, then as unitary
operations on qubits.

| Note | Contents |
| :--- | :--- |
| [Reversible_Classical_Gates](Reversible_Classical_Gates.md) | CNOT, Toffoli (CCNOT), Fredkin (CSWAP) — truth tables, diagrams, formulas |
| [From_Classical_To_Quantum](From_Classical_To_Quantum.md) | The standard basis, 2-qubit basis, CNOT on superpositions |
| [Single_Qubit_Gates](Single_Qubit_Gates.md) | $I$, $Z$, $X$, $Y$, $H$ — matrices and their effect |
| [Involutions](Involutions.md) | $U^2 = I$, the table of involution gates, the reverse Bell circuit |

## Reading order

1. [Reversible_Classical_Gates](Reversible_Classical_Gates.md) — reversibility on plain bits.
2. [From_Classical_To_Quantum](From_Classical_To_Quantum.md) — same gates, now acting on kets and superpositions.
3. [Single_Qubit_Gates](Single_Qubit_Gates.md) — the one-qubit toolbox.
4. [Involutions](Involutions.md) — the property that lets a circuit undo itself.

## Cheat sheet

$$C(x,y) = (x,\; x \oplus y)$$
$$T(x,y,z) = \big(x,\; y,\; (x \wedge y) \oplus z\big)$$
$$F(x,y,z) = \big(x,\; (\neg x \wedge y) \vee (x \wedge z),\; (\neg x \wedge z) \vee (x \wedge y)\big)$$

$$I = \begin{bmatrix}1&0\\0&1\end{bmatrix} \quad
X = \begin{bmatrix}0&1\\1&0\end{bmatrix} \quad
Y = \begin{bmatrix}0&1\\-1&0\end{bmatrix} \quad
Z = \begin{bmatrix}1&0\\0&-1\end{bmatrix} \quad
H = \tfrac{1}{\sqrt2}\begin{bmatrix}1&1\\1&-1\end{bmatrix}$$
