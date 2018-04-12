import os


def _load_secret_from_path(path: str) -> str:
    if not os.path.exists(path):
        return None

    with open(path, "r") as secret_file:
        return secret_file.read().strip()


def _load_from_run_secrets(name: str) -> str:
    lowercase_name = name.lower()
    path = f"/run/secrets/{lowercase_name}"
    return _load_secret_from_path(path)


def _load_from_environment_hint(name: str) -> str:
    uppercase_name = name.upper()
    path = os.getenv(f"{uppercase_name}_FILE")
    return _load_secret_from_path(path) if path else None


def _load_from_environment_variable(name: str) -> str:
    uppercase_name = name.upper()
    return os.getenv(uppercase_name)


def load(name: str, fallback: str = None) -> str:
    """
    Searches for and returns the first secret that matches the following
    criteria in the order described:

      1. The contents of `/run/secrets/{lowercase_secret_name}`
      2. The contents of the path in the env var `{uppercase_secret_name}_FILE`
      3. The contents of the env var `{uppercase_secret_name}`
      4. The provided fallback (if any)
    """
    secret = (
        _load_from_run_secrets(name)
        or _load_from_environment_hint(name)
        or _load_from_environment_variable(name)
        or fallback
    )
    return secret
