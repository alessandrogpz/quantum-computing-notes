# Quantum Computing Notes

Notes and working code from studying quantum computing, built around
*Quantum Computing for Everyone* (Chris Bernhardt) and IBM's Qiskit.

The notes follow the book's approach and use **real probability amplitudes**
rather than complex ones. That is enough for everything up to the quantum Fourier
transform; [Real_vs_Complex_Amplitudes](01_Foundations/Real_vs_Complex_Amplitudes.md)
explains why, and where it stops.

Every protocol and algorithm here runs on a local simulator, or on real IBM
hardware with `--ibm`.

## Contents

| | |
| :--- | :--- |
| **[01_Foundations](01_Foundations/00_Foundations.md)** | Dirac notation, tensor products, the entanglement criterion, measurement from either party's perspective |
| **[02_Gates](02_Gates/00_Gates.md)** | Reversible classical gates, the move to qubits, single-qubit gates, involutions |
| **[03_Protocols](03_Protocols/00_Protocols.md)** | Superdense coding, teleportation, and the BB84 and E91 key-distribution protocols |
| **[04_Algorithms](04_Algorithms/00_Algorithms.md)** | Shor's algorithm factoring 15 |

Each folder has a `00_` index note with the reading order.

## Running the code

```bash
uv run python 02_Gates/gates.py                 # each gate's matrix and truth table
uv run python 03_Protocols/superdense_coding.py
uv run python 03_Protocols/teleportation.py
uv run python 03_Protocols/bb84.py --eve      # key distribution, with an eavesdropper
uv run python 03_Protocols/e91.py             # entanglement-based, tests CHSH
uv run python 04_Algorithms/shors.py
```

`uv run` uses the project's own Python; plain `python` will not find qiskit.
Add `--ibm` to any of them to run on real hardware, and `--help` for options.

Circuit diagrams are generated from the same circuits the scripts run:

```bash
uv run python _scripts/build_figures.py
```

## Running on IBM hardware

Copy the credentials template and add an API key from
[cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys):

```bash
cp .env.example .env
```

| Variable | Required | Notes |
| :--- | :-: | :--- |
| `QISKIT_API_KEY` | yes | IBM Cloud API key |
| `INSTANCE` | no | Instance CRN; blank uses your account default |

`.env` is gitignored, so each machine needs its own.

Results from real hardware are noisy — expect a weak signal rather than clean
output, and check the answer classically where you can.
