import os
import tempfile
from unittest.mock import patch

import sec


def test_load_secret_from_path():
    """
    Make sure that the `_load_secret_from_path` function returns the contents
    of the file found in the provided path (stripped of any leading or
    trailing whitespaces) or `None` if the file does not exist.
    """
    license_path = os.path.join(os.getcwd(), "LICENSE")

    with open(license_path) as license_file:
        license = license_file.read().strip()

    assert sec._load_secret_from_path(license_path) == license
    assert sec._load_secret_from_path("/i/do/not/exist") is None


def test_load_from_run_secrets():
    """
    Make sure that the `_load_from_run_secrets` function calls
    `_load_secret_from_path` with the appropriate argument and returns its
    return value.
    """
    secret_name = "lesecret"
    secret_path = os.path.join("/run/secrets", secret_name)

    with patch("sec._load_secret_from_path") as load_from_path_mock:
        secret = sec._load_from_run_secrets(secret_name)

    load_from_path_mock.assert_called_once_with(secret_path)
    assert secret == load_from_path_mock.return_value


def test_load_from_environment_hint():
    """
    Make sure that the `_load_from_environment_hint` function calls
    `_load_secret_from_path` with the appropriate argument and returns its
    return value. If the "hinted" path does not exist, it should return `None`.
    """
    # Check for existing hint
    with patch("sec._load_secret_from_path") as load_from_path_mock:
        with tempfile.NamedTemporaryFile() as secret_file:
            secret_name = "mystiko"
            uppercase_secret_name = secret_name.upper()
            secret_environment_hint = f"{uppercase_secret_name}_FILE"
            os.environ[secret_environment_hint] = secret_file.name
            secret = sec._load_from_environment_hint(secret_name)

            load_from_path_mock.assert_called_once_with(secret_file.name)
            assert secret == load_from_path_mock.return_value

            del os.environ[secret_environment_hint]

    # Check for non existent hint
    secret_name = "idonotexist"
    secret = sec._load_from_environment_hint(secret_name)
    assert secret is None


def test_load_from_environment_variable():
    """
    Make sure that the `_load_from_environment_variable` function returns the
    contents of the corresponding environment variable, after sanitising the
    name of the secret.
    """
    environment_variable_name = "DATABASE_URL"
    secret = "postgres://USER:PASSWORD@HOST:PORT/NAME"

    assert sec._load_from_environment_variable(environment_variable_name) is None

    os.environ[environment_variable_name] = secret
    assert sec._load_from_environment_variable("DATABASE_URL") == secret
    assert sec._load_from_environment_variable("database_url") == secret
    assert sec._load_from_environment_variable("database/url") == secret

    del os.environ[environment_variable_name]


def test_parse_dotenv_line():
    assert sec._parse_dotenv_line("") is None
    assert sec._parse_dotenv_line("# comment") is None
    assert sec._parse_dotenv_line("MISSING") is None
    assert sec._parse_dotenv_line("PLAIN=hello # comment") == ("PLAIN", "hello")
    assert sec._parse_dotenv_line("export DATABASE_URL=postgres") == (
        "DATABASE_URL",
        "postgres",
    )
    assert sec._parse_dotenv_line("DATABASE_URL='postgres'") == (
        "DATABASE_URL",
        "postgres",
    )
    assert sec._parse_dotenv_line('UNICODE_SECRET="pa=ss # 🔐 café"') == (
        "UNICODE_SECRET",
        "pa=ss # 🔐 café",
    )


def test_load_from_dotenv_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        dotenv_path = os.path.join(temp_dir, ".env")

        with open(dotenv_path, "w", encoding="utf-8-sig") as dotenv_file:
            dotenv_file.write("# comment\n")
            dotenv_file.write("export DATABASE_URL='postgres://user:pass@host/db'\n")
            dotenv_file.write('UNICODE_SECRET="pa=ss # 🔐 café"\n')
            dotenv_file.write("PLAIN_SECRET=hello # trailing comment\n")

        assert (
            sec._load_from_dotenv_file("database_url", dotenv_path)
            == "postgres://user:pass@host/db"
        )
        assert (
            sec._load_from_dotenv_file("unicode_secret", dotenv_path)
            == "pa=ss # 🔐 café"
        )
        assert sec._load_from_dotenv_file("plain_secret", dotenv_path) == "hello"
        assert sec._load_from_dotenv_file("missing", dotenv_path) is None


def test_load():
    """
    Make sure that the `load` function returns the secret found in the first
    of the following cases:
      1. via `_load_from_run_secrets`
      2. via `_load_from_environment_hint`
      3. via `_load_from_environment_variable`
      4. None or the provided fallback
    """
    with patch("sec._load_from_run_secrets") as run_secrets_mock:
        with patch("sec._load_from_environment_hint") as env_hint_mock:
            with patch("sec._load_from_environment_variable") as env_var_mock:
                with patch("sec._load_from_dotenv_file") as dotenv_mock:
                    secret_name = "whoa"

                    # Test case 1
                    assert sec.load(secret_name) == run_secrets_mock.return_value

                    # Test case 2
                    run_secrets_mock.return_value = None
                    assert sec.load(secret_name) == env_hint_mock.return_value

                    # Test case 3
                    env_hint_mock.return_value = None
                    assert sec.load(secret_name) == env_var_mock.return_value

                    # Test case 4
                    env_var_mock.return_value = None
                    assert sec.load(secret_name) == dotenv_mock.return_value

                    # Test case 5
                    dotenv_mock.return_value = None
                    assert sec.load(secret_name) is None
                    assert sec.load(secret_name, "fallback") == "fallback"
