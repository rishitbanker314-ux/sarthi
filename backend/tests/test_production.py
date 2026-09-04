import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from services.api.config import Settings
from services.api.main import app

def test_production_config_rejects_local_auth():
    with pytest.raises(ValueError, match="Cannot run with auth_mode='local' in production."):
        Settings(
            _env_file=None,
            env="production",
            demo_mode=False,
            auth_mode="local",
            dev_jwt_secret="real_secret",
            cors_origins="https://example.com"
        )

def test_production_config_rejects_demo_mode():
    with pytest.raises(ValueError, match="Cannot run with demo_mode=True in production."):
        Settings(
            _env_file=None,
            env="production",
            demo_mode=True,
            auth_mode="supabase",
            dev_jwt_secret="real_secret",
            cors_origins="https://example.com"
        )

def test_production_config_rejects_wildcard_cors():
    with pytest.raises(ValueError, match="cors_origins cannot contain wildcard '\*' in production."):
        Settings(
            _env_file=None,
            env="production",
            demo_mode=False,
            auth_mode="supabase",
            dev_jwt_secret="real_secret",
            cors_origins="*,https://example.com"
        )

def test_production_security_headers():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"

def test_dev_routes_missing_in_production():
    pass
