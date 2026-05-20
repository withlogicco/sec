# AGENTS.md

## Scope

These instructions apply to the entire repository.

## Project Rules

- Preserve the public API. Do not change the `sec.load(name, fallback=None)` signature or the documented lookup order unless a task explicitly asks for it.
- Use `uv` for local development, dependency management, and packaging workflows.
- Keep automation in GitHub Actions only. Do not add Travis, Pipenv, Poetry, or parallel CI tooling back into the repository.
- Use Ruff for formatting and linting. Do not introduce Black, isort, or Flake8-style tooling.
- Keep `.env` support dependency-free. It must remain UTF-8 friendly and continue to handle quoted values, comments, and `export KEY=value` entries.

## Validation

- Run `uv run ruff check .`
- Run `uv run ruff format --check .`
- Run `uv run pytest`
