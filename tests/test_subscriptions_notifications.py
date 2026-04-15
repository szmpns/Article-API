from fastapi.testclient import TestClient

from tests.helpers import auth_headers, login_user, register_user


def test_subscribe_me_success(client: TestClient) -> None:
    register_user(client, "user2@example.com", "user2", "strongpassword123")
    token = login_user(client, "user2@example.com", "strongpassword123")

    response = client.post("/subscriptions/me", headers=auth_headers(token))

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 1


def test_subscribe_me_duplicate_returns_409(client: TestClient) -> None:
    register_user(client, "user2@example.com", "user2", "strongpassword123")
    token = login_user(client, "user2@example.com", "strongpassword123")

    first = client.post("/subscriptions/me", headers=auth_headers(token))
    second = client.post("/subscriptions/me", headers=auth_headers(token))

    assert first.status_code == 201
    assert second.status_code == 409


def test_unsubscribe_me_success(client: TestClient) -> None:
    register_user(client, "user2@example.com", "user2", "strongpassword123")
    token = login_user(client, "user2@example.com", "strongpassword123")

    client.post("/subscriptions/me", headers=auth_headers(token))
    response = client.delete("/subscriptions/me", headers=auth_headers(token))

    assert response.status_code == 204


def test_notification_created_for_subscriber_when_article_is_published(client: TestClient) -> None:
    register_user(client, "author@example.com", "author", "strongpassword123")
    author_token = login_user(client, "author@example.com", "strongpassword123")

    register_user(client, "subscriber@example.com", "subscriber", "strongpassword123")
    subscriber_token = login_user(client, "subscriber@example.com", "strongpassword123")

    subscribe_response = client.post(
        "/subscriptions/me",
        headers=auth_headers(subscriber_token),
    )
    assert subscribe_response.status_code == 201

    create_article_response = client.post(
        "/articles",
        headers=auth_headers(author_token),
        json={
            "title": "New article",
            "content": "Notification content",
        },
    )
    assert create_article_response.status_code == 201

    notifications_response = client.get(
        "/notifications/me",
        headers=auth_headers(subscriber_token),
    )

    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 1
    assert notifications[0]["message"] == "New article published: New article"


def test_no_new_notification_after_unsubscribe(client: TestClient) -> None:
    register_user(client, "author@example.com", "author", "strongpassword123")
    author_token = login_user(client, "author@example.com", "strongpassword123")

    register_user(client, "subscriber@example.com", "subscriber", "strongpassword123")
    subscriber_token = login_user(client, "subscriber@example.com", "strongpassword123")

    client.post("/subscriptions/me", headers=auth_headers(subscriber_token))
    client.delete("/subscriptions/me", headers=auth_headers(subscriber_token))

    create_article_response = client.post(
        "/articles",
        headers=auth_headers(author_token),
        json={
            "title": "Another article",
            "content": "Should not notify unsubscribed user",
        },
    )
    assert create_article_response.status_code == 201

    notifications_response = client.get(
        "/notifications/me",
        headers=auth_headers(subscriber_token),
    )

    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert notifications == []