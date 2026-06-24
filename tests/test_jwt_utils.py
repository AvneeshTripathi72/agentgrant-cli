import jwt
import pytest

from agentgrant.core.exceptions import TokenError
from agentgrant.utils.jwt_utils import decode_token, verify_token


def test_decode_token_returns_claims() -> None:
    token = jwt.encode({"sub": "user123"}, "x" * 32, algorithm="HS256")
    payload = decode_token(token)

    assert payload.claims["sub"] == "user123"
    assert payload.header["alg"] == "HS256"


def test_verify_token_fails_on_wrong_secret() -> None:
    token = jwt.encode({"sub": "user123"}, "x" * 32, algorithm="HS256")

    with pytest.raises(TokenError):
        verify_token(token, secret="y" * 32, algorithm="HS256")


def test_decode_and_verify_token_from_file(tmp_path) -> None:
    token = jwt.encode({"sub": "user123"}, "x" * 32, algorithm="HS256")
    token_path = tmp_path / "token.jwt"
    token_path.write_text(token, encoding="utf-8")

    decoded = decode_token(str(token_path))
    verified = verify_token(str(token_path), secret="x" * 32, algorithm="HS256")

    assert decoded.claims["sub"] == "user123"
    assert verified.valid is True
