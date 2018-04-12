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
    path = os.getenv(f"{name}_FILE")
    return _load_secret_from_path(path) if path else None


def _load_from_environment_variable(name: str) -> str:
    uppercase_name = name.upper()
    return os.getenv(uppercase_name)


def load_secret(name: str, fallback: str = None) -> str:
    secret = (
        _load_from_run_secrets(name)
        or _load_from_environment_hint(name)
        or _load_from_environment_variable(name)
        or fallback
    )
    return secret
