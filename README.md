# AgentGrant CLI

AgentGrant CLI is a production-oriented Python command-line interface for working with Grantex-style APIs, documentation, grants, identities, scopes, and JWT tokens.

## Features

- Click-based command tree with grouped subcommands
- async `httpx` clients for API and docs access
- Rich terminal output plus `json`, `yaml`, and `csv` output modes
- Pydantic Settings-backed configuration
- JWT decode and verification with issuer and audience support
- docs caching and local search ranking
- cache inspection and clearing
- doctor diagnostics
- shell completion instructions
- typed codebase with tests and packaging metadata

## Project Structure

```text
agentgrant-cli/
├── agentgrant/
│   ├── cli.py
│   ├── __main__.py
│   ├── commands/
│   ├── core/
│   ├── clients/
│   ├── models/
│   └── utils/
├── tests/
├── examples/
├── docs/
├── .github/workflows/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── Makefile
└── mkdocs.yml
```

## Installation

```bash
pip install -e .[dev]
```

With `uv`:

```bash
uv sync --extra dev
```

## Configuration

Configuration is stored at `~/.agentgrant/config.json`.

Environment variable overrides:

- `AGENTGRANT_API_BASE_URL`
- `AGENTGRANT_DOCS_BASE_URL`
- `AGENTGRANT_API_KEY`
- `AGENTGRANT_JWT_SECRET`
- `AGENTGRANT_JWT_ALGORITHM`

## Commands

### Configuration

```bash
agentgrant init
agentgrant login --api-key xxx
agentgrant logout
agentgrant whoami
agentgrant config show
agentgrant config set api_key xxx
agentgrant config reset
```

### Documentation

```bash
agentgrant docs
agentgrant search delegation
agentgrant page trust-registry
```

### Scopes

```bash
agentgrant scopes
agentgrant scopes --output json
agentgrant scopes --output yaml
agentgrant scopes --output csv
```

### Tokens

```bash
agentgrant token decode token.jwt
agentgrant token verify token.jwt --secret xxx
agentgrant token verify token.jwt --issuer issuer --audience audience
```

### Identities and Grants

```bash
agentgrant identity get user123
agentgrant identity list
agentgrant grant list --page 1 --limit 20 --status active --user user123
agentgrant grant revoke abc123
```

### Maintenance

```bash
agentgrant cache info
agentgrant cache clear
agentgrant doctor
agentgrant version
agentgrant completion --shell powershell
```

## Output Modes

- default Rich tables and panels
- `--json-output`
- per-command `--output json|yaml|csv|table` where supported

## Development

```bash
pytest
ruff check .
black --check .
mypy agentgrant
```

## Notes

The CLI currently assumes Grantex-compatible endpoints such as `/scopes`, `/grants`, `/identities`, `/whoami`, and `/health`. Update the client paths if your deployment uses different routes.

