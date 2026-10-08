---
marp: true
theme: default
paginate: true
math: katex
style: |
  section { font-size: 25px; }
  h1 { color: #c2185b; font-size: 42px; }
  h2 { color: #c2185b; font-size: 32px; }
  section.lead { text-align: center; }
  code { font-size: 0.85em; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; align-items: center; }
  .small { font-size: 0.82em; }
  section.gates .cols { grid-template-columns: 1.05fr 1fr; align-items: start; }
  section.gates table { width: 100%; font-size: 1.12em; }
  section.involution .cols { grid-template-columns: 1fr 1fr; align-items: start; }
  section.involution table { width: 100%; font-size: 0.86em; }
  section.run table { font-size: 0.8em; }
  section.run td, section.run th { padding: 0.12em 0.55em; }
  section.involution td, section.involution th { padding: 0.18em 0.5em; }
---

<!-- _class: lead -->

# Quantum Computing Fundamentals

From kets to key distribution

Alessandro Gentili Perez

<span class="small">Based on *Quantum Computing for Everyone* (Bernhardt), implemented in Qiskit</span>

---

## Everything here is 2D, and real

A qubit is a vector of length 1. With **real** amplitudes, every state sits on the
unit circle. **Kets** are column vectors; **bras** are their transpose.

$$|0\rangle = \begin{bmatrix}1\cr0\end{bmatrix} \qquad |1\rangle = \begin{bmatrix}0\cr1\end{bmatrix} \qquad \langle 0| = \begin{bmatrix}1 & 0\end{bmatrix}$$

![width:300px](images/circle_basis.png)

<span class="small">Complex amplitudes would fill a sphere instead. Not needed until the quantum Fourier transform.</span>

---

## A qubit, and why the squares sum to 1

$$|v\rangle = c_0|0\rangle + c_1|1\rangle \qquad c_0^2 + c_1^2 = 1$$

$c_0$ and $c_1$ are **probability amplitudes**. Measuring gives

$$P(0) = c_0^2 \qquad P(1) = c_1^2$$

so the normalisation condition is just "the probabilities add to 1".

**Standard basis** — $\{|0\rangle, |1\rangle\}$ — is orthonormal:

$$\langle 0|0\rangle = 1 \qquad \langle 1|1\rangle = 1 \qquad \langle 0|1\rangle = 0$$

<span class="small">A bra times a ket gives a number: the overlap between two states.</span>

---

## Two qubits: the tensor product

Alice has $|v\rangle = c_0|a_0\rangle + c_1|a_1\rangle$, Bob has $|w\rangle = d_0|b_0\rangle + d_1|b_1\rangle$.

$$|v\rangle \otimes |w\rangle = c_0d_0|a_0b_0\rangle + c_0d_1|a_0b_1\rangle + c_1d_0|a_1b_0\rangle + c_1d_1|a_1b_1\rangle$$

Name the four amplitudes:

$$r = c_0d_0 \qquad s = c_0d_1 \qquad t = c_1d_0 \qquad u = c_1d_1$$

It is still normalised, because

$$\underbrace{(c_0^2 + c_1^2)}_{1}\underbrace{(d_0^2 + d_1^2)}_{1} = r^2 + s^2 + t^2 + u^2 = 1$$

---

## The entanglement test

If the state really came from a tensor product, then

$$ru = c_0d_0 \cdot c_1d_1 = c_0c_1d_0d_1 \qquad st = c_0d_1 \cdot c_1d_0 = c_0c_1d_0d_1$$

They must be equal. So:

$$\boxed{\begin{aligned} ru = st &\Rightarrow \textbf{separable} \cr ru \neq st &\Rightarrow \textbf{entangled}\end{aligned}}$$

Separable means each qubit has a state of its own. Entangled means only the
**pair** has a state.

<span class="small">Equivalently: $ru - st$ is the determinant of $\begin{bmatrix}r & s\cr t & u\end{bmatrix}$, so separable = determinant zero.</span>

---

## Example A — not entangled

Alice $\left(\tfrac{1}{\sqrt2}, \tfrac{1}{\sqrt2}\right)$, Bob $\left(\tfrac12, \tfrac{\sqrt3}{2}\right)$. Tensor them:

$$r = \tfrac{1}{2\sqrt2} \quad s = \tfrac{\sqrt3}{2\sqrt2} \quad t = \tfrac{1}{2\sqrt2} \quad u = \tfrac{\sqrt3}{2\sqrt2}$$

**Test:** $ru = \tfrac{\sqrt3}{8}$ and $st = \tfrac{\sqrt3}{8}$. Equal → separable.

**Group by Alice's kets:**

$$|a_0\rangle\left(\tfrac{1}{2\sqrt2}|b_0\rangle + \tfrac{\sqrt3}{2\sqrt2}|b_1\rangle\right) + |a_1\rangle\left(\tfrac{1}{2\sqrt2}|b_0\rangle + \tfrac{\sqrt3}{2\sqrt2}|b_1\rangle\right)$$

**Normalise each bracket** — both have norm $\sqrt{\tfrac18 + \tfrac38} = \tfrac{1}{\sqrt2}$ — and Bob's part is a **common factor**:

$$= \left(\tfrac{1}{\sqrt2}|a_0\rangle + \tfrac{1}{\sqrt2}|a_1\rangle\right)\left(\tfrac12|b_0\rangle + \tfrac{\sqrt3}{2}|b_1\rangle\right)$$

---

## Example B — entangled

$$r = \tfrac12 \qquad s = \tfrac12 \qquad t = \tfrac{1}{\sqrt2} \qquad u = 0$$

**Test:** $ru = 0$ but $st = \tfrac{1}{2\sqrt2}$. Different → entangled.

**Group by Alice's kets and normalise the same way:**

$$\tfrac{1}{\sqrt2}|a_0\rangle\left(\tfrac{1}{\sqrt2}|b_0\rangle + \tfrac{1}{\sqrt2}|b_1\rangle\right) + \tfrac{1}{\sqrt2}|a_1\rangle|b_0\rangle$$

Bob's two brackets are now **different**, so nothing factors out. Neither qubit
has a state of its own.

**What that means:** Alice measures $|a_0\rangle$ or $|a_1\rangle$ with equal odds — but
her result decides Bob's. Get $|a_1\rangle$ and Bob is $|b_0\rangle$ with certainty.

---

<!-- _class: lead -->

# Gates

So far: how to **describe** a two-qubit state, and test whether it is entangled.

Now: how to **change** one — and how entanglement actually gets made.

![width:330px](images/gates_single.png)

---

## $I$ and $Z$ — leave the magnitudes alone

All of these act on $a_0|0\rangle + a_1|1\rangle$ in the standard basis.

$I$ is the **identity** — it does nothing:

$$I = \begin{bmatrix}1 & 0\cr 0 & 1\end{bmatrix} \qquad I\big(a_0|0\rangle + a_1|1\rangle\big) = a_0|0\rangle + a_1|1\rangle$$

$Z$ leaves both **magnitudes** unchanged but flips the sign of $a_1$ — the
**relative phase**:

$$Z = \begin{bmatrix}1 & 0\cr 0 & -1\end{bmatrix} \qquad Z\big(a_0|0\rangle + a_1|1\rangle\big) = a_0|0\rangle - a_1|1\rangle$$

Probabilities are unaffected, since $|-a_1|^2 = |a_1|^2$. The phase only becomes
visible once the qubit **interferes** with another — for instance after a Hadamard.

---

## $X$ and $Y$ — the two NOTs

Both exchange $|0\rangle$ and $|1\rangle$.

$$X = \begin{bmatrix}0 & 1\cr 1 & 0\end{bmatrix} \qquad\qquad Y = \begin{bmatrix}0 & 1\cr -1 & 0\end{bmatrix}$$

$$X\big(a_0|0\rangle + a_1|1\rangle\big) = a_1|0\rangle + a_0|1\rangle \qquad Y\big(a_0|0\rangle + a_1|1\rangle\big) = a_1|0\rangle - a_0|1\rangle$$

So $X$ is a pure swap; $Y$ swaps **and** changes the relative phase.

<span class="small">The Pauli $Y$ is usually $-i$ times the matrix above, giving $\begin{bmatrix}0 & -i\cr i & 0\end{bmatrix}$. The real version is used here because these slides avoid complex numbers — but only the complex one squares to $I$. Qiskit's `qc.y()` applies the complex one.</span>

---

## Hadamard — into superposition

$$H = \begin{bmatrix} \tfrac{1}{\sqrt2} & \tfrac{1}{\sqrt2} \cr \tfrac{1}{\sqrt2} & -\tfrac{1}{\sqrt2} \end{bmatrix} = \tfrac{1}{\sqrt2}\begin{bmatrix}1 & 1\cr 1 & -1\end{bmatrix} \qquad \begin{aligned} H|0\rangle &= \tfrac{1}{\sqrt2}\big(|0\rangle + |1\rangle\big) \cr H|1\rangle &= \tfrac{1}{\sqrt2}\big(|0\rangle - |1\rangle\big) \end{aligned}$$

<div class="cols">

![width:480px](images/gates_action.png)

<div>

In a diagram, a one-qubit gate is a square with its letter in it:

![width:290px](images/gates_single.png)

</div>

</div>

---

## Why Hadamard, specifically?

The $\tfrac{1}{\sqrt2}$ is not a choice. Without it $\begin{bmatrix}1&1\cr1&-1\end{bmatrix}|0\rangle$ has length$^2 = 2$,
so the probabilities would sum to 2. Every gate must preserve length.

<div class="cols">

<div>

**Plenty of gates make superposition:**

| | $P(0)$ | $P(1)$ |
| :--- | :-: | :-: |
| $R_y(\pi/3)\vert 0\rangle$ | 0.75 | 0.25 |
| $R_y(\pi/2)\vert 0\rangle$ | 0.50 | 0.50 |
| $R_y(2\pi/3)\vert 0\rangle$ | 0.25 | 0.75 |

$R_y(\pi/2)$ gives the **same** equal superposition as $H$ does from $|0\rangle$.

</div>

<div>

**But only $H$ undoes itself:**

$$H^2 = I \qquad R_y(\pi/2)^2 = R_y(\pi) \neq I$$

They agree on $|0\rangle$ and differ on $|1\rangle$ — that difference *is* the involution.

$H$ is a **basis change** between $Z$ and $X$, and swapping bases twice returns you home.

</div>

</div>

<span class="small">Every protocol here leans on that: the Bell circuit, Bob's decoder, BB84's $X$-basis measurement.</span>

---

<!-- _class: involution -->

## Involutions — gates that undo themselves

Applying one twice returns the input: $\boxed{U^2 = I}$

<div class="cols">

| Gate | Qubits | What it does |
| :--- | :-: | :--- |
| $X$ | 1 | swaps $\vert 0\rangle \leftrightarrow \vert 1\rangle$ |
| $Y$ | 1 | swaps, with phases |
| $Z$ | 1 | sign flip on $\vert 1\rangle$ |
| $H$ | 1 | basis change |
| CNOT | 2 | flip if control is 1 |
| SWAP | 2 | exchange the two |
| Toffoli | 3 | flip if both controls 1 |
| Fredkin | 3 | swap if control is 1 |

<div>

![width:450px](images/circuit_bell_involution.png)

At the barrier the state is $\tfrac{1}{\sqrt2}|00\rangle + \tfrac{1}{\sqrt2}|11\rangle$. Run the same two gates again and you are back at $|00\rangle$.

<span class="small">That "un-preparing" step is exactly what Bob does in superdense coding, and Alice in teleportation.</span>

</div>

</div>

---

## CNOT, and making entanglement

A single-qubit gate can **never** entangle. You need a two-qubit gate.

<div class="cols">

![width:380px](images/circuit_bell.png)

```python
qc = QuantumCircuit(2)
qc.h(0)        # superposition
qc.cx(0, 1)    # entangle
```

</div>

$$|00\rangle \xrightarrow{H} \tfrac{1}{\sqrt2}(|00\rangle + |10\rangle) \xrightarrow{CNOT} \tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)$$

Test it: $r = u = \tfrac{1}{\sqrt2}$, $s = t = 0$, so $ru = \tfrac12 \neq 0 = st$. **Entangled.**

---

## And it shows up in the measurements

<div class="cols">

![width:400px](images/hist_bell.png)

Only `00` and `11`. Never `01` or `10`.

The two qubits always agree — but neither had a value before measurement.

This **Bell pair** is the resource every protocol below is built on.

</div>

---

## Superdense coding

Send **2 classical bits** by physically transmitting **1 qubit**.

![width:560px](images/circuit_superdense_01.png)

**Alice owns q0, Bob owns q1** — they share $\tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)$, one each.
Alice applies one gate to **her qubit only**, sends it to Bob, and he — now holding
both — undoes the Bell circuit.

| Bob finally reads | 00 | 01 | 10 | 11 |
|:--|:-:|:-:|:-:|:-:|
| so Alice applies | $I$ | $X$ | $Z$ | $ZX$ |

<span class="small">The top row is the **message Bob reads after decoding** — not the state in flight.</span>

---

## Superdense coding — why it works

$$|00\rangle \xrightarrow{H} \tfrac{1}{\sqrt2}(|00\rangle + |10\rangle) \xrightarrow{CNOT} \tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)$$

Alice applies $X$ to send `01`:

$$\xrightarrow{X} \tfrac{1}{\sqrt2}(|10\rangle + |01\rangle)$$

Bob reverses the Bell circuit:

$$\xrightarrow{CNOT} \tfrac{1}{\sqrt2}(|11\rangle + |01\rangle) \xrightarrow{H} |01\rangle \quad \textsf{— the two bits he reads}$$

```python
qc.h(0); qc.cx(0, 1)      # Bell pair, shared in advance
qc.x(0)                   # Alice encodes "01" on her qubit alone
qc.cx(0, 1); qc.h(0)      # Bob decodes
```

<span class="small">The four gates map the pair onto four distinguishable Bell states. Entanglement is what lets one qubit carry two bits.</span>

---

## Quantum teleportation

Move **1 qubit's state** using **2 classical bits**. The exact opposite trade.

![width:790px](images/circuit_teleportation.png)

**Alice owns `psi` and `alice`; Bob owns `bob`.** She entangles her state with her
half of the pair, measures both of hers, and sends two classical bits — nothing
quantum crosses. Bob corrects his qubit.

| Bob receives | 00 | 01 | 10 | 11 |
|:--|:-:|:-:|:-:|:-:|
| Bob applies | $I$ | $X$ | $Z$ | $Y$ |

---

## Teleportation — the catch

The state is **not copied** — no-cloning forbids that. Alice's measurement
destroys her copy at the moment Bob's appears.

Nothing travels faster than light either: without the 2 classical bits, Bob's
qubit is useless. Each of his four possible states is equally likely.

```python
qc.ry(theta, psi)              # the state to send
qc.h(a); qc.cx(a, b)           # shared Bell pair
qc.cx(psi, a); qc.h(psi)       # Alice: reverse Bell circuit
qc.measure(psi, c[0]); qc.measure(a, c[1])
with qc.if_test((c[1], 1)): qc.x(b)    # Bob corrects
with qc.if_test((c[0], 1)): qc.z(b)
```

<span class="small">Verified in `teleportation.py`: $|0\rangle$, $|1\rangle$, $|+\rangle$ and $R_y(\pi/3)|0\rangle$ all arrive in 100% of shots.</span>

---

## BB84 — detecting an eavesdropper

Not encryption. It produces a shared random key **and tells you if anyone looked**.
$Z = \lbrace|0\rangle, |1\rangle\rbrace$ and $X = \lbrace|+\rangle, |-\rangle\rbrace$ are **conjugate** — certain in one, a coin flip in the other.

![width:430px](images/circuit_bb84_clean.png)

<div class="cols">

<div>

**One qubit, changing hands.** `channel` is Alice's before the barrier, Bob's after.

- `X` — Alice's **bit**: present 1, absent 0
- first `H` — her **basis**: present $X$, absent $Z$
- second `H` — **Bob's** basis, picked blind

</div>

<div>

**The order is the security:**

1. Alice sends the qubit
2. Bob measures **immediately**, guessing a basis
3. *Then* they announce bases — never bits
4. Discard the mismatches

</div>

</div>

<span class="small">Bases match → the two $H$s cancel, $H^2 = I$ → Bob reads her bit exactly. Bases differ → one lone $H$ → a coin flip.</span>

---

<!-- _class: run -->

## BB84 — eight rounds, start to finish

Alice flips **two** coins (bit, basis). Bob flips **one** (basis), blind.

| # | A bit | A base | sends | B base | B reads | match? | |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| 0 | 1 | $X$ | $\vert-\rangle$ | $X$ | **1** | yes | **key** |
| 1 | 0 | $Z$ | $\vert 0\rangle$ | $X$ | 0 | no | discard — right by luck |
| 2 | 0 | $Z$ | $\vert 0\rangle$ | $X$ | 1 | no | discard — **wrong** |
| 3 | 1 | $Z$ | $\vert 1\rangle$ | $Z$ | **1** | yes | **key** |
| 4 | 0 | $X$ | $\vert+\rangle$ | $X$ | **0** | yes | **key** |
| 5 | 0 | $Z$ | $\vert 0\rangle$ | $Z$ | **0** | yes | **key** |
| 6 | 0 | $Z$ | $\vert 0\rangle$ | $Z$ | **0** | yes | **key** |
| 7 | 0 | $Z$ | $\vert 0\rangle$ | $X$ | 0 | no | discard |

They announce their **bases** publicly — never the bits — and drop the mismatches.
Alice keeps `1 1 0 0 0`, Bob keeps `1 1 0 0 0`: a secret neither of them sent.

<span class="small">Rounds 1 and 2 are the point — same choices, different outcomes. On a mismatch Bob still gets a bit, just a worthless one, and nobody knows which until the bases are announced.</span>

---

## BB84 — what Eve costs

![width:560px](images/circuit_bb84_eve.png)

Eve cannot copy the qubit (**no-cloning**), so she must measure — and guess a basis.

She is wrong half the time, and then Bob errs half of *those*:

$$\text{QBER} = \tfrac12 \times \tfrac12 = 25\text{\%}$$

Alice and Bob sacrifice some bits, compare them openly, and abort above **11%**.

<span class="small">Her gain: 75% of the key. Useless, because the key is discarded.</span>

---

## E91 — the same job, via Bell's theorem

<div class="cols">

![width:430px](images/circuit_e91.png)

A source emits entangled pairs. Each side measures along a randomly chosen axis.

$$E(\theta_a, \theta_b) = \cos(\theta_a - \theta_b)$$

</div>

Combine four settings into the **CHSH** sum $S$. Any theory where the bits existed
before measurement obeys $|S| \le 2$. Quantum mechanics reaches $2\sqrt2 \approx 2.83$.

Eve has to entangle herself with the pair to learn anything — and **monogamy of
entanglement** means that halves every correlation, dropping $S$ to $1.41$.

<span class="small">Measured: $S = 2.78 \pm 0.07$ clean, $1.34$ with Eve. The eavesdropper is visible as a *failed violation*.</span>

---

<!-- _class: lead -->

## Recap

| | sends | adversary | needs entanglement |
|:--|:--|:-:|:-:|
| Superdense coding | 2 bits via 1 qubit | no | yes |
| Teleportation | 1 qubit via 2 bits | no | yes |
| BB84 | a secret key | **yes** | no |
| E91 | a secret key | **yes** | yes |

All four run locally or on IBM hardware with `--ibm`.

<span class="small">github.com/alessandrogpz/quantum-computing-notes</span>
