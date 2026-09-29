# EVE Healthcare — Diagnostic Test Booking API

> **SDE Backend Assignment** — Flask · PostgreSQL · SQLAlchemy · JWT · Redis · Celery · pytest

A production-style REST API for booking diagnostic tests with simulated payments, idempotent webhooks, Redis caching, and Celery-powered email confirmation.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [How to Run Locally](#2-how-to-run-locally)
3. [API Endpoints & Example Requests](#3-api-endpoints--example-requests)
4. [Database & Schema Design](#4-database--schema-design)
5. [Important Assumptions](#5-important-assumptions)
6. [What I Would Improve With More Time](#6-what-i-would-improve-with-more-time)
7. [Architecture](#7-architecture)
8. [Tests](#8-tests)

---

## 1. Project Overview

A patient can:

1. **Register / Log in** — JWT-based auth (no refresh tokens in this scope)
2. **Browse** diagnostic centres and their tests
3. **Book a test** — server pulls price from the DB; client cannot override it
4. **Pay** through a simulated payment endpoint (SUCCESS · FAILED · RANDOM)
5. **Receive a confirmation email** — sent by a Celery worker after a successful payment
6. **Trigger a webhook** — idempotent payment-provider callback updates booking status
7. **Own their data** — users can only see and cancel their own bookings

No Docker. No MongoDB. No Stripe/Razorpay. No real payment gateway.

---

## 2. How to Run Locally

### Prerequisites

| Service    | Version   | Notes                        |
|------------|-----------|------------------------------|
| Python     | 3.11+     |                              |
| PostgreSQL | 15+       | Running on port 5432         |
| Redis      | 7+        | Running on port 6379         |

On Windows, start PostgreSQL and Redis as services (or via pgAdmin / Redis installer).

---

### Step 1 — Clone & create virtual environment

```powershell
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Step 2 — Configure environment

```powershell
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env` and fill in your values:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/diagnostic_booking
JWT_SECRET_KEY=a-long-random-secret

# Email (Gmail example — use an App Password if 2FA is enabled)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Set true to suppress real emails during development
MAIL_SUPPRESS_SEND=false
```

---

### Step 3 — Create databases

```sql
-- Run in psql or pgAdmin
CREATE DATABASE diagnostic_booking;
```

---

### Step 4 — Apply migrations & seed data

```powershell
# Windows
$env:FLASK_APP = "run.py"
.venv\Scripts\flask db upgrade
.venv\Scripts\python seed.py
```

```bash
# macOS/Linux
export FLASK_APP=run.py
flask db upgrade
python seed.py
```

---

### Step 5 — Start all services (3 terminals)

**Terminal 1 — Flask API**

```powershell
.venv\Scripts\python run.py
```

→ API available at `http://localhost:5000`  
→ Swagger UI at `http://localhost:5000/api/docs`

**Terminal 2 — Celery worker** (sends booking confirmation emails)

```powershell
# Windows
.venv\Scripts\celery -A celery_app.celery worker --loglevel=INFO --pool=solo

# macOS/Linux
celery -A celery_app.celery worker --loglevel=INFO
```

**Terminal 3 — Redis** (if not running as a service)

```powershell
redis-server
```

---

## 3. API Endpoints & Example Requests

All responses use a consistent envelope:

```json
{ "success": true, "data": { ... } }
{ "success": false, "error": { "code": "BOOKING_NOT_FOUND", "message": "..." } }
```

Protected routes require `Authorization: Bearer <jwt>`.

---

### Auth

#### `POST /api/auth/signup`

```json
// Request
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "Password1"
}

// 201 Response
{
  "success": true,
  "data": { "id": 1, "name": "Alice", "email": "alice@example.com", "created_at": "2025-10-01T10:00:00" }
}
```

#### `POST /api/auth/login`

```json
// Request
{ "email": "alice@example.com", "password": "Password1" }

// 200 Response
{
  "success": true,
  "data": {
    "access_token": "eyJhbGci...",
    "user": { "id": 1, "name": "Alice", "email": "alice@example.com" }
  }
}
```

#### `GET /api/auth/me` *(JWT required)*

```json
// 200 Response
{ "success": true, "data": { "id": 1, "name": "Alice", "email": "alice@example.com" } }
```

---

### Diagnostic Centres

#### `GET /api/centres?page=1&per_page=10`

```json
// 200 Response (results cached in Redis)
{
  "success": true,
  "data": [
    { "id": 1, "name": "EVE Koramangala", "location": "Bengaluru" }
  ],
  "meta": { "page": 1, "per_page": 10, "total": 3 }
}
```

#### `GET /api/centres/<id>`

```json
// 200 Response
{
  "success": true,
  "data": {
    "id": 1,
    "name": "EVE Koramangala",
    "location": "Bengaluru",
    "tests": [
      { "id": 1, "name": "CBC", "description": "Complete blood count", "price": "499.00" }
    ]
  }
}
```

#### `GET /api/centres/<id>/tests`

```json
// 200 Response (results cached in Redis)
{
  "success": true,
  "data": [
    { "id": 1, "name": "CBC", "description": "Complete blood count", "price": "499.00" }
  ]
}
```

#### `GET /api/tests/<id>`

```json
// 200 Response
{
  "success": true,
  "data": { "id": 1, "name": "CBC", "price": "499.00", "centre_id": 1 }
}
```

---

### Bookings *(JWT required)*

#### `POST /api/bookings`

```json
// Request
{
  "test_id": 1,
  "centre_id": 1,
  "appointment_datetime": "2025-10-15T09:00:00"
}

// 201 Response
{
  "success": true,
  "data": {
    "id": 1,
    "test_id": 1,
    "centre_id": 1,
    "appointment_datetime": "2025-10-15T09:00:00",
    "amount": "499.00",
    "status": "PENDING",
    "created_at": "2025-10-01T10:05:00"
  }
}
```

> `amount` is **always taken from the test price** in the database. Client-supplied amounts are ignored.

#### `GET /api/bookings`

```json
// 200 Response — only the authenticated user's bookings
{
  "success": true,
  "data": [ { "id": 1, "status": "PENDING", "amount": "499.00", ... } ]
}
```

#### `GET /api/bookings/<id>`

```json
// 200 Response
{ "success": true, "data": { "id": 1, "status": "CONFIRMED", ... } }

// 404 if booking belongs to another user (no 403 leak)
```

#### `POST /api/bookings/<id>/cancel`

```json
// 200 Response
{ "success": true, "data": { "id": 1, "status": "CANCELLED", ... } }

// 409 if booking is already CONFIRMED, FAILED, or CANCELLED
```

---

### Payments *(JWT required)*

#### `POST /api/payments/`

```json
// Request
{
  "booking_id": 1,
  "simulate_result": "SUCCESS"   // optional: SUCCESS | FAILED (default from env)
}

// 201 Response
{
  "success": true,
  "data": {
    "id": 1,
    "booking_id": 1,
    "external_payment_id": "pay_a3f91bc...",
    "amount": "499.00",
    "status": "SUCCESS"
  }
}
```

> On SUCCESS: booking status → `CONFIRMED`, Celery enqueues a confirmation email.  
> On FAILED: booking status → `FAILED`. A retry payment is allowed.  
> Duplicate SUCCESS payment → **409 CONFLICT**.

---

### Webhook *(no auth — simulated provider callback)*

#### `POST /api/payments/webhook/`

```json
// Request
{
  "event_id": "evt_abc123",
  "payment_id": "pay_a3f91bc...",
  "status": "SUCCESS"
}

// 200 Response — first delivery
{
  "success": true,
  "data": {
    "already_processed": false,
    "event_id": "evt_abc123",
    "payment": { ... },
    "booking_status": "CONFIRMED",
    "processed": true
  }
}

// 200 Response — duplicate delivery (idempotent)
{
  "success": true,
  "data": {
    "already_processed": true,
    "event_id": "evt_abc123",
    "processed": true
  }
}
```

---

### Error Responses

| HTTP | `code`                    | When                                  |
|------|---------------------------|---------------------------------------|
| 400  | `BAD_REQUEST`             | Missing/invalid JSON                  |
| 401  | `UNAUTHORIZED`            | Missing or invalid JWT                |
| 401  | `TOKEN_EXPIRED`           | Expired JWT                           |
| 404  | `NOT_FOUND`               | Resource does not exist               |
| 409  | `PAYMENT_ALREADY_SUCCEEDED` | Duplicate payment for same booking  |
| 409  | `BOOKING_ALREADY_CANCELLED` | Cancel already-cancelled booking    |
| 422  | `VALIDATION_ERROR`        | Schema validation failure             |

---

## 4. Database & Schema Design

### Entity-Relationship Overview

```
users
  └── bookings (user_id FK)
        └── payments (booking_id FK)
        └── webhook_events (via external_payment_id)

diagnostic_centres
  └── diagnostic_tests (centre_id FK)
        └── bookings (test_id FK, centre_id FK)
```

### Tables

#### `users`
| Column          | Type          | Notes                         |
|-----------------|---------------|-------------------------------|
| id              | SERIAL PK     |                               |
| name            | VARCHAR(120)  | NOT NULL                      |
| email           | VARCHAR(255)  | UNIQUE, indexed               |
| password_hash   | VARCHAR(255)  | bcrypt via Werkzeug           |
| created_at      | TIMESTAMPTZ   | auto                          |
| updated_at      | TIMESTAMPTZ   | auto                          |

#### `diagnostic_centres`
| Column    | Type         | Notes |
|-----------|--------------|-------|
| id        | SERIAL PK    |       |
| name      | VARCHAR(200) |       |
| location  | VARCHAR(200) |       |

#### `diagnostic_tests`
| Column      | Type           | Notes                     |
|-------------|----------------|---------------------------|
| id          | SERIAL PK      |                           |
| centre_id   | INT FK         | → diagnostic_centres      |
| name        | VARCHAR(200)   |                           |
| description | TEXT           | nullable                  |
| price       | NUMERIC(10, 2) | source of truth for amount|

#### `bookings`
| Column               | Type           | Notes                              |
|----------------------|----------------|------------------------------------|
| id                   | SERIAL PK      |                                    |
| user_id              | INT FK         | → users (CASCADE DELETE)           |
| test_id              | INT FK         | → diagnostic_tests (RESTRICT)      |
| centre_id            | INT FK         | → diagnostic_centres (RESTRICT)    |
| appointment_datetime | TIMESTAMPTZ    | must be in the future              |
| amount               | NUMERIC(10, 2) | copied from test.price at creation |
| status               | VARCHAR(20)    | PENDING · CONFIRMED · FAILED · CANCELLED |

#### `payments`
| Column              | Type           | Notes                                    |
|---------------------|----------------|------------------------------------------|
| id                  | SERIAL PK      |                                          |
| booking_id          | INT FK         | → bookings                               |
| external_payment_id | VARCHAR(64)    | UNIQUE (e.g. `pay_<uuid>`)               |
| amount              | NUMERIC(10, 2) |                                          |
| status              | VARCHAR(20)    | SUCCESS · FAILED                         |
| created_at          | TIMESTAMPTZ    |                                          |

> **Partial unique index**: `WHERE status = 'SUCCESS'` — enforces at most one successful payment per booking at the database level.

#### `webhook_events`
| Column              | Type        | Notes                                    |
|---------------------|-------------|------------------------------------------|
| id                  | SERIAL PK   |                                          |
| event_id            | VARCHAR(128)| **UNIQUE** — idempotency key             |
| external_payment_id | VARCHAR(64) |                                          |
| event_type          | VARCHAR(20) | SUCCESS · FAILED                         |
| processed           | BOOLEAN     | set true after side effects applied      |
| created_at          | TIMESTAMPTZ |                                          |

### Webhook Idempotency Mechanism

1. `INSERT` into `webhook_events(event_id)` and `flush`.
2. If a **UNIQUE constraint violation** fires → rollback, return `already_processed: true`. No payment/booking rows touched.
3. If insert succeeds → `SELECT FOR UPDATE` on payment + booking, apply status, `processed = true`, `COMMIT`.

This is a database-level guarantee — no application-level locks or queues needed.

---

## 5. Important Assumptions

| Area | Assumption |
|------|-----------|
| **Catalogue** | Centres and tests are managed via `seed.py`; the API has no admin write endpoints |
| **Amounts** | Price is always taken from `diagnostic_tests.price`; client JSON amount is ignored |
| **Appointment time** | Must be strictly in the future (server validates) |
| **Passwords** | Minimum 8 characters, at least one letter and one digit |
| **Webhook auth** | Endpoint is unauthenticated — in production a HMAC signature would be verified |
| **Payment simulation** | `simulate_result` lets callers choose SUCCESS/FAILED; `PAYMENT_SIMULATE_RESULT=RANDOM` in env randomises it |
| **Booking ownership** | Any attempt to access another user's booking returns 404, not 403 (avoids resource enumeration) |
| **Redis availability** | If Redis is down, cache get/set failures are silently logged; reads fall through to PostgreSQL |
| **Celery** | Workers are best-effort; if the worker is down the booking is still CONFIRMED — email is retried up to 3× by Celery |
| **Email** | Flask-Mail + SMTP; configure `MAIL_*` env vars. `MAIL_SUPPRESS_SEND=true` disables actual sending in dev |

---

## 6. What I Would Improve With More Time

### Security
- **Webhook signature verification** — HMAC-SHA256 header (`X-Signature`) + replay-window check (reject events older than 5 minutes)
- **Rate limiting** on login and webhook endpoints (Flask-Limiter)
- **Refresh tokens + token revocation** (JWT blocklist in Redis)
- **Password reset flow** via email OTP

### Reliability
- **Outbox pattern** for webhook processing — store intent in DB, process in worker, guarantees at-least-once delivery without coupling it to the HTTP request thread
- **Dead-letter queue** for failed Celery tasks
- **Celery beat** for scheduled tasks (e.g. appointment reminders 24h prior)
- **Retry budget** per booking to prevent infinite payment retries

### Observability
- **Structured JSON logging** (python-json-logger) + correlation IDs per request
- **Prometheus metrics** — request latency, payment success rate, cache hit ratio
- **Sentry** integration for exception tracking

### API
- **Full OpenAPI 3 spec** on every route with request/response schemas (not just Swagger overlay)
- **Admin endpoints** for managing centres and tests (with cache invalidation on writes)
- **Pagination cursors** instead of offset pagination for large datasets

### Infrastructure
- **Dockerfile + docker-compose** for one-command local setup
- **Alembic data migrations** for seeding in CI
- **CI pipeline** (GitHub Actions) — lint (ruff), type check (mypy), pytest with PostgreSQL service container

---

## 7. Architecture

```
HTTP Client
    │
    ▼
Flask (Application Factory — app/__init__.py)
    ├── JWT Auth (Flask-JWT-Extended)
    ├── Marshmallow Schemas (validation)
    ├── Routes (thin — delegates to services)
    │     ├── /api/auth
    │     ├── /api/centres  ─── Redis cache (TTL 60s)
    │     ├── /api/bookings
    │     ├── /api/payments ─── PostgreSQL (SELECT FOR UPDATE)
    │     └── /api/payments/webhook ─── Idempotency via unique event_id
    │
    ├── Services (business logic)
    │     ├── auth_service
    │     ├── catalogue_service  ←→  Redis
    │     ├── booking_service
    │     ├── payment_service    →   Celery
    │     └── webhook_service
    │
    ├── SQLAlchemy ORM → PostgreSQL
    │
    └── Celery Worker (Redis broker)
          └── send_booking_confirmation
                └── Flask-Mail → SMTP
```

### Redis cache keys

| Key pattern                    | Content          | TTL      |
|-------------------------------|------------------|----------|
| `centres:list:{page}:{per_page}` | List response | 60 s     |
| `centre:{id}:tests`           | Tests for centre | 60 s     |

Cache is invalidated explicitly by `invalidate_centre_caches()` (used in `seed.py` and admin writes).

---

## 8. Tests

```powershell
# Run all tests (uses in-memory SQLite — no external services needed)
.venv\Scripts\pytest -v

# Run against real PostgreSQL
$env:TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5432/diagnostic_booking_test"
.venv\Scripts\pytest -v
```

**42 tests · 0 failures**

| File | What it covers |
|------|---------------|
| `test_auth.py` | Signup, login, weak password, JWT requirement |
| `test_authorization.py` | Ownership enforcement — User B cannot access User A's resources |
| `test_bookings.py` | Create, list, cancel, validation |
| `test_cache_and_celery.py` | Redis cache hit/miss/invalidation, Celery task dispatch and email |
| `test_centres.py` | List, retrieve, pagination meta |
| `test_payments.py` | Success, failure, retry, duplicate, cancel guard |
| `test_webhooks.py` | Idempotency (duplicate `event_id`), FAILED-cannot-downgrade-SUCCESS |

Test configuration:
- `CELERY_TASK_ALWAYS_EAGER=True` — tasks run synchronously, no worker needed
- `USE_FAKEREDIS=True` — in-memory Redis, no Redis server needed
- `MAIL_SUPPRESS_SEND=True` — no real emails sent; `mail.send` is mocked in email tests

---

## Quick Start (TL;DR)

```powershell
# 1. Install
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
copy .env.example .env   # then edit .env

# 3. Database
flask db upgrade
python seed.py

# 4. Run (3 terminals)
python run.py                                                          # Flask
celery -A celery_app.celery worker --loglevel=INFO --pool=solo        # Celery
redis-server                                                           # Redis (if not a service)

# 5. Test
pytest -v
```

API docs: `http://localhost:5000/api/docs`
