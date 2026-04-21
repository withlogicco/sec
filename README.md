# Sec - Tiny Python library for using secrets

[![CI](https://github.com/withlogicco/sec/actions/workflows/ci.yml/badge.svg)](https://github.com/withlogicco/sec/actions/workflows/ci.yml)

Sec is a tiny Python library for using secrets. Simple to its core, Sec exposes just **one function** and offers **no configurations options**.

---

If you are developing web applications, then by most chances your application uses some sort of "secret" information (e.g. database passwords, API keys etc.) which hopefully 🙏 is not kept into the code base.

Since this kind of information is not kept in the database, it resides in an external place like a file (e.g. `/run/secrets/aws-key`) or an environment variable (e.g. `DATABASE_URL`).

All Sec does is provide a single, unique interface for accessing these information from a Python application.

## Installation

You can install `sec` with uv:

```
uv add sec
```

For local development, install the project and dev tools with:

```
uv sync --group dev
```

Quality checks use Ruff and pytest:

```
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Requirements

Sec requires Python 3.6 (or greater) to work.

## API Documentation

### `load(name, fallback=None)`

The `load` method of Sec attempts to load the contents of a secret, based on a given name, in the following order:

1. Load the contents of `/run/secrets/{name}` (`name` is lowercased here)
2. Load the contents of the path found in the environment variable `{name}_FILE` (`name` is uppercased here)
3. Load the content of the environment variable `{name}` (`name` is uppercased here)
4. Load the content of the `.env` file in the current working directory
5. Return the value of the `fallback` argument if provided, or `None`

## Quick Start Example

First, let's create some secret files

```shell
$ echo "supersecret" > /run/secrets/mystiko
$ export MYSECRET_FILE=/run/secrets/mystiko
$ export ANOTHER_SECRET=hello
$ echo "DATABASE_URL=postgresql://user:password@localhost/app" > .env
```

Next, let's open up the Python interpreter and load these secrets in our application.

```python
>>> import sec
>>> sec.load('mystiko')
'supersecret'
>>> sec.load('mysecret')
'supersecret'
>>> sec.load('another_secret')
'hello'
>>> sec.load('database_url')
'postgresql://user:password@localhost/app'
```

The `.env` support is intentionally dependency-free and understands simple `.env`
files, including blank lines, comments, `export KEY=value` entries, quoted
values, and UTF-8 content such as emoji or accented characters.

## Use Cases

### Docker Swarm Secrets

[Docker Secrets](https://docs.docker.com/engine/swarm/secrets/) lets services running on Docker Swarm get exclusive access to secret information that are encrypted at rest.

Although this feature is amazing, it cannot be used outside of Docker Swarm (e.g. in Docker on your local machine) so developers tend to create hacks and workarounds around this issue.

This is where `sec` comes into play. The following application code will work the same in production with Docker Secrets and in development with environment variables instead.

```python
import sec

# The following line will work the same in development and production
database_url = sec.load('database_url')
```

Below you can see the corresponding Docker files that we set up to run the above application.

#### `docker-compose.yml`

```yaml
version: "3.6"

services:
  web:
    image: company/app
    secrets:
      - database-url

secrets:
  settings:
    external:
      name: database-url
```

#### `docker-compose.override.yml`

```yaml
version: "3.6"

services:
  web:
    build: .
    volumes:
      - .:/usr/src/app
    environment:
      DATABASE_URL: postgresql://user:password@postgres

  postgres:
    image: postgres:latest

secrets:
  settings:
    external:
      name: database-url
```

## License

Sec is [`MIT Licensed`](LICENSE).
