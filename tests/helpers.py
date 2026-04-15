from fastapi.testclient import TestClient


def register_user(
    client: TestClient,
    email: str,
    username: str,
    password: str,
) -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(
    client: TestClient,
    email: str,
    password: str,
) -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}