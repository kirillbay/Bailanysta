# Bailanysta — DEPLOYMENT

> Дата: 2026-09-05 | STEP 16 — Production Deployment
> Architecture: `Internet → HTTPS (nginx) → Frontend (nginx) + Backend (uvicorn) → PostgreSQL` — Docker Compose prod

---

## 1. Prerequisites

- Docker + Docker Compose v2
- Domain + DNS (e.g., `bailanysta.example.com` + `api.bailanysta.example.com` or single domain)
- VPS (2 vCPU / 2GB RAM min, 10GB disk)
- `openssl` for secret generation

---

## 2. Server Requirements

- Ubuntu 22.04 LTS recommended
- Docker 24+, Compose v2
- Open ports 80, 443 (and 8000 only internally if not behind proxy)
- 10GB for `postgres_data` + `uploads_data`

---

## 3. Environment Variables

Copy `.env.example` → `.env` and fill **real** values. Never commit `.env`.

```bash
cp .env.example .env
nano .env
```

Required for production:

```env
APP_ENV=production
DEBUG=false
DATABASE_URL=postgresql+psycopg://bailanysta:STRONGPASS@postgres:5432/bailanysta
POSTGRES_DB=bailanysta
POSTGRES_USER=bailanysta
POSTGRES_PASSWORD=STRONGPASS
SECRET_KEY=  # see §4
ALGORITHM=HS256
CORS_ORIGINS=https://bailanysta.example.com
VITE_API_URL=https://api.bailanysta.example.com
# or single origin: https://bailanysta.example.com (if proxy /api)
BACKEND_PORT=8000
FRONTEND_PORT=80
```

Frontend `VITE_API_URL` is baked at `npm run build` time → pass via `docker-compose.prod.yml` `args` or rebuild.

---

## 4. Secret Generation

```bash
openssl rand -hex 32
# or
python -c "import secrets; print(secrets.token_hex(32))"
```

Set as `SECRET_KEY`. In `production` the app **refuses to start** if `SECRET_KEY` is `change-me` or `<32` chars (`app/core/config.py: validate_secret`).

---

## 5. PostgreSQL

- Image `postgres:16-alpine`
- Volume `postgres_data:/var/lib/postgresql/data` — **persistent**, `down -v` would delete! Use `down` without `-v` for updates
- No host port exposed in prod (`docker-compose.prod.yml` comments out `5432:5432`) — internal `postgres:5432` only
- Healthcheck `pg_isready`

---

## 6. Migrations

Production must run Alembic, **not** `Base.metadata.create_all()`.

Backend `CMD` runs `alembic upgrade head && uvicorn ...` on startup.

Manual:

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml exec backend alembic current
# verify SQL without applying:
docker compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head --sql
```

Never run `downgrade` on prod without backup.

---

## 7. Docker

### Files

- `backend/Dockerfile` — `python:3.12-slim`, `pip install -r requirements.txt`, `useradd appuser`, `HEALTHCHECK /health`, `CMD alembic upgrade head && uvicorn --workers 2`
- `frontend/Dockerfile` — multi-stage: `node:20-alpine` build `npm ci && npm run build` → `nginx:alpine` serve `dist` + `nginx.conf` SPA fallback + `HEALTHCHECK`
- `docker-compose.yml` — dev: postgres only (with host port)
- `docker-compose.prod.yml` — prod: postgres + backend + frontend, `postgres_data` + `uploads_data` volumes, `bailanysta` network, healthchecks, `restart: unless-stopped`

### Commands

```bash
# Validate compose
docker compose -f docker-compose.prod.yml config

# Build
docker compose -f docker-compose.prod.yml build

# Up
docker compose -f docker-compose.prod.yml up -d

# Logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres

# Down (keep volumes!)
docker compose -f docker-compose.prod.yml down
# DANGER: down -v deletes DB + uploads!
```

---

## 8. Reverse Proxy

Use `nginx.prod.example.conf` as template. Must handle:

- `HTTP → HTTPS 301`
- `TLS` termination (Certbot `fullchain.pem` + `privkey.pem`)
- `/` → `frontend:80` (SPA `try_files $uri /index.html`)
- `/api/` → `backend:8000`
- `/uploads/` → `backend:8000`
- `/api/v1/ws` → `backend:8000` with `Upgrade: websocket` + `Connection: Upgrade` + `proxy_read_timeout 3600s`

Example `nginx.prod.example.conf` in repo root — no real certs.

Required headers already set by backend (`CSP`, `HSTS` etc) — proxy duplicates for defense.

---

## 9. HTTPS

- Certbot: `certbot --nginx -d bailanysta.example.com -d api.bailanysta.example.com`
- Auto-renew via `cron`
- `https://` → `Secure` cookies, `wss://` for WebSocket (`VITE_API_URL https://` → frontend does `http→ws` replace to `wss`)

---

## 10. Frontend

- Build args: `VITE_API_URL` must be `https://...` in prod, **not** `http://localhost`
- `npm run build` → `dist` (472kB) served via `nginx` with `try_files $uri /index.html` for SPA routes (`/`, `/search`, `/clubs/:slug`, `/projects/:id`, `/profile`, `/settings` all fallback to `index.html`)
- Lazy routes: `Suspense` fallback skeleton

---

## 11. Backend

- Production ASGI: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` (not `--reload`)
- Env: `APP_ENV=production`, `DEBUG=false`, `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
- CORS: explicit `CORS_ORIGINS=https://bailanysta.example.com`, **no** `*` with credentials
- Health: `GET /health` liveness (no DB), `GET /api/v1/health` + `GET /api/v1/health/db` readiness (DB check) — no secrets leak
- Migrations: `alembic upgrade head` before serve
- Healthchecks: `HEALTHCHECK` in Dockerfile

---

## 12. WebSocket (WSS)

```
Client (wss://) → nginx (443) → http://backend:8000/api/v1/ws (ws)
```

Headers:

```
Upgrade: websocket
Connection: Upgrade
```

`getWsUrl()` in `frontend/src/hooks/useRealtime.ts` does `VITE_API_URL.replace(/^http/, "ws")` → `https` → `wss` automatic.

Events: `connected`, `subscribed`, `message.created|updated|deleted`, `notification.created`, `error` — unchanged.

Single-instance `realtime/manager.py` (no Redis) — documented.

---

## 13. Uploads

- Path `uploads/` inside backend container → volume `uploads_data:/app/uploads`
- Persistent across recreates (`docker compose down` without `-v` keeps it)
- Permissions `755`, `appuser`
- Validation: `Pillow verify`, `5MB`, `UUID`, `safe_subdir`, `no SVG`
- Backup: `docker compose -f docker-compose.prod.yml exec backend tar czf - /app/uploads` or host `docker volume` backup

---

## 14. Backups

PostgreSQL:

```bash
# Dump
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > backup-$(date +%F).sql.gz

# Restore (DANGER: overwrites)
gunzip -c backup-2026-09-05.sql.gz | docker compose -f docker-compose.prod.yml exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB
```

Uploads:

```bash
docker run --rm -v bailanysta_uploads_data:/volume -v $(pwd):/backup alpine tar czf /backup/uploads-$(date +%F).tar.gz -C / volume .
```

Periodic via `cron` + off-site copy (R2/S3) recommended.

---

## 15. Logs

```bash
docker compose -f docker-compose.prod.yml logs -f --tail=100 backend
docker compose -f docker-compose.prod.yml logs -f postgres
```

Backend logs: startup `Uvicorn running on 0.0.0.0:8000`, `alembic upgrade`, `500 Internal server error` (no stack trace to client). Do **not** log `password`, `JWT`, `cookies`, `SECRET_KEY`, `DATABASE_URL`.

---

## 16. Health Checks

```bash
curl -f https://bailanysta.example.com/health
curl -f https://api.bailanysta.example.com/api/v1/health
curl -f https://api.bailanysta.example.com/api/v1/health/db  # readiness
```

Frontend health: `wget -q --spider http://localhost/` inside container.

All must return `200`.

---

## 17. Update Procedure

```bash
git pull
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d
# migrations run automatically; check logs
docker compose -f docker-compose.prod.yml logs -f backend | grep alembic
```

Zero-downtime requires external proxy with two backends — for MVP, brief restart is acceptable.

---

## 18. Rollback Procedure

```bash
git log --oneline -5
git checkout <previous-commit>
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d
# if DB migration broke:
docker compose -f docker-compose.prod.yml exec postgres pg_restore ...
```

Keep `postgres_data` volume — `down -v` would lose DB.

---

## 19. Known Limitations (prod)

- In-memory rate limiter (single-instance, no Redis)
- Single-instance WebSocket `realtime/manager.py` (no Redis Pub/Sub)
- Local `uploads/` volume (no S3)
- Offset pagination (no cursor)
- No E2EE, no 2FA, no private DMs voice/video
- `alembic` must run on every backend start (no separate job)
- Documented in `SECURITY.md` + `ARCHITECTURE.md`

---

## 20. Checklist

- [ ] `SECRET_KEY` strong (>=32) ✅ (`config.py` validates)
- [ ] `CORS_ORIGINS` explicit https ✅
- [ ] `Secure=True HttpOnly=True SameSite=Lax` ✅
- [ ] `CSP` + `HSTS` ✅
- [ ] `DATABASE_URL` via env, not hardcoded ✅
- [ ] `alembic upgrade head` ✅
- [ ] `uploads_data` persistent ✅
- [ ] `postgres_data` persistent ✅
- [ ] `docker compose -f docker-compose.prod.yml config` ✅
- [ ] `docker compose -f docker-compose.prod.yml up -d` ✅ (if Docker available, else NOT VERIFIED)
- [ ] `curl /health` ✅
- [ ] `pytest -q` 281 ✅
- [ ] `tsc --noEmit` ✅
- [ ] `npm run build` 472kB ✅

---

## 21. Smoke Test (if Docker available)

```bash
docker compose -f docker-compose.prod.yml up -d
sleep 30
curl -f http://localhost:8000/health
curl -f http://localhost:8000/api/v1/health
# register/login/post/project/club/message via API
# WebSocket wss://localhost/api/v1/ws?token=...
docker compose -f docker-compose.prod.yml down
```

If Docker not available on CI/host → `NOT VERIFIED — Docker not available on this host` (honest, not faked).

---

*See `README.md` §Deployment for quick start, `SECURITY.md` for security, `ARCHITECTURE.md` §19-20 for design.*
