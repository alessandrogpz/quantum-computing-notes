"""IBM Quantum credentials, loaded from the vault's gitignored .env file.

Fill in .env (never .env.example) and any script here can reach hardware:

    from ibm_account import get_service
    service = get_service()

.env is listed in .gitignore, so it stays on this machine and is never pushed.
.env.example is the committed template and must never contain a real token.

The token is passed straight to QiskitRuntimeService rather than written to
~/.qiskit/, so your credentials live in exactly one file that you control.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"

REQUIRED = ("QISKIT_API_KEY",)
OPTIONAL = ("INSTANCE", "CHANNEL")


def load_env(path: pathlib.Path = ENV_PATH) -> dict[str, str]:
    """Parse a KEY=value file. Ignores blanks, comments and surrounding quotes."""
    if not path.exists():
        raise SystemExit(
            f"No credentials file at {path}\n\n"
            f"Create one by copying the template:\n"
            f"    cp {EXAMPLE_PATH.name} {path.name}\n"
            f"then paste your token into it. {path.name} is gitignored."
        )

    env: dict[str, str] = {}
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise SystemExit(f"{path.name}:{n}: expected KEY=value, got {raw!r}")
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip("'\"")

    missing = [k for k in REQUIRED if not env.get(k)]
    if missing:
        raise SystemExit(
            f"{path.name} is missing a value for: {', '.join(missing)}\n"
            f"Get a token from https://quantum.cloud.ibm.com/"
        )
    return env


def get_service():
    """Return an authenticated QiskitRuntimeService."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    env = load_env()
    kwargs = {
        "channel": env.get("CHANNEL", "ibm_quantum_platform"),
        "token": env["QISKIT_API_KEY"],
    }
    if env.get("INSTANCE"):
        kwargs["instance"] = env["INSTANCE"]
    return QiskitRuntimeService(**kwargs)


def describe() -> None:
    """Print what is configured, without ever revealing the token."""
    env = load_env()
    token = env["QISKIT_API_KEY"]
    print(f"  file      {ENV_PATH}")
    print(f"  token     {token[:4]}...{token[-4:]}  ({len(token)} chars)")
    print(f"  channel   {env.get('CHANNEL', 'ibm_quantum_platform')}")
    print(f"  instance  {env.get('INSTANCE') or '(not set, will use your default)'}")


if __name__ == "__main__":
    describe()
