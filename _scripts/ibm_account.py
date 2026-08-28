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


# IBM's own error strings, mapped to what to actually do about them.
DIAGNOSES = (
    ("disabled", """Your API key exists but IBM has DISABLED it.

  This is an account-side state, not a problem with .env -- the token was read
  and sent correctly, and IBM answered. Nothing local will fix it.

  Fix: create a fresh key at
      https://cloud.ibm.com/iam/apikeys
  ("Create" -> copy it immediately, it is shown only once), then replace
  QISKIT_API_KEY in .env.

  A key ends up disabled when it is revoked by hand, when its service ID is
  disabled, or when the IBM Cloud account itself is suspended or its trial
  plan has lapsed. If a new key is disabled straight away, the account is the
  problem, not the key -- check https://cloud.ibm.com/account for a banner."""),
    ("not found", """The INSTANCE in .env does not match any instance on this account.

  Fix: leave INSTANCE blank to use your default, or copy the CRN from
      https://quantum.cloud.ibm.com/instances"""),
    ("invalid", """IBM rejected the API key as invalid.

  Check for a truncated paste or stray whitespace in .env, then verify at
      https://cloud.ibm.com/iam/apikeys"""),
    ("unauthorized", """The key authenticated but lacks permission for this instance.

  Check the instance CRN in .env, or leave it blank for your default."""),
)


def get_service():
    """Return an authenticated QiskitRuntimeService, with legible failures."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    env = load_env()
    kwargs = {
        "channel": env.get("CHANNEL", "ibm_quantum_platform"),
        "token": env["QISKIT_API_KEY"],
    }
    if env.get("INSTANCE"):
        kwargs["instance"] = env["INSTANCE"]

    try:
        return QiskitRuntimeService(**kwargs)
    except Exception as exc:
        text = f"{exc} {exc.__cause__ or ''}".lower()
        for needle, advice in DIAGNOSES:
            if needle in text:
                raise SystemExit(f"\nIBM rejected your credentials.\n\n  {advice}\n") from exc
        raise


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
