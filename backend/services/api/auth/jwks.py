import time
import httpx
import jwt
from jwt import PyJWKSet
from jwt.exceptions import PyJWKClientError
import structlog

from services.api.config import get_settings

logger = structlog.get_logger()

class AsyncRateLimitedJWKS:
    def __init__(self, url: str):
        self.url = url
        self.jwks = None
        self.last_fetch = 0.0
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_signing_key(self, kid: str) -> jwt.PyJWK:
        # Check cache first
        if self.jwks:
            for key in self.jwks.keys:
                if key.key_id == kid:
                    return key

        # If not in cache, check rate limit
        now = time.time()
        if now - self.last_fetch < 60:
            logger.warning("JWKS refresh rate limited", kid=kid)
            raise PyJWKClientError("JWKS refresh rate limited")

        logger.info("Fetching JWKS", url=self.url)
        self.last_fetch = now
        
        try:
            resp = await self.client.get(self.url)
            resp.raise_for_status()
        except httpx.RequestError as e:
            logger.error("Failed to fetch JWKS", error=str(e))
            raise PyJWKClientError("Failed to fetch JWKS") from e
            
        self.jwks = PyJWKSet.from_dict(resp.json())

        # Check again
        for key in self.jwks.keys:
            if key.key_id == kid:
                return key

        raise PyJWKClientError(f"Unable to find a signing key that matches: '{kid}'")

_jwks_client = None

def get_jwks_client() -> AsyncRateLimitedJWKS:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = AsyncRateLimitedJWKS(get_settings().supabase_jwks_url)
    return _jwks_client
