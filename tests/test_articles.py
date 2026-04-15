from fastapi.testclient import TestClient

from tests.helpers import auth_headers, login_user, register_user


def test_create_article_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/articles",
        json={
            "title": "My article",
            "content": "Some content",
        },
    )

    assert response.status_code == 401


def test_create_article_success(client: TestClient) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    token = login_user(client, "user1@example.com", "strongpassword123")

    response = client.post(
        "/articles",
        headers=auth_headers(token),
        json={
            "title": "My first article",
            "content": "This is my first article.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first article"
    assert data["content"] == "This is my first article."
    assert data["author_id"] == 1


def test_list_articles_returns_list(client: TestClient) -> None:
    response = client.get("/articles")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_article_by_id_success(client: TestClient) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    token = login_user(client, "user1@example.com", "strongpassword123")

    create_response = client.post(
        "/articles",
        headers=auth_headers(token),
        json={
            "title": "Article title",
            "content": "Article content",
        },
    )
    article_id = create_response.json()["id"]

    response = client.get(f"/articles/{article_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Article title"


def test_get_article_returns_404_when_missing(client: TestClient) -> None:
    response = client.get("/articles/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"


def test_update_article_success_for_owner(client: TestClient) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    token = login_user(client, "user1@example.com", "strongpassword123")

    create_response = client.post(
        "/articles",
        headers=auth_headers(token),
        json={
            "title": "Old title",
            "content": "Old content",
        },
    )
    article_id = create_response.json()["id"]

    response = client.patch(
        f"/articles/{article_id}",
        headers=auth_headers(token),
        json={"title": "New title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["content"] == "Old content"


def test_update_article_returns_403_for_non_owner(client: TestClient) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    owner_token = login_user(client, "user1@example.com", "strongpassword123")

    register_user(client, "user2@example.com", "user2", "strongpassword123")
    other_token = login_user(client, "user2@example.com", "strongpassword123")

    create_response = client.post(
        "/articles",
        headers=auth_headers(owner_token),
        json={
            "title": "Owner article",
            "content": "Owner content",
        },
    )
    article_id = create_response.json()["id"]

    response = client.patch(
        f"/articles/{article_id}",
        headers=auth_headers(other_token),
        json={"title": "Hacked title"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to modify this article"


def test_delete_article_success_for_owner(client: TestClient) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    token = login_user(client, "user1@example.com", "strongpassword123")

    create_response = client.post(
        "/articles",
        headers=auth_headers(token),
        json={
            "title": "Delete me",
            "content": "Delete content",
        },
    )
    article_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/articles/{article_id}",
        headers=auth_headers(token),
    )
    assert delete_response.status_code == 204

    get_response = client.get(f"/articles/{article_id}")
    assert get_response.status_code == 404


def test_delete_article_returns_403_for_non_owner(client: TestClient) -> None:
    register_user(client, "user1@example.com", "user1", "strongpassword123")
    owner_token = login_user(client, "user1@example.com", "strongpassword123")

    register_user(client, "user2@example.com", "user2", "strongpassword123")
    other_token = login_user(client, "user2@example.com", "strongpassword123")

    create_response = client.post(
        "/articles",
        headers=auth_headers(owner_token),
        json={
            "title": "Owner article",
            "content": "Owner content",
        },
    )
    article_id = create_response.json()["id"]

    response = client.delete(
        f"/articles/{article_id}",
        headers=auth_headers(other_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to delete this article"