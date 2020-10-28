from typing import Optional
import os


def _sanitize_environment_variable_name(name: str) -> str:
    uppercase_name = name.upper()
    sanitized_name = uppercase_name.replace("/", "_")
    return sanitized_name


def _load_secret_from_path(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None

    with open(path, "r") as secret_file:
        return secret_file.read().strip()


def _load_from_run_secrets(name: str) -> Optional[str]:
    lowercase_name = name.lower()
    path = f"/run/secrets/{lowercase_name}"
    return _load_secret_from_path(path)


def _load_from_environment_hint(name: str) -> Optional[str]:
    uppercase_name = name.upper()
    path = os.getenv(f"{uppercase_name}_FILE")
    return _load_secret_from_path(path) if path else None


def _load_from_environment_variable(name: str) -> Optional[str]:
    sanitized_name = _sanitize_environment_variable_name(name)
    return os.getenv(sanitized_name)


def load(name: str, fallback: str = None) -> Optional[str]:
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
