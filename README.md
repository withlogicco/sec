# Sec - Simple library for using secrets in Python applications

[![Build Status](https://travis-ci.org/sourcelair/sec.svg?branch=master)](https://travis-ci.org/sourcelair/sec)

Sec is a simple library for using secrets in Python applications. Simple to its core, Sec exposes just **one function** and offers **no configurations options**.

## Installation

To install `sec` use Pipenv to add it to the dependencies of your project

```
pipenv install sec
```

## Requirements

Sec requires Python 3.6 (or greater) to work.

## API Documentation

### `load(name, fallback=None)`

The `load` method of Sec attempts to load the contents of a secret, based on a given name, in the following order:

1. Load the contents of `/run/secrets/{name}` (`name` is lowercased here)
2. Load the contents of the path found in the environment variable `{name}_FILE` (`name` is uppercased here)
3. Load the content of the environment variable `{name}` (`name` is uppercased here)
4. Return the value of the `fallback` argument if provided, or `None`

## License

Sec is [`MIT Licensed`](LICENSE).
