from __future__ import annotations

import click

from agentgrant.core.context import AppContext, pass_context
from agentgrant.core.exceptions import ConfigurationError
from agentgrant.utils.jwt_utils import decode_token, verify_token


@click.group("token")
def token_group() -> None:
    """Token operations."""


@token_group.command("decode")
@click.argument("token_input")
@pass_context
def token_decode(app: AppContext, token_input: str) -> None:
    """Decode a JWT without signature verification."""
    payload = decode_token(token_input)
    app.printer.emit(payload.model_dump(mode="json"), title="Decoded JWT")


@token_group.command("verify")
@click.argument("token_input")
@click.option("--secret", default=None, help="JWT secret override.")
@click.option("--issuer", default=None, help="Expected token issuer.")
@click.option("--audience", default=None, help="Expected token audience.")
@pass_context
def token_verify(
    app: AppContext,
    token_input: str,
    secret: str | None,
    issuer: str | None,
    audience: str | None,
) -> None:
    """Verify a JWT."""
    signing_secret = secret or app.settings.jwt_secret
    if not signing_secret:
        raise ConfigurationError(
            "A JWT secret is required. Use --secret or configure AGENTGRANT_JWT_SECRET."
        )
    payload = verify_token(
        token_input,
        secret=signing_secret,
        algorithm=app.settings.jwt_algorithm,
        issuer=issuer,
        audience=audience,
    )
    app.printer.emit(payload.model_dump(mode="json"), title="Verified JWT")
