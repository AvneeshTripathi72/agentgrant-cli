import jwt
import pytest

from agentgrant.commands.token import decode_token, verify_token
from agentgrant.utils.config import PersistedConfig


def test_decode_token_returns_header_and_claims() -> None:
    token = jwt.encode({"sub": "user123"}, "secret", algorithm="HS256")
    decoded = decode_token(token)

    assert decoded["claims"]["sub"] == "user123"
    assert decoded["header"]["alg"] == "HS256"


def test_verify_token_requires_secret() -> None:
    token = jwt.encode({"sub": "user123"}, "secret", algorithm="HS256")

    with pytest.raises(ValueError):
        verify_token(token, PersistedConfig())


def test_verify_token_validates_signature() -> None:
    token = jwt.encode({"sub": "user123"}, "secret", algorithm="HS256")
    verified = verify_token(token, PersistedConfig(jwt_secret="secret"))

    assert verified["valid"] is True
    assert verified["claims"]["sub"] == "user123"

