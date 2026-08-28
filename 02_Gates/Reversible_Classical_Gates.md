# Reversible Classical Gates

CNOT, Toffoli (CCNOT) and Fredkin (CSWAP) are gates that also exist in
**traditional computing**. They are all **involutions**: applying the operation
twice reverts the bits to their original state.

$$\forall (x,y):\quad f(x,y) = (x', y') \quad \text{and} \quad f(f(x,y)) = (x,y)$$

See [[Involutions]] for the general property.

## Controlled NOT gate (CNOT)

Flip the target $y$ if the control $x$ is 1.

| $x$ | $y$ | → | $x$ | $x \oplus y$ |
| :-: | :-: | :-: | :-: | :-: |
| 0 | 0 | | 0 | 0 |
| 0 | 1 | | 0 | 1 |
| 1 | 0 | | 1 | 1 |
| 1 | 1 | | 1 | 0 |

![[gate_cnot.png|200]]

$$C(x,y) = (x,\; x \oplus y)$$

## Toffoli gate (CCNOT)

Flip the target $z$ if **both** controls $x, y$ are 1.

| $x$ | $y$ | $z$ | → | $x$ | $y$ | $(x \wedge y) \oplus z$ |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 0 | 0 | 0 | | 0 | 0 | 0 |
| 0 | 0 | 1 | | 0 | 0 | 1 |
| 0 | 1 | 0 | | 0 | 1 | 0 |
| 0 | 1 | 1 | | 0 | 1 | 1 |
| 1 | 0 | 0 | | 1 | 0 | 0 |
| 1 | 0 | 1 | | 1 | 0 | 1 |
| 1 | 1 | 0 | | 1 | 1 | 1 |
| 1 | 1 | 1 | | 1 | 1 | 0 |

![[gate_toffoli.png|220]]

$$T(x,y,z) = \big(x,\; y,\; (x \wedge y) \oplus z\big)$$

## Fredkin gate (CSWAP)

Swap the targets $y, z$ if the control $x$ is 1.

| $x$ | $y$ | $z$ | → | $x$ | $(\neg x \wedge y) \vee (x \wedge z)$ | $(\neg x \wedge z) \vee (x \wedge y)$ |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 0 | 0 | 0 | | 0 | 0 | 0 |
| 0 | 0 | 1 | | 0 | 0 | 1 |
| 0 | 1 | 0 | | 0 | 1 | 0 |
| 0 | 1 | 1 | | 0 | 1 | 1 |
| 1 | 0 | 0 | | 1 | 0 | 0 |
| 1 | 0 | 1 | | 1 | 1 | 0 |
| 1 | 1 | 0 | | 1 | 0 | 1 |
| 1 | 1 | 1 | | 1 | 1 | 1 |

![[gate_fredkin.png|220]]

$$F(x,y,z) = \big(x,\; (\neg x \wedge y) \vee (x \wedge z),\; (\neg x \wedge z) \vee (x \wedge y)\big)$$

---

Next: [[From_Classical_To_Quantum]] — the same gates acting on qubits.
