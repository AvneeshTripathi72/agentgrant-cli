from __future__ import annotations

from pathlib import Path
from typing import Any

import jwt
from jwt import PyJWTError

from agentgrant.core.exceptions import TokenError
from agentgrant.models.token import TokenPayload


def read_token(token_input: str) -> str:
    path = Path(token_input)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return token_input.strip()


def decode_token(token_input: str) -> TokenPayload:
    token = read_token(token_input)
    try:
        header = jwt.get_unverified_header(token)
        claims = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    except PyJWTError as exc:
        raise TokenError(f"Unable to decode token: {exc}") from exc
    return TokenPayload(header=header, claims=claims)


def verify_token(
    token_input: str,
    secret: str,
    algorithm: str,
    issuer: str | None = None,
    audience: str | None = None,
) -> TokenPayload:
    token = read_token(token_input)
    options: dict[str, Any] = {"verify_signature": True, "verify_exp": True}
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            issuer=issuer,
            audience=audience,
            options=options,
        )
        header = jwt.get_unverified_header(token)
    except PyJWTError as exc:
        raise TokenError(f"Token verification failed: {exc}") from exc
    return TokenPayload(header=header, claims=claims, valid=True, algorithm=algorithm)
