# Contributing

## Setup

```bash
pip install -e .[dev]
pre-commit install
```

## Local checks

```bash
ruff check .
black --check .
mypy agentgrant
pytest
```

## Pull requests

- keep changes scoped
- add or update tests
- keep public command behavior documented in `README.md`

