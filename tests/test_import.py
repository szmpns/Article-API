from fastapi.testclient import TestClient

import app.api.routes.articles as articles_module
from tests.helpers import auth_headers, login_user, register_user


class MockResponse:
    def __init__(self, payload: list[dict]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> list[dict]:
        return self._payload


def test_import_articles_success(client: TestClient, monkeypatch) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    token = login_user(client, "user1@example.com", "strongpassword123")

    payload = [
        {
            "title": "Imported article 1",
            "content": "Imported content 1",
        },
        {
            "title": "Imported article 2",
            "content": "Imported content 2",
        },
        {
            "title": "x",
            "content": "Too short title",
        },
    ]

    def mock_get(*args, **kwargs):
        return MockResponse(payload)

    monkeypatch.setattr(articles_module.httpx, "get", mock_get)

    response = client.post(
        "/articles/import",
        headers=auth_headers(token),
        json={"source_url": "http://example.com/articles.json"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 2
    assert data["skipped_count"] == 1
    assert data["total_received"] == 3


def test_import_articles_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/articles/import",
        json={"source_url": "http://example.com/articles.json"},
    )

    assert response.status_code == 401