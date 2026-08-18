# Usta kg — Deployment Guide

This document describes how to deploy the Usta kg monorepo on a Linux server using Docker Compose.

Prerequisites
- A Linux server (Ubuntu 22.04+ recommended)
- Docker & Docker Compose installed
- Domain name configured to point to the server

Quick start (example)

1. Clone the repo on the server:

```bash
git clone <repo-url> ustakg
cd ustakg
```

2. Copy and edit `.env.example` to `.env` and set production secrets:

```bash
cp .env.example .env
# edit .env with secure values (POSTGRES_PASSWORD, SECRET_KEY, CORS_ORIGINS)
```

3. Start the stack:

```bash
docker compose up -d --build
```

4. SSL (optional) — recommended to use a reverse proxy with SSL termination (NGINX + Certbot):

Install certbot and obtain certificate:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.example
```

Notes
- The `docker-compose.yml` starts four services: `db` (Postgres), `backend` (FastAPI + uvicorn), `web` (Next.js), and `nginx` (reverse proxy). Nginx is configured to proxy `/api/` to the backend and all other requests to the Next.js app. WebSocket upgrade headers are set for chat endpoints.
- On first start the backend runs `alembic upgrade head` to apply migrations. Ensure the DB user configured in `.env` has permission to create tables.
- For production scale, run multiple backend replicas behind a real load balancer, use managed Postgres, and configure persistent storage/backups.

Rollback
- To stop the stack and remove containers:

```bash
docker compose down
```

Troubleshooting
- If the backend cannot connect to DB, check `docker compose logs db` for Postgres errors.
- If websockets fail, ensure Nginx config includes `proxy_set_header Upgrade` and `Connection "upgrade"` for the `/api/` and `/api/v1/chats/ws/` locations.
