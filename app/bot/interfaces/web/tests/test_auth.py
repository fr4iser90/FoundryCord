import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.bot.interfaces.web.server import app
from app.bot.interfaces.web.models.user import User

client = TestClient(app)

@pytest.fixture
def mock_auth_service():
    with patch('interfaces.web.routes.auth.AuthService') as MockAuthService:
        auth_service_instance = MockAuthService.return_value
        auth_service_instance.get_oauth_url.return_value = "https://discord.com/api/oauth2/mock"
        auth_service_instance.exchange_code.return_value = {"access_token": "mock_token"}
        auth_service_instance.get_user_info.return_value = {
            "id": "123456789",
            "username": "test_user",
            "email": "test@example.com",
            "avatar": "avatar_hash"
        }
        auth_service_instance.generate_jwt.return_value = "mock_jwt_token"
        auth_service_instance.create_or_update_user = MagicMock()
        yield auth_service_instance

def test_login_redirect(mock_auth_service):
    response = client.get("/auth/login", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://discord.com/api/oauth2/mock"

def test_callback_success(mock_auth_service):
    response = client.get("/auth/callback?code=mock_code", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/dashboard"
    assert "auth_token" in response.cookies
    assert response.cookies["auth_token"] == "mock_jwt_token"

def test_callback_error():
    response = client.get("/auth/callback?error=access_denied", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/login?error=access_denied"

def test_callback_no_code():
    response = client.get("/auth/callback", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/login?error=no_code"

def test_logout():
    response = client.get("/auth/logout", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/"
    assert "auth_token" in response.cookies
    assert response.cookies["auth_token"] == "" 