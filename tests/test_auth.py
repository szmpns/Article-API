from fastapi.testclient import TestClient

from tests.helpers import auth_headers, login_user, register_user


def test_healthcheck(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_user_success(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["is_active"] is True
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_user_returns_409(client: TestClient) -> None:
    register_user(client, "test@example.com", "testuser", "strongpassword123")

    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 409


def test_register_validation_error(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "username": "ab",
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_login_success_returns_token(client: TestClient) -> None:
    register_user(client, "test@example.com", "testuser", "strongpassword123")

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password_returns_401(client: TestClient) -> None:
    register_user(client, "test@example.com", "testuser", "strongpassword123")

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_auth_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_returns_current_user(client: TestClient) -> None:
    register_user(client, "test@example.com", "testuser", "strongpassword123")
    token = login_user(client, "test@example.com", "strongpassword123")

    response = client.get("/auth/me", headers=auth_headers(token))

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"