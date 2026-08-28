# Entanglement Criterion

Given a two-qubit state written in the amplitudes of [Tensor_Products](Tensor_Products.md):

$$r\,|a_0\rangle|b_0\rangle + s\,|a_0\rangle|b_1\rangle + t\,|a_1\rangle|b_0\rangle + u\,|a_1\rangle|b_1\rangle$$

## The test

If the state came from a tensor product of two independent qubits, then
$r = c_0d_0$, $s = c_0d_1$, $t = c_1d_0$, $u = c_1d_1$, and therefore:

$$ru = c_0d_0 \cdot c_1d_1 = c_0c_1d_0d_1$$
$$st = c_0d_1 \cdot c_1d_0 = c_0c_1d_0d_1$$

The two are identical. This gives the criterion:

$$\boxed{
\begin{aligned}
ru = st &\;\Rightarrow\; \text{particles are NOT entangled (separable)} \\
ru \neq st &\;\Rightarrow\; \text{particles ARE entangled}
\end{aligned}}$$

Intuitively: if $ru = st$ the state factors back into "Alice's part times Bob's
part", so each qubit has a state of its own. If not, no such factoring exists —
neither qubit has an individual state, only the pair does.

## Worked example — not entangled

$$r = \tfrac{1}{2\sqrt2}, \quad s = \tfrac{\sqrt3}{2\sqrt2}, \quad t = \tfrac{1}{2\sqrt2}, \quad u = \tfrac{\sqrt3}{2\sqrt2}$$

Check normalization: $\tfrac18 + \tfrac38 + \tfrac18 + \tfrac38 = 1$ ✓
Check the criterion: $ru = \tfrac{\sqrt3}{8} = st$ → **not entangled**.

Writing $|v\rangle \otimes |w\rangle$ and grouping from **Alice's perspective**
(factor out her basis kets):

$$\tfrac{1}{2\sqrt2}|a_0\rangle|b_0\rangle + \tfrac{\sqrt3}{2\sqrt2}|a_0\rangle|b_1\rangle + \tfrac{1}{2\sqrt2}|a_1\rangle|b_0\rangle + \tfrac{\sqrt3}{2\sqrt2}|a_1\rangle|b_1\rangle$$

$$= |a_0\rangle\left(\tfrac{1}{2\sqrt2}|b_0\rangle + \tfrac{\sqrt3}{2\sqrt2}|b_1\rangle\right) + |a_1\rangle\left(\tfrac{1}{2\sqrt2}|b_0\rangle + \tfrac{\sqrt3}{2\sqrt2}|b_1\rangle\right)$$

Each bracket must be normalized before it can be read as a state. Its norm is:

$$\|\cdot\| = \sqrt{\sum_i c_i^2} = \sqrt{\left(\tfrac{1}{2\sqrt2}\right)^2 + \left(\tfrac{\sqrt3}{2\sqrt2}\right)^2} = \sqrt{\tfrac18 + \tfrac38} = \tfrac{1}{\sqrt2}$$

Pulling that factor out to leave unit vectors inside:

$$= \tfrac{1}{\sqrt2}|a_0\rangle\left(\tfrac12|b_0\rangle + \tfrac{\sqrt3}{2}|b_1\rangle\right) + \tfrac{1}{\sqrt2}|a_1\rangle\left(\tfrac12|b_0\rangle + \tfrac{\sqrt3}{2}|b_1\rangle\right)$$

Bob's vector is now a **common factor**, so it pulls apart:

$$= \left(\tfrac{1}{\sqrt2}|a_0\rangle + \tfrac{1}{\sqrt2}|a_1\rangle\right)\left(\tfrac12|b_0\rangle + \tfrac{\sqrt3}{2}|b_1\rangle\right)$$

If Alice measures first she gets $\tfrac12$ chance of $|a_0\rangle$ and $\tfrac12$
chance of $|a_1\rangle$, and **her result has no influence on Bob's measurement** —
his state is the same either way.

## Worked example — entangled

$$r = \tfrac12, \quad s = \tfrac12, \quad t = \tfrac{1}{\sqrt2}, \quad u = 0$$

Check normalization: $\tfrac14 + \tfrac14 + \tfrac12 + 0 = 1$ ✓
Check the criterion: $ru = 0$, $st = \tfrac{1}{2\sqrt2}$ → $ru \neq st$ → **entangled**.

See [Measurement_and_Perspective](Measurement_and_Perspective.md) for what happens when this state is measured.
