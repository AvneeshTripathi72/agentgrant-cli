from __future__ import annotations

from pathlib import Path
from typing import Any

import jwt
from jwt import PyJWTError

from agentgrant.utils.config import PersistedConfig
from agentgrant.utils.printer import Printer


def _read_token(token_input: str) -> str:
    candidate = Path(token_input)
    if candidate.exists():
        return candidate.read_text(encoding="utf-8").strip()
    return token_input.strip()


def decode_token(token_input: str) -> dict[str, Any]:
    token = _read_token(token_input)
    try:
        header = jwt.get_unverified_header(token)
        claims = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    except PyJWTError as exc:
        raise ValueError(f"Unable to decode token: {exc}") from exc
    return {"header": header, "claims": claims}


def verify_token(token_input: str, settings: PersistedConfig, secret: str | None = None) -> dict[str, Any]:
    token = _read_token(token_input)
    signing_key = secret or settings.jwt_secret
    if not signing_key:
        raise ValueError("A JWT secret is required. Provide --secret or set AGENTGRANT_JWT_SECRET.")

    algorithm = settings.jwt_algorithm
    try:
        claims = jwt.decode(token, signing_key, algorithms=[algorithm])
    except PyJWTError as exc:
        raise ValueError(f"Token verification failed: {exc}") from exc
    return {"valid": True, "algorithm": algorithm, "claims": claims}


def render_decoded_token(printer: Printer, token_input: str) -> None:
    printer.emit(decode_token(token_input), title="Decoded JWT")


def render_verified_token(
    printer: Printer,
    token_input: str,
    settings: PersistedConfig,
    secret: str | None = None,
) -> None:
    printer.emit(verify_token(token_input, settings, secret=secret), title="Verified JWT")

