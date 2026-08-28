# Measurement and Perspective

Continues the entangled example from [Entanglement_Criterion](Entanglement_Criterion.md):

$$r = \tfrac12, \quad s = \tfrac12, \quad t = \tfrac{1}{\sqrt2}, \quad u = 0$$

The same physical state can be grouped from either side. The grouping does not
change the state — it just makes one person's measurement outcomes readable.

## Alice's perspective

$$\tfrac12|a_0\rangle|b_0\rangle + \tfrac12|a_0\rangle|b_1\rangle + \tfrac{1}{\sqrt2}|a_1\rangle|b_0\rangle + 0\,|a_1\rangle|b_1\rangle$$

$$= |a_0\rangle\left(\tfrac12|b_0\rangle + \tfrac12|b_1\rangle\right) + |a_1\rangle\left(\tfrac{1}{\sqrt2}|b_0\rangle + 0\,|b_1\rangle\right)$$

Normalizing each bracket:

$$\left\|\tfrac12, \tfrac12\right\| = \sqrt{\left(\tfrac12\right)^2 + \left(\tfrac12\right)^2} = \tfrac{1}{\sqrt2}
\qquad
\left\|\tfrac{1}{\sqrt2}, 0\right\| = \sqrt{\left(\tfrac{1}{\sqrt2}\right)^2 + 0^2} = \tfrac{1}{\sqrt2}$$

$$= \tfrac{1}{\sqrt2}|a_0\rangle\left(\tfrac{1}{\sqrt2}|b_0\rangle + \tfrac{1}{\sqrt2}|b_1\rangle\right) + \tfrac{1}{\sqrt2}|a_1\rangle\left(|b_0\rangle + 0\,|b_1\rangle\right)$$

Here Bob's vectors are **different** in the two terms, so they cannot be pulled
out as a common factor — this is what entanglement looks like algebraically.

**Alice measures first.** The amplitudes in front of her kets are both
$\tfrac{1}{\sqrt2}$, so she gets $\tfrac12$ for $|a_0\rangle$ and $\tfrac12$ for
$|a_1\rangle$. But once her outcome is fixed, **Bob's state is determined**:

| Alice gets | Bob's state collapses to | meaning |
| :--- | :--- | :--- |
| $\vert a_0\rangle$ ($\vert a_1\rangle$ is gone) | $\tfrac{1}{\sqrt2}\vert b_0\rangle + \tfrac{1}{\sqrt2}\vert b_1\rangle$ | Bob has equal chances of $\vert b_0\rangle$ or $\vert b_1\rangle$ |
| $\vert a_1\rangle$ ($\vert a_0\rangle$ is gone) | $\vert b_0\rangle + 0\,\vert b_1\rangle$ | Bob is guaranteed to be $\vert b_0\rangle$ |

## Bob's perspective

The same state, grouped by Bob's kets instead:

$$\tfrac12|a_0\rangle|b_0\rangle + \tfrac12|a_0\rangle|b_1\rangle + \tfrac{1}{\sqrt2}|a_1\rangle|b_0\rangle + 0\,|a_1\rangle|b_1\rangle$$

$$= \left(\tfrac12|a_0\rangle + \tfrac{1}{\sqrt2}|a_1\rangle\right)|b_0\rangle + \left(\tfrac12|a_0\rangle + 0\,|a_1\rangle\right)|b_1\rangle$$

Normalizing each bracket:

$$\left\|\tfrac12, \tfrac{1}{\sqrt2}\right\| = \sqrt{\left(\tfrac12\right)^2 + \left(\tfrac{1}{\sqrt2}\right)^2} = \sqrt{\tfrac34} = \tfrac{\sqrt3}{2}
\qquad
\left\|\tfrac12, 0\right\| = \tfrac12$$

$$= \left(\tfrac{1}{\sqrt3}|a_0\rangle + \tfrac{\sqrt2}{\sqrt3}|a_1\rangle\right)\tfrac{\sqrt3}{2}|b_0\rangle + \left(|a_0\rangle + 0\,|a_1\rangle\right)\tfrac12|b_1\rangle$$

**Bob measures first.** From the outside factors, Bob has
$\left(\tfrac{\sqrt3}{2}\right)^2 = \tfrac34$ chance of $|b_0\rangle$ and
$\left(\tfrac12\right)^2 = \tfrac14$ chance of $|b_1\rangle$.

| Bob gets | Alice's state collapses to | Alice's odds |
| :--- | :--- | :--- |
| $\vert b_0\rangle$ ($\vert b_1\rangle$ disappears) | $\tfrac{1}{\sqrt3}\vert a_0\rangle + \tfrac{\sqrt2}{\sqrt3}\vert a_1\rangle$ | $\tfrac13$ for $\vert a_0\rangle$, $\tfrac23$ for $\vert a_1\rangle$ |
| $\vert b_1\rangle$ ($\vert b_0\rangle$ disappears) | $\vert a_0\rangle + 0\,\vert a_1\rangle$ | 100% $\vert a_0\rangle$ |

## Takeaway

Whoever measures first sees the marginal probabilities of *their own* grouping;
the other person's state is then conditioned on that outcome. Both groupings
describe the same state, so the joint statistics come out the same either way.
