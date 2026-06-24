# AgentGrant CLI

AgentGrant CLI is a production-oriented Python command-line tool for working with the Grantex platform from the terminal. It covers documentation discovery, scope inspection, identity lookup, grant management, and JWT token inspection in a single CLI built with Click, `httpx`, Rich, and Pydantic Settings.

## Overview

The project is designed for developers, operators, and agent builders who need to inspect Grantex resources quickly without switching to a browser or writing one-off scripts.

Core capabilities:

- initialize and persist local CLI configuration
- store and use an API key for authenticated API requests
- fetch `llms.txt` and list documentation pages
- search across documentation pages
- open and print a specific documentation page
- list available scopes
- decode JWTs without verification
- verify JWTs with a configured or explicit secret
- fetch identity details
- list grants
- revoke a grant
- render either Rich terminal output or JSON output

## Tech Stack

- Python 3.12+
- Click
- httpx
- Rich
- Pydantic Settings
- PyJWT
- pytest
- Hatchling for packaging

## Project Structure

```text
agentgrant-cli/
├── agentgrant/
│   ├── cli.py
│   ├── __main__.py
│   ├── commands/
│   │   ├── docs.py
│   │   ├── grant.py
│   │   ├── identity.py
│   │   ├── scopes.py
│   │   └── token.py
│   ├── models/
│   │   └── docs.py
│   └── utils/
│       ├── config.py
│       ├── http_client.py
│       └── printer.py
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_docs.py
│   └── test_token.py
├── pyproject.toml
└── README.md
```

## Installation

Create a Python 3.12+ environment, then install the package and development dependencies.

```bash
pip install -e .[dev]
```

If you use `uv`, the equivalent setup is:

```bash
uv sync --extra dev
```

## Configuration

The CLI stores configuration at:

```text
~/.agentgrant/config.json
```

Default configuration fields:

- `api_base_url`
- `docs_base_url`
- `api_key`
- `jwt_secret`
- `jwt_algorithm`

Environment variables can override file-based configuration:

- `AGENTGRANT_API_BASE_URL`
- `AGENTGRANT_DOCS_BASE_URL`
- `AGENTGRANT_API_KEY`
- `AGENTGRANT_JWT_SECRET`
- `AGENTGRANT_JWT_ALGORITHM`

## Command Reference

### Initialize configuration

```bash
agentgrant init
```

Optional flags:

- `--api-base-url`
- `--docs-base-url`
- `--jwt-algorithm`

### Store an API key

```bash
agentgrant login --api-key YOUR_API_KEY
```

### List documentation pages from `llms.txt`

```bash
agentgrant docs
```

### Search documentation pages

```bash
agentgrant search delegation
agentgrant search scopes
```

### Print a documentation page

```bash
agentgrant page scopes
agentgrant page trust-registry
```

### List scopes

```bash
agentgrant scopes
```

### Decode a JWT

```bash
agentgrant token decode token.jwt
```

This command reads either a raw token string or a file path containing the token.

### Verify a JWT

```bash
agentgrant token verify token.jwt --secret YOUR_SECRET
```

If `--secret` is omitted, the CLI uses `AGENTGRANT_JWT_SECRET` or the stored config value.

### Fetch an identity

```bash
agentgrant identity get user123
```

### List grants

```bash
agentgrant grant list
```

### Revoke a grant

```bash
agentgrant grant revoke abc123
```

## JSON Output

Every command supports structured output through the global `--json-output` flag.

Example:

```bash
agentgrant --json-output scopes
```

## CLI Help

Click automatically provides help output for the root command and all subcommands.

Examples:

```bash
agentgrant --help
agentgrant token --help
agentgrant grant revoke --help
```

## Testing

Run the test suite with:

```bash
pytest
```

Current test coverage includes:

- CLI initialization behavior
- config persistence
- `llms.txt` parsing
- JWT decode and verification flows

## Design Notes

- HTTP calls use async `httpx` under a small client wrapper.
- Output formatting is centralized in a printer utility so commands can switch between Rich output and JSON easily.
- Settings merge persisted config with environment overrides.
- Documentation search works by fetching `llms.txt`, resolving page links, downloading page bodies, and ranking matches locally.

## API Path Assumptions

This CLI currently assumes the following API routes:

- `/scopes`
- `/identities/{identity_id}`
- `/grants`
- `/grants/{grant_id}`

If the Grantex API uses different routes or response shapes, adjust the command handlers in `agentgrant/commands/`.

## Status

The codebase is structured and ready for extension, but live validation against the real Grantex API depends on having:

- a working Python 3.12+ runtime
- installable dependencies
- valid Grantex API credentials
- confirmed production API and docs endpoints
