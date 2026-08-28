# Algorithms

Quantum algorithms, each with a runnable Qiskit implementation beside the note.

| Note | Code | Does what |
| :--- | :--- | :--- |
| [Shors_Algorithm](Shors_Algorithm.md) | [`shors_15.py`](shors_15.py) | factors $N = 15$ into $3 \times 5$ by period-finding, simulated exactly |
| [↳ on hardware](Shors_Algorithm.md#running-it-on-real-ibm-hardware) | [`shors_15_ibm.py`](shors_15_ibm.py) | the same circuit transpiled and submitted to an IBM device |

## The line where complex amplitudes become mandatory

The rest of this vault uses **real** probability amplitudes (see
[Real_vs_Complex_Amplitudes](../99_TODO/Real_vs_Complex_Amplitudes.md)). That works through entanglement, teleportation,
superdense coding and Grover's search.

It stops here. [Shors_Algorithm](Shors_Algorithm.md) is built on the quantum Fourier transform, whose
phases $e^{-i\pi/2^k}$ have no real-valued form. Anything in this folder built on
the QFT — phase estimation, order finding, Shor — needs $i$.

## Shape shared by these algorithms

Most quantum algorithms follow the same three beats, and Shor is a clean example:

1. **Superpose** — put a register into every input state at once.
2. **Compute into phase or entanglement** — apply the function so the answer is
   encoded in the state, but not yet readable.
3. **Interfere** — apply a transform (usually the inverse QFT) that concentrates
   amplitude on the outcomes you want, so measurement reveals the answer.

Step 2 is not "parallel search". Measuring after step 2 gives a random answer. The
algorithm lives in step 3.
