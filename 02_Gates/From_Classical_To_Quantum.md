# From Classical to Quantum Gates

The gates in [[Reversible_Classical_Gates]] (CNOT, CCNOT, CSWAP) can also be
applied in traditional computing. From here on the gates are for **quantum
computing**, so a few things need defining first.

## Definitions

- Use the **standard basis** $\left(\begin{bmatrix}1\\0\end{bmatrix}, \begin{bmatrix}0\\1\end{bmatrix}\right)$,
  where $|0\rangle = \begin{bmatrix}1\\0\end{bmatrix}$ and $|1\rangle = \begin{bmatrix}0\\1\end{bmatrix}$.
- Qubits have the form $a_0|0\rangle + a_1|1\rangle$ with $a_0^2 + a_1^2 = 1$;
  $a_0$ and $a_1$ are probability amplitudes.
- Usually the system has more than one qubit. For a 2-qubit system the basis is the
  tensor product of the standard basis with itself (see [[Tensor_Products]]):

$$\big(|0\rangle|0\rangle,\; |0\rangle|1\rangle,\; |1\rangle|0\rangle,\; |1\rangle|1\rangle\big) = \big(|00\rangle,\; |01\rangle,\; |10\rangle,\; |11\rangle\big)$$

## CNOT on basis states

| in | out | | in | out |
| :-: | :-: | :-: | :-: | :-: |
| $\vert 0\rangle\vert 0\rangle$ | $\vert 0\rangle\vert 0\rangle$ | | $\vert 00\rangle$ | $\vert 00\rangle$ |
| $\vert 0\rangle\vert 1\rangle$ | $\vert 0\rangle\vert 1\rangle$ | | $\vert 01\rangle$ | $\vert 01\rangle$ |
| $\vert 1\rangle\vert 0\rangle$ | $\vert 1\rangle\vert 1\rangle$ | | $\vert 10\rangle$ | $\vert 11\rangle$ |
| $\vert 1\rangle\vert 1\rangle$ | $\vert 1\rangle\vert 0\rangle$ | | $\vert 11\rangle$ | $\vert 10\rangle$ |

Because CNOT acts linearly, it can also be written on a general superposition —
it just swaps the last two amplitudes:

$$\text{CNOT}\big(r|00\rangle + s|01\rangle + t|10\rangle + u|11\rangle\big) = r|00\rangle + s|01\rangle + u|10\rangle + t|11\rangle$$

## Careful with what the output wires mean

A wire on the right of a diagram does **not** always carry a state of its own.

Take: top qubit $\tfrac{1}{\sqrt2}|0\rangle + \tfrac{1}{\sqrt2}|1\rangle$,
bottom qubit $|0\rangle$.

![[circuit_bell_prep.png|300]]

*(qubit 0 = top wire, put into superposition by $H$; qubit 1 = target.)*

The input state is:

$$\left(\tfrac{1}{\sqrt2}|0\rangle + \tfrac{1}{\sqrt2}|1\rangle\right)|0\rangle = \tfrac{1}{\sqrt2}|00\rangle + \tfrac{1}{\sqrt2}|10\rangle$$

CNOT acts on each basis vector separately, so this is sent to:

$$\tfrac{1}{\sqrt2}|00\rangle + \tfrac{1}{\sqrt2}|11\rangle$$

This is an **entangled state** ($ru \neq st$ — see [[Entanglement_Criterion]]).
We cannot assign individual states to the top and bottom wires on the right side;
the correct way to label the diagram is with one brace over both outputs:

```text
 1/√2|0⟩ + 1/√2|1⟩ ──────●──────  ⎫
                         │        ⎬  1/√2|00⟩ + 1/√2|11⟩
              |0⟩ ──────⊕──────  ⎭
```

This state is the one used as the starting resource in [[Superdense_Coding]] and
[[Quantum_Teleportation]].

## In Qiskit

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

qc = QuantumCircuit(2)
qc.h(0)        # top qubit into superposition
qc.cx(0, 1)    # CNOT: control 0, target 1
print(Statevector(qc))   # 1/√2 |00> + 1/√2 |11>
```

> [!warning] Bit ordering
> Qiskit is **little-endian**: in the label `|q1 q0⟩` the *rightmost* character is
> qubit 0. These notes write the control/first qubit on the left. For symmetric
> states like $\tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)$ it makes no difference,
> but for e.g. $|10\rangle$ it does — check the qubit indices, not the position in
> the string.
