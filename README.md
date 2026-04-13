# Article-API

Simple REST API for managing articles and users.

It provides article management, user authentication, subscriptions for newly created content, notifications, and bulk import of articles from an external source.

---

## Features

* User registration
* User authentication with JWT
* Current user endpoint
* Create, list, retrieve, update, and delete articles
* Article ownership protection
* Subscribe to updates about newly created articles
* Notifications for subscribed users
* Bulk import of articles from an external JSON source
* PostgreSQL persistence
* Docker-based setup

---

## Tech stack

* Python 3.11
* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic
* JWT authentication
* Docker / Docker Compose

---

## Project structure

```
app/
├── api/
│   └── routes/
│       ├── articles.py
│       ├── auth.py
│       ├── imports.py
│       ├── notifications.py
│       └── subscriptions.py
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
├── models/
│   ├── article.py
│   ├── notification.py
│   ├── subscription.py
│   └── users.py
├── schemas/
│   ├── article.py
│   ├── auth.py
│   ├── import_data.py
│   ├── notification.py
│   ├── subscription.py
│   └── user.py
└── main.py
```

---

## Requirements

* Docker
* Docker Compose

---

## Run locally

Clone the repository:

```
git clone https://github.com/szmpns/Article-API.git
cd Article-API
```

Start the application:

```
docker compose up --build
```

The API will be available at:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

## Environment configuration

The application can run even with an empty `.env` file because default values are defined in the settings class.

Example `.env`:

```
APP_NAME=Article API
DEBUG=true

DB_HOST=db
DB_PORT=5432
DB_NAME=article_api
DB_USER=postgres
DB_PASSWORD=postgres

SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## Authentication

Authentication uses **JWT bearer tokens**.

### Register

`POST /auth/register`

Example request body:

```
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "strongpassword123"
}
```

### Login

`POST /auth/login`

Example request body:

```
{
  "email": "test@example.com",
  "password": "strongpassword123"
}
```

### Current user

`GET /auth/me`

Requires header:

```
Authorization: Bearer <access_token>
```

---

## Main endpoints

### Auth

```
POST /auth/register
POST /auth/login
GET /auth/me
```

### Articles

```
POST /articles
GET /articles
GET /articles/{article_id}
PATCH /articles/{article_id}
DELETE /articles/{article_id}
```

### Subscriptions

```
POST /subscriptions/me
DELETE /subscriptions/me
```

### Notifications

```
GET /notifications/me
```

### Import

```
POST /articles/import
```

---

## Bulk import

The import endpoint expects a JSON object:

```
{
  "source_url": "http://host.docker.internal:9000/sample_articles.json"
}
```

The external source must return a JSON array in this format:

```
[
  {
    "title": "Imported article 1",
    "content": "Content from external source 1"
  },
  {
    "title": "Imported article 2",
    "content": "Content from external source 2"
  }
]
```

Example response:

```
{
  "imported_count": 2,
  "skipped_count": 1,
  "total_received": 3
}
```

---

## Assumptions

To keep the solution simple, the following assumptions were made:

* subscriptions are **global**, not author-specific
* a subscribed user receives notifications about **every newly created article**
* article import is performed by an **authenticated user**
* imported articles are assigned to the user who triggers the import
* duplicate imported articles are skipped based on `title + content + author_id`
* HTTPS is expected to be handled in production by a **reverse proxy**

---

## Notes about Docker and import

For local testing of imports from files served on the host machine, Docker uses:

```
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This allows containers to access services running on the host machine.

---

## Security notes

* passwords are stored as **hashed values**
* JWT is used for authenticated endpoints
* article update and deletion are restricted to the **article owner**
* protected endpoints return appropriate status codes (`401`, `403`, `404`, `409`)

---

## Example workflow

1. Register the first user
2. Log in as the first user and obtain a JWT token
3. Register the second user
4. Log in as the second user and obtain a JWT token
5. Subscribe the second user to article updates
6. Create an article as the first user
7. Check notifications for the second user
8. Import articles from an external JSON source

---

## Possible future improvements

* proper database migrations instead of creating tables at startup
* unified error response schema
* marking notifications as read
* author-specific subscriptions
* automated tests with a dedicated test database
* CI pipeline with linting and tests