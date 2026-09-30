"""Run a circuit either locally or on IBM hardware.

Every script in this repo uses this, so they all work the same way:

    from backend import run
    counts = run(circuit, shots=1024)            # local simulator
    counts = run(circuit, shots=1024, ibm=True)  # real IBM device

Local runs need nothing but qiskit. IBM runs read credentials from the .env file
in the repo root (copy .env.example and fill in QISKIT_API_KEY).
"""

import pathlib

from qiskit import transpile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"


def load_env() -> dict[str, str]:
    if not ENV.exists():
        raise SystemExit(
            f"No {ENV.name} file. Copy the template and add your IBM token:\n"
            f"    cp .env.example .env"
        )
    env = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip("'\"")
    if not env.get("QISKIT_API_KEY"):
        raise SystemExit("QISKIT_API_KEY is empty in .env")
    return env


def service():
    from qiskit_ibm_runtime import QiskitRuntimeService

    env = load_env()
    kwargs = {"channel": "ibm_quantum_platform", "token": env["QISKIT_API_KEY"]}
    if env.get("INSTANCE"):
        kwargs["instance"] = env["INSTANCE"]
    try:
        return QiskitRuntimeService(**kwargs)
    except Exception as exc:
        if "disabled" in f"{exc} {exc.__cause__ or ''}".lower():
            raise SystemExit(
                "IBM has disabled this API key. Create a new one at\n"
                "    https://cloud.ibm.com/iam/apikeys\n"
                "and replace QISKIT_API_KEY in .env"
            ) from exc
        raise


def run(circuit, shots: int = 1024, ibm: bool = False, backend_name: str | None = None):
    """Run the circuit and return a {bitstring: count} dict."""
    creg = circuit.cregs[0].name

    if not ibm:
        # Aer rather than StatevectorSampler: teleportation uses mid-circuit
        # measurement and classical feed-forward, which the statevector sampler
        # cannot execute.
        from qiskit_aer import AerSimulator

        sim = AerSimulator()
        return sim.run(transpile(circuit, sim), shots=shots).result().get_counts()

    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    svc = service()
    backend = (svc.backend(backend_name) if backend_name
               else svc.least_busy(simulator=False, operational=True))
    isa = generate_preset_pass_manager(backend=backend, optimization_level=3).run(circuit)
    print(f"  backend {backend.name}, depth {isa.depth()}, "
          f"{sum(n for g, n in isa.count_ops().items() if g in ('cz', 'ecr', 'cx'))} 2q gates")

    sampler = SamplerV2(mode=backend)
    sampler.options.dynamical_decoupling.enable = True
    sampler.options.twirling.enable_gates = True
    job = sampler.run([(isa, None, shots)])
    print(f"  job {job.job_id()}")
    return getattr(job.result()[0].data, creg).get_counts()
