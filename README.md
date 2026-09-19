# Blogging Platform API

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)
![SQLite](https://img.shields.io/badge/database-SQLite-003B57)
![uv](https://img.shields.io/badge/packaging-uv-de5fe9)
![pytest](https://img.shields.io/badge/tests-pytest-0a9edc)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A **FastAPI** RESTful blogging platform API themed after Clancy's letters from
Dema (*Twenty One Pilots* lore) — create, publish, update, delete, and search
letters with categories, normalized tags, and UTC timestamps. Built with
Hexagonal Architecture (Ports and Adapters), SQLAlchemy 2.0 async, and SQLite.

## Table of contents

- [Features](#features)
- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [API](#api)
- [Configuration](#configuration)
- [Development](#development)
- [Project structure](#project-structure)
- [Design notes](#design-notes)
- [Project origin](#project-origin)

---

## Features

- **Full CRUD operations**: create, read, update, and delete letters with strict
  schema validation (`extra="forbid"`, automatic whitespace stripping).
- **Full-text search**: filter letters using `?term=` across `title`, `content`,
  and `category` (case-insensitive, wildcards `%` and `_` safely escaped).
- **Tag normalization**: case-insensitive tag deduplication while preserving the
  author's original casing for presentation and maintaining order of appearance.
- **Hexagonal Architecture (Ports & Adapters)**: pure domain models decoupled
  from the persistence backend and HTTP framework.
- **Dual repository adapters**: an async SQLite adapter (via SQLAlchemy 2.0 and
  `aiosqlite`) alongside an in-memory fake repository, both tested against the
  exact same repository contract suite.
- **Deterministic testing**: time is passed explicitly into repositories via a
  pluggable `Clock` abstraction, allowing tests to advance time without `sleep`.
- **Database seeder**: built-in command (`make seed` / `blog-seed`) to populate
  the database with canonical letters from Clancy's escape from Dema.
- **Consistent JSON serialization**: response models use camelCase
  (`createdAt`, `updatedAt`) formatted as ISO 8601 UTC with `Z` suffix.
- **Standardized error envelopes**: unified error payload shape for validation
  failures (`400 Bad Request`) and missing entities (`404 Not Found`).

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/carvalhocaio/blogging-platform-api.git
cd blogging-platform-api
```

### 2. Install dependencies and git hooks

```bash
make sync
make hooks
```

### 3. Seed the database (optional)

Populate `dema.db` with Clancy's initial letters:

```bash
make seed
# 5 letters seeded
```

### 4. Run the development server

```bash
make run
```

The API starts at `http://127.0.0.1:8000`.

- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc documentation: `http://127.0.0.1:8000/redoc`

---

## API

| Method | Path | Status | Description |
|---|---|---|---|
| `POST` | `/posts` | `201 Created` | Create a new letter |
| `GET` | `/posts` | `200 OK` | List all letters, optionally filtered by `?term=` |
| `GET` | `/posts/{id}` | `200 OK` | Retrieve a single letter by ID |
| `PUT` | `/posts/{id}` | `200 OK` | Replace an existing letter |
| `DELETE` | `/posts/{id}` | `204 No Content` | Delete a letter by ID |

### Endpoints and Examples

#### Create a letter

```bash
curl -X POST "http://127.0.0.1:8000/posts" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dear Clancy",
    "content": "The bishops are watching the wall.",
    "category": "Letters",
    "tags": ["Trench", "Dema"]
  }'
```

```json
{
  "id": 1,
  "title": "Dear Clancy",
  "content": "The bishops are watching the wall.",
  "category": "Letters",
  "tags": [
    "Trench",
    "Dema"
  ],
  "createdAt": "2026-09-18T12:00:00Z",
  "updatedAt": "2026-09-18T12:00:00Z"
}
```

#### List letters (with optional search)

```bash
# List all letters
curl "http://127.0.0.1:8000/posts"

# Filter by term (searches title, content, and category)
curl "http://127.0.0.1:8000/posts?term=bishops"
```

```json
[
  {
    "id": 1,
    "title": "Dear Clancy",
    "content": "The bishops are watching the wall.",
    "category": "Letters",
    "tags": [
      "Trench",
      "Dema"
    ],
    "createdAt": "2026-09-18T12:00:00Z",
    "updatedAt": "2026-09-18T12:00:00Z"
  }
]
```

#### Get a letter by ID

```bash
curl "http://127.0.0.1:8000/posts/1"
```

#### Update a letter

```bash
curl -X PUT "http://127.0.0.1:8000/posts/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Dear Clancy (Updated)",
    "content": "The bishops have left the east tower.",
    "category": "Letters",
    "tags": ["Trench", "Escape"]
  }'
```

```json
{
  "id": 1,
  "title": "Dear Clancy (Updated)",
  "content": "The bishops have left the east tower.",
  "category": "Letters",
  "tags": [
    "Trench",
    "Escape"
  ],
  "createdAt": "2026-09-18T12:00:00Z",
  "updatedAt": "2026-09-18T12:30:00Z"
}
```

#### Delete a letter

```bash
curl -i -X DELETE "http://127.0.0.1:8000/posts/1"
# HTTP/1.1 204 No Content
```

### Error Responses

#### Validation Error (`400 Bad Request`)

When request payloads fail validation or contain unknown fields:

```json
{
  "message": "validation failed",
  "errors": [
    {
      "field": "title",
      "message": "String should have at least 1 character"
    }
  ]
}
```

#### Not Found (`404 Not Found`)

When accessing, updating, or deleting a non-existent post:

```json
{
  "message": "post 404 not found",
  "errors": []
}
```

---

## Configuration

Settings are loaded via `pydantic-settings` from environment variables prefixed
with `BLOG_` or from an optional `.env` file.

| Variable | Default | Description |
|---|---|---|
| `BLOG_DATABASE_URL` | `sqlite+aiosqlite:///dema.db` | Async SQLAlchemy database connection URL |
| `BLOG_ECHO_SQL` | `false` | Echo executed SQL queries to logging output |

---

## Development

All standard development tasks are orchestrated through the `Makefile`:

```bash
make help          # List all available Makefile targets
make sync          # Install runtime and dev dependencies using uv
make run           # Start the development server with live reload
make seed          # Populate the database with Clancy's letters
make test          # Run the test suite with pytest
make lint          # Check code with ruff
make lint-fix      # Automatically fix safe linting violations with ruff
make format        # Format code with ruff
make format-check  # Verify formatting with ruff without modifying files
make audit         # Audit dependencies for vulnerabilities with pip-audit
make check         # Run full verification suite locally (lint, format, audit, test)
make hooks         # Install pre-commit git hooks
make hooks-run     # Run all pre-commit hooks over all files
make clean         # Remove caches and build artifacts
```

---

## Project structure

```
src/blogging_platform_api/
├── config.py                          # Settings loaded from BLOG_* environment variables
├── main.py                            # FastAPI app factory, lifespan, and engine management
├── domain/                            # Pure core models and repository interface
│   ├── errors.py                      # Domain exception hierarchy (PostNotFoundError)
│   ├── models.py                      # Post, PostDraft, and tag normalization logic
│   └── repository.py                  # PostRepository Protocol (the port)
├── application/                       # Application use cases and business orchestration
│   ├── clock.py                       # Clock Protocol and SystemClock implementation
│   └── posts.py                       # PostService coordinating repository and clock
├── infrastructure/                    # External adapters and persistence layer
│   ├── seed.py                        # Database seeder with Clancy's canonical letters
│   └── persistence/
│       ├── database.py                # Async engine, sessionmaker, and schema migration
│       ├── memory.py                  # InMemoryPostRepository (test fake adapter)
│       ├── models.py                  # SQLAlchemy ORM mapped entities (PostRow, TagRow, PostTagRow)
│       └── sqlite.py                  # SQLitePostRepository (async SQLAlchemy adapter)
└── web/                               # HTTP transport layer (FastAPI)
    ├── dependencies.py                # Request-scoped dependency injection
    ├── handlers.py                    # Centralized error handlers for 400 and 404
    ├── routes.py                      # /posts router endpoint definitions
    └── schemas.py                     # Pydantic schemas with camelCase serialization
```

---

## Design notes

### Architecture & Dependency Inversion

Dependencies strictly point inward: `web → application → domain`, and `domain`
has zero external framework dependencies:

- **Domain**: Pure Python dataclasses (`Post`, `PostDraft`) and the
  `PostRepository` protocol defining storage capabilities.
- **Application**: `PostService` orchestrates use cases without knowing how or
  where data is stored.
- **Infrastructure**: Adapters implement the `PostRepository` contract.
- **Web**: FastAPI handlers parse payloads, invoke `PostService`, and serialize
  responses into the external HTTP contract.

### Contract Testing

The repository contract in `tests/test_post_repository_contract.py` runs identical
assertions against both `InMemoryPostRepository` and `SQLitePostRepository`.
This guarantees that the in-memory fake used for fast unit tests behaves
identically to the production SQLite database adapter.

### Time & Determinism

Timestamps (`created_at` and `updated_at`) are never read from `datetime.now()`
inside repository layers. Instead, `PostService` receives an injectable `Clock`
protocol. In tests, `FrozenClock` controls time advances explicitly, allowing
robust verification that `created_at` remains unchanged while `updated_at`
advances when replacing a post.

### Relational Schema & Normalized Tags

- Tags are stored in a normalized many-to-many relationship (`tags`, `post_tags`,
  `posts`).
- `post_tags` maintains a `position` column to preserve the original tag ordering
  specified in the request.
- SQLite foreign key enforcement is enabled on connection via `PRAGMA foreign_keys=ON`.
- Tags are indexed by `slug` (case-folded) with a unique constraint, preventing
  duplicate tags across posts.

### Search Implementation

Search via `?term=` queries `title`, `content`, and `category`. In SQLite, SQL
wildcard characters (`%` and `_`) and the escape character (`\`) are safely
escaped before evaluation, preventing pattern injection and ensuring literal
substring matches.

### Twenty One Pilots Lore

The API's data model and default database (`dema.db`) are themed after the
conceptual lore of *Twenty One Pilots* (*Trench* / *Clancy*). The seed command
populates letters authored by Clancy detailing life inside the walled city of
Dema, the nine bishops, and the Bandito rebellion.

---

## Project origin

Built as an implementation of the
[Blogging Platform API](https://roadmap.sh/projects/blogging-platform-api)
project from [roadmap.sh](https://roadmap.sh).
