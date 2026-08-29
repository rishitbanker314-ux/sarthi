import pytest
import uuid
import jwt
import time
from unittest.mock import AsyncMock, patch
from jwt.exceptions import PyJWKClientError

from services.api.auth.verifier import verify_supabase_token, verify_local_token, Claims
from services.api.auth.jwks import AsyncRateLimitedJWKS, get_jwks_client
from services.api.auth.dependencies import get_current_user
from services.api.routers.dev_auth import dev_user_id
from services.api.errors import AppError
from services.api.config import Settings

# Dummy keys for testing
HS256_SECRET = "test-secret"
email = "demo@sarathi.app"
test_uuid = dev_user_id(email)

@pytest.fixture
def mock_settings():
    return Settings(
        dev_jwt_secret=HS256_SECRET,
        auth_mode="local",
        supabase_jwks_url="http://fake-jwks"
    )

def test_dev_user_id_deterministic():
    id1 = dev_user_id("test@example.com")
    id2 = dev_user_id("test@example.com")
    assert id1 == id2
    assert id1.version == 5

def test_verify_local_token_success(mock_settings):
    with patch("services.api.auth.verifier.get_settings", return_value=mock_settings):
        now = int(time.time())
        token = jwt.encode(
            {"sub": str(test_uuid), "email": email, "exp": now + 3600, "nbf": now},
            HS256_SECRET,
            algorithm="HS256"
        )
        claims = verify_local_token(token)
        assert claims.sub == test_uuid
        assert claims.email == email

def test_verify_local_token_expired(mock_settings):
    with patch("services.api.auth.verifier.get_settings", return_value=mock_settings):
        now = int(time.time())
        # Expired token (more than 60s leeway)
        token = jwt.encode(
            {"sub": str(test_uuid), "email": email, "exp": now - 100, "nbf": now - 200},
            HS256_SECRET,
            algorithm="HS256"
        )
        with pytest.raises(AppError) as exc_info:
            verify_local_token(token)
        assert exc_info.value.code == "TOKEN_EXPIRED"

@pytest.mark.asyncio
async def test_verify_supabase_token_missing_kid():
    token = jwt.encode({"sub": str(test_uuid), "exp": int(time.time()) + 3600}, "secret", algorithm="HS256")
    with pytest.raises(AppError) as exc_info:
        await verify_supabase_token(token)
    assert exc_info.value.code == "TOKEN_INVALID"

@pytest.mark.asyncio
async def test_jwks_rate_limiting():
    client = AsyncRateLimitedJWKS("http://fake")
    client.client.get = AsyncMock() # Mock the actual HTTP call
    client.client.get.side_effect = Exception("Should not hit network twice")
    
    # Fake setting last fetch to just now
    client.last_fetch = time.time()
    
    with pytest.raises(PyJWKClientError, match="rate limited"):
        await client.get_signing_key("some-kid")

@pytest.mark.asyncio
async def test_strict_algorithm_pinning():
    # If we pass an HS256 token to Supabase verifier, it will fail because it pins ES256
    token = jwt.encode(
        {"sub": str(test_uuid), "exp": int(time.time()) + 3600},
        "some-secret",
        algorithm="HS256",
        headers={"kid": "fake-kid"}
    )
    
    # We must mock get_jwks_client to return a fake ES256 key, but jwt.decode will reject it
    # because the token header says HS256 and the algorithms=["ES256"] argument blocks it.
    mock_jwks = AsyncMock()
    # Return any key object (just needs a .key attribute)
    class FakeKey:
        key = "fake-public-key"
    mock_jwks.get_signing_key.return_value = FakeKey()
    
    with patch("services.api.auth.verifier.get_jwks_client", return_value=mock_jwks):
        with pytest.raises(AppError) as exc_info:
            await verify_supabase_token(token)
        # It fails because algorithms=["ES256"] doesn't match the token's "alg": "HS256"
        assert exc_info.value.code == "TOKEN_INVALID"
