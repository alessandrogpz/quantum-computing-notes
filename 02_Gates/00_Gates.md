# Gates

Reversible logic gates, first as classical operations on bits, then as unitary
operations on qubits.

| Note | Contents |
| :--- | :--- |
| [Reversible_Classical_Gates](Reversible_Classical_Gates.md) | CNOT, Toffoli (CCNOT), Fredkin (CSWAP) — truth tables, diagrams, formulas |
| [From_Classical_To_Quantum](From_Classical_To_Quantum.md) | The standard basis, 2-qubit basis, CNOT on superpositions |
| [Single_Qubit_Gates](Single_Qubit_Gates.md) | $I$, $Z$, $X$, $Y$, $H$ — matrices and their effect |
| [Involutions](Involutions.md) | $U^2 = I$, the table of involution gates, the reverse Bell circuit |
| [`gates.py`](gates.py) | every gate above built in Qiskit, with its matrix and truth table |

## Reading order

1. [Reversible_Classical_Gates](Reversible_Classical_Gates.md)
2. [From_Classical_To_Quantum](From_Classical_To_Quantum.md)
3. [Single_Qubit_Gates](Single_Qubit_Gates.md)
4. [Involutions](Involutions.md)

## Cheat sheet

$$C(x,y) = (x, x \oplus y)$$
$$T(x,y,z) = \big(x, y, (x \wedge y) \oplus z\big)$$
$$F(x,y,z) = \big(x, (\neg x \wedge y) \vee (x \wedge z), (\neg x \wedge z) \vee (x \wedge y)\big)$$

$$I = \begin{bmatrix}1&0\cr0&1\end{bmatrix} \quad
X = \begin{bmatrix}0&1\cr1&0\end{bmatrix} \quad
Y = \begin{bmatrix}0&1\cr-1&0\end{bmatrix} \quad
Z = \begin{bmatrix}1&0\cr0&-1\end{bmatrix} \quad
H = \tfrac{1}{\sqrt2}\begin{bmatrix}1&1\cr1&-1\end{bmatrix}$$
