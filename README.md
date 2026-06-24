# AgentGrant CLI

AgentGrant CLI is a Python command-line tool for working with Grantex-style APIs from the terminal. It is built for inspecting documentation, scopes, identities, grants, and JWT tokens with a clean command surface, structured output, and a modular codebase.

## Highlights

- Click-based CLI with grouped subcommands
- Async HTTP clients built on `httpx`
- Rich terminal tables, panels, and JSON output
- Config management with Pydantic Settings
- JWT decode and verify flows with issuer and audience support
- Docs discovery from `llms.txt`
- Local docs caching
- Cache inspection and clearing
- Environment diagnostics via `doctor`
- Shell completion guidance
- Packaging and repo tooling for real project use

## Tech Stack

- Python 3.12+
- Click
- httpx
- Rich
- Pydantic
- Pydantic Settings
- PyJWT
- pytest
- Ruff
- Black
- mypy
- Hatchling

## Repository Structure

```text
agentgrant-cli/
|-- agentgrant/
|   |-- cli.py
|   |-- __main__.py
|   |-- commands/
|   |   |-- docs.py
|   |   |-- search.py
|   |   |-- page.py
|   |   |-- scopes.py
|   |   |-- identity.py
|   |   |-- grant.py
|   |   |-- token.py
|   |   |-- config.py
|   |   |-- cache.py
|   |   |-- doctor.py
|   |   |-- version.py
|   |   `-- completion.py
|   |-- core/
|   |   |-- settings.py
|   |   |-- exceptions.py
|   |   |-- constants.py
|   |   |-- logger.py
|   |   |-- cache_manager.py
|   |   |-- context.py
|   |   `-- session.py
|   |-- clients/
|   |   |-- api_client.py
|   |   |-- docs_client.py
|   |   `-- auth_client.py
|   |-- models/
|   |   |-- docs.py
|   |   |-- grant.py
|   |   |-- identity.py
|   |   |-- scope.py
|   |   `-- token.py
|   `-- utils/
|       |-- printer.py
|       |-- jwt_utils.py
|       |-- parser.py
|       |-- formatter.py
|       `-- validators.py
|-- tests/
|-- docs/
|-- examples/
|-- .github/workflows/
|-- pyproject.toml
|-- README.md
|-- LICENSE
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- .env.example
|-- .pre-commit-config.yaml
|-- Makefile
`-- mkdocs.yml
```

## Installation

### Using pip

```bash
pip install -e .[dev]
```

### Using uv

```bash
uv sync --extra dev
```

### Install as a tool

```bash
uv tool install .
```

## Configuration

The CLI stores config at:

```text
~/.agentgrant/config.json
```

Supported environment variables:

- `AGENTGRANT_API_BASE_URL`
- `AGENTGRANT_DOCS_BASE_URL`
- `AGENTGRANT_API_KEY`
- `AGENTGRANT_JWT_SECRET`
- `AGENTGRANT_JWT_ALGORITHM`

Environment variables override values stored in the config file.

## Quick Start

```bash
agentgrant init
agentgrant login --api-key YOUR_API_KEY
agentgrant docs
agentgrant search delegation
agentgrant scopes
agentgrant token decode token.jwt
```

## Examples

The repository includes small command examples in:

```text
examples/
```

Current example file:

```text
examples/docs.txt
```

## Commands

### Root help

```bash
agentgrant --help
```

### Configuration commands

```bash
agentgrant init
agentgrant login --api-key xxx
agentgrant logout
agentgrant whoami
agentgrant config show
agentgrant config set api_key xxx
agentgrant config reset
```

### Documentation commands

```bash
agentgrant docs
agentgrant search delegation
agentgrant search scopes
agentgrant page trust-registry
agentgrant page delegation
```

Docs support in the current codebase:

- `llms.txt` page discovery
- cached page fetches
- local ranking for search results
- fuzzy page resolution

### Scope commands

```bash
agentgrant scopes
agentgrant scopes --output json
agentgrant scopes --output yaml
agentgrant scopes --output csv
```

### Token commands

```bash
agentgrant token decode token.jwt
agentgrant token verify token.jwt --secret xxx
agentgrant token verify token.jwt --issuer issuer.example
agentgrant token verify token.jwt --audience my-audience
```

The token commands accept either:

- a raw JWT string
- a file path containing the token

### Identity commands

```bash
agentgrant identity get user123
agentgrant identity list
```

### Grant commands

```bash
agentgrant grant list
agentgrant grant list --page 1 --limit 20
agentgrant grant list --status active --user user123
agentgrant grant revoke abc123
```

### Cache commands

```bash
agentgrant cache info
agentgrant cache clear
```

### Doctor command

```bash
agentgrant doctor
```

This command checks:

- Python version
- config file presence
- cache directory presence
- API connectivity
- JWT secret configuration
- selected environment variables

### Version command

```bash
agentgrant version
```

### Completion command

```bash
agentgrant completion --shell bash
agentgrant completion --shell zsh
agentgrant completion --shell fish
agentgrant completion --shell powershell
```

## Global Flags

- `--json-output`
- `-v`
- `-vv`
- `--debug`
- `--no-cache`

## Output Formats

Default output is Rich-formatted terminal output.

Supported output styles in the current project:

- Rich tables and panels
- `--json-output`
- `--output table`
- `--output json`
- `--output yaml`
- `--output csv`

## Development

### Run tests

```bash
pytest
```

### Run linting

```bash
ruff check .
black --check .
mypy agentgrant
```

### Make targets

```bash
make install
make test
make lint
make format
make typecheck
```

## CI Workflows

The repository includes GitHub Actions workflows for:

- lint
- tests
- build
- release checks

Workflow files live in:

```text
.github/workflows/
```

## Current Verification

The project has been locally verified with:

- `ruff check .`
- `pytest`

At the moment, the test suite passes, but coverage is still below the original `>95%` target from the prompt. The current structure is production-oriented, but the test suite still needs to be expanded.

## Notes

The current implementation assumes Grantex-style endpoints such as:

- `/scopes`
- `/grants`
- `/grants/{grant_id}`
- `/identities`
- `/identities/{identity_id}`
- `/whoami`
- `/health`

If your backend uses different routes or response shapes, update the client modules under `agentgrant/clients/` and the command handlers under `agentgrant/commands/`.
