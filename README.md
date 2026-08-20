# Usta kg 🇰🇬

**Register them, book them, trust them.** Usta kg is a full-stack marketplace that connects **customers** across Kyrgyzstan with **local service masters** (usta) — plumbers, electricians, builders, tutors, and more — for finding, pricing, and contracting home/job services. The platform spans a FastAPI (REST + WebSocket) backend, an Expo/React Native mobile app, and a Next.js web app with an admin panel.

**Phases 0–10 (project complete):** environment setup → architecture → database → backend API → mobile app → web app → real-time chat → QA → Dockerization/deployment → **launch & analytics**. Everything is committed to `origin/main`.

---

## 1. Overview

| | |
|---|---|
| **Mission** | Make hiring trusted local professionals in Kyrgyzstan fast, safe, and transparent. |
| **Target market** | Kyrgyzstan — Bishkek and beyond; customer ↔ master matching with Kyrgyz/Russian-language UI support. |
| **Core loop** | Customer posts an order → masters send offers → customer accepts one → live chat → completes → reviews & ratings. |

### Tech stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL 15, psycopg2 |
| **Auth** | JWT (access + refresh), OAuth2 password flow, bcrypt (passlib), phone-number accounts (`+996…`) |
| **Realtime** | WebSocket chat via FastAPI `ConnectionManager` |
| **Mobile** | Expo / React Native, Zustand auth store, Axios API client, WebSocket chat UI |
| **Web** | Next.js (App Router), Tailwind CSS, Axios client, admin panel |
| **Infra** | Docker Compose (db + backend + web + nginx), Nginx reverse proxy (REST + WebSocket) |
| **QA & Ops** | Pytest suite (dedicated PostgreSQL test DB), structured JSON analytics/audit logs |

---

## 2. Architecture Overview

```
                            ┌─────────────────────────┐
                            │         Client          │
                            │  mobile (Expo)  web      │
                            │  (React Native) (Next)   │
                            └────────────┬────────────┘
                                         │ HTTPS: REST + WebSocket
                                         ▼
                            ┌─────────────────────────┐
                            │       Nginx (:80)        │
                            │  reverse proxy + ws://   │
                            └────────────┬────────────┘
                ┌────────────────────────┼────────────────────┐
                ▼                                             ▼
    ┌───────────────────────┐                    ┌───────────────────┐
    │  Backend (:8000)      │    ┌─────────┐    │  Web (:3000)      │
    │  FastAPI uvicorn      │───▶│Database │    │  Next.js admin +  │
    │  REST + WebSocket     │    └─────────┘    │  landing pages    │
    │  JWT auth + analytics │    PostgreSQL 15  └───────────────────┘
    └───────────────────────┘
```

Key flows:

1. **Auth** — users register with a Kyrgyzstan phone number (`+996XXXXXXXXX`), receive JWT access + refresh tokens.
2. **Matching** — customers create orders; masters submit offers; the customer accepts one offer (others auto-reject) and the order moves to `IN_PROGRESS`.
3. **Realtime chat** — accepting an offer auto-creates a chat; participants talk live over `WS /api/v1/chats/ws/{chat_id}` (messages persisted to Postgres).
4. **Trust** — on completion, customers review the master; ratings and review counts are recomputed server-side.
5. **Observability** — `/api/v1/health` exposes DB/WebSocket/version status; `/ready` is a PostgreSQL-aware readiness probe; `app/core/logging.py` adds structured JSON request logging; `app/core/analytics.py` emits structured metrics for every key business event.

---

## 3. Quick Start (local development)

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- PostgreSQL 15 running locally (or Docker)

### Backend

```bash
# 1. Create the database (once)
createdb ustakg_db   # or: CREATE DATABASE ustakg_db;

# 2. Configure environment
cp .env.example .env
#    edit POSTGRES_USER / POSTGRES_PASSWORD / SECRET_KEY to match your machine

# 3. Install & run
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head             # apply migrations
uvicorn app.main:app --reload
```

Backend is now at `http://localhost:8000` — Swagger UI at `http://localhost:8000/docs`, OpenAPI JSON at `http://localhost:8000/api/v1/openapi.json`.

### Web (Next.js)

```bash
cd web
npm install
npm run dev
# → http://localhost:3000
```

### Mobile (Expo)

```bash
cd mobile
npm install
npm start
# scan the QR code with Expo Go, or press a / i for Android / iOS emulator
```

### Run the test suite (optional)

```bash
cd backend
python -m pytest tests -v
```

> Tests spin up a dedicated `ustakg_test_db` PostgreSQL database and apply the Alembic migrations automatically.

---

## 4. Production Deployment (Docker Compose)

The repo ships a complete Dockerized stack (`docker-compose.yml` + `backend/Dockerfile`, `web/Dockerfile`, `nginx/nginx.conf`; see also `DEPLOYMENT.md`).

```bash
# 1. Clone & configure production secrets
cp .env.example .env
#    set strong POSTGRES_PASSWORD, SECRET_KEY and CORS_ORIGINS

# 2. Build and start all services
docker compose up -d --build
```

What it brings up:

| Service | Image / Build | Exposed |
|---|---|---|
| `db` | `postgres:15` | internal (healthcheck `pg_isready`) |
| `backend` | `backend/Dockerfile` (python:3.12-slim) | `8000` |
| `web` | `web/Dockerfile` | `3000` |
| `nginx` | `nginx:stable` | `80` (proxies REST + WebSocket) |

```bash
docker compose logs -f          # follow all services
docker compose ps               # status check
docker compose down             # stop (add -v to drop the data volume)
```

Post-deploy checks:

```bash
curl http://<host>/health                 # liveness (process up?)
curl http://<host>/ready                  # readiness (DB reachable? version 1.0.0)
curl http://<host>/api/v1/health          # DB/WebSocket/version status
curl http://<host>/api/v1/categories/     # smoke test against real DB
```

> **Production health-check cheat sheet:** `/health` = liveness only (no DB I/O, safe for
> load balancers/uptime monitors). `/ready` = readiness (issues `SELECT 1` to PostgreSQL).
> See `DEPLOYMENT.md` for wiring these into your LB / container healthchecks.

---

## 5. API Documentation

**Base URL:** `http://localhost:8000` · **Interactive docs:** `/docs` · **OpenAPI:** `/api/v1/openapi.json`
**Auth:** `Authorization: Bearer <access_token>` — obtain a token from `POST /api/v1/auth/login` (OAuth2 form: `username` = phone number, `password`).

### REST endpoints (20+)

| Method | Path | Description | Access |
|---|---|---|---|
| GET | `/health` | Liveness probe (no DB I/O) | Public |
| GET | `/ready` | Readiness probe (DB `SELECT 1`, version `1.0.0`) | Public |
| GET | `/api/v1/health` | DB + WebSocket status, version `1.0.0` | Public |
| POST | `/api/v1/auth/register` | Register customer/master (returns tokens) | Public |
| POST | `/api/v1/auth/login` | JWT login (phone + password) | Public |
| POST | `/api/v1/auth/refresh` | Exchange refresh token for a new pair | Public |
| GET | `/api/v1/auth/me` | Current user profile | Auth |
| GET | `/api/v1/categories/` | Category tree (subcategories nested) | Public |
| POST | `/api/v1/categories/` | Create a category | Admin |
| GET | `/api/v1/masters/` | List masters (filters: `rating`, `category_id`) | Public |
| GET | `/api/v1/masters/{id}` | Master public profile | Public |
| PUT | `/api/v1/masters/profile` | Update own bio/experience/categories | Master |
| POST | `/api/v1/orders/` | Create an order | Auth |
| GET | `/api/v1/orders/` | List orders (defaults to `OPEN`; filters `status_filter`, `category_id`) | Public |
| GET | `/api/v1/orders/{id}` | Order details + offers | Auth (owner/admin for non-open) |
| PATCH | `/api/v1/orders/{id}/status` | Change order status | Owner / Admin |
| POST | `/api/v1/offers/` | Submit offer on an open order | Master |
| GET | `/api/v1/offers/order/{order_id}` | List offers for an order | Owner / Admin |
| POST | `/api/v1/offers/{id}/accept` | Accept offer (rejects others, auto-creates chat) | Owner / Admin |
| POST | `/api/v1/reviews/` | Review a completed order (updates master rating) | Owner / Admin |
| GET | `/api/v1/chats/` | List my chats | Auth |
| GET | `/api/v1/chats/{chat_id}/messages` | Chat message history | Chat participant |

### WebSocket endpoint

| Endpoint | Auth | Protocol |
|---|---|---|
| `WS /api/v1/chats/ws/{chat_id}` | JWT via `?token=<access_token>` query param | JSON messages |

```jsonc
// Client → Server
{ "message_text": "Здравствуйте, когда сможете приехать?" }

// Server → Client
{ "type": "message", "id": "…", "chat_id": "…", "sender_id": "…",
  "message_text": "…", "created_at": "…" }
// Server → Client on join
{ "type": "system", "message": "joined" }
```

### Analytics / audit events

The backend emits structured JSON log lines via `app.core.analytics.track_event(event, payload)`:

| Event | Trigger |
|---|---|
| `user.registered` | New customer/master registration |
| `order.created` | Customer places an order |
| `offer.accepted` | Customer accepts a master's offer |
| `review.submitted` | Review posted after a completed order |

### Structured access logging

`app.core.logging.configure_logging()` installs a JSON `StreamHandler` on the root logger, and
`RequestLoggingMiddleware` emits one JSON line per HTTP request:

```json
{"ts": "2026-08-20T12:00:00+0000", "level": "INFO", "logger": "ustakg.access",
 "message": "request_completed", "method": "GET", "path": "/health",
 "status_code": 200, "duration_ms": 2.31, "request_id": "-", "client_ip": "127.0.0.1"}
```

Forward the `ustakg.analytics` and `ustakg.access` loggers to your aggregator (ELK, Datadog,
CloudWatch, etc.) for dashboards on registrations, orders, conversion, satisfaction, and API
latency/error rates.

---

## 6. Project Completion Summary (Phases 0–10)

| Phase | Deliverable | Status |
|---|---|---|
| **0 — Environment setup** | Dev environment, Git/GitHub repo `Ustakg` | ✅ |
| **1 — Product & MVP scope** | Product vision, MVP requirements, user roles | ✅ |
| **2 — System architecture** | Monorepo (`backend/`, `mobile/`, `web/`), FastAPI core, Dockerfile, env config | ✅ |
| **3 — Database structure** | SQLAlchemy models (9 tables), Alembic migration, applied to PostgreSQL | ✅ |
| **4 — Backend API core** | Auth (JWT + roles), categories, masters, orders, offers, reviews, pytest suite | ✅ |
| **5 — Mobile app** | Expo/React Native foundation, navigation, screens, Axios API client, Zustand store | ✅ |
| **6 — Web app & admin** | Next.js landing pages + admin panel with Tailwind | ✅ |
| **7 — Realtime chat** | WebSocket chat backend + mobile/web chat UI | ✅ |
| **8 — QA verification** | End-to-end tests across stacks, debug-log cleanup | ✅ |
| **9 — Production deployment** | `docker-compose.yml`, Dockerfiles, Nginx config, `DEPLOYMENT.md` | ✅ |
| **10 — Launch & analytics** | `/api/v1/health` (DB/WebSocket/version), analytics event tracking, master README | ✅ |

### Repository layout

```
usta-kg/
├── backend/            # FastAPI service (app/, tests/, Dockerfile, alembic, requirements.txt)
├── mobile/             # Expo / React Native app (App.js, src/)
├── web/                # Next.js app (src/ with app/, components/, services/, hooks/)
├── nginx/              # nginx.conf (REST + WebSocket reverse proxy)
├── docker-compose.yml  # full stack orchestration
├── DEPLOYMENT.md       # deployment runbook
└── README.md           # this document
```

---

**Usta kg — every phase implemented, committed to `origin/main`, and ready for public launch.** 🚀

