import ast
import os
from typing import Optional, Tuple


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


def _parse_dotenv_line(line: str) -> Optional[Tuple[str, str]]:
    stripped_line = line.strip()

    if not stripped_line or stripped_line.startswith("#"):
        return None

    if stripped_line.startswith("export "):
        stripped_line = stripped_line[len("export ") :].strip()

    if "=" not in stripped_line:
        return None

    key, value = stripped_line.split("=", 1)
    key = key.strip()
    value = value.strip()

    if not key:
        return None

    value = _parse_dotenv_value(value)

    return key, value


def _parse_dotenv_value(value: str) -> str:
    if not value:
        return ""

    if value[0] in {'"', "'"}:
        return _parse_quoted_dotenv_value(value)

    comment_index = _find_unquoted_comment_index(value)
    if comment_index is not None:
        value = value[:comment_index]

    return value.rstrip()


def _parse_quoted_dotenv_value(value: str) -> str:
    quote_character = value[0]
    escaped = False

    for index in range(1, len(value)):
        character = value[index]

        if escaped:
            escaped = False
            continue

        if character == "\\":
            escaped = True
            continue

        if character == quote_character:
            literal = value[: index + 1]
            remainder = value[index + 1 :].strip()

            if remainder and not remainder.startswith("#"):
                raise ValueError("Invalid trailing content in .env value")

            return ast.literal_eval(literal)

    raise ValueError("Unterminated quoted value in .env file")


def _find_unquoted_comment_index(value: str) -> Optional[int]:
    for index, character in enumerate(value):
        if character != "#":
            continue

        if index == 0 or value[index - 1].isspace():
            return index

    return None


def _load_from_dotenv_file(name: str, dotenv_path: str = ".env") -> Optional[str]:
    sanitized_name = _sanitize_environment_variable_name(name)

    if not os.path.exists(dotenv_path):
        return None

    with open(dotenv_path, "r", encoding="utf-8-sig") as dotenv_file:
        for line in dotenv_file:
            try:
                parsed_entry = _parse_dotenv_line(line)
            except (SyntaxError, ValueError):
                continue

            if parsed_entry is None:
                continue

            key, value = parsed_entry
            if key == sanitized_name:
                return value

    return None


def load(name: str, fallback: str = None) -> Optional[str]:
    """
    Searches for and returns the first secret that matches the following
    criteria in the order described:

      1. The contents of `/run/secrets/{lowercase_secret_name}`
      2. The contents of the path in the env var `{uppercase_secret_name}_FILE`
      3. The contents of the env var `{uppercase_secret_name}`
      4. The contents of `{pwd}/.env`
      5. The provided fallback (if any)
    """
    secret = (
        _load_from_run_secrets(name)
        or _load_from_environment_hint(name)
        or _load_from_environment_variable(name)
        or _load_from_dotenv_file(name)
        or fallback
    )
    return secret
