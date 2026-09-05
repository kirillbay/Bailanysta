# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 3 — Authentication)

---

## 1. Текущий STEP

**STEP 3 — Authentication — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 3 — authentication` (см. §17)
- Статус: JWT + Argon2id + HttpOnly cookies + register/login/me/logout + protected frontend — всё работает, 39 тестов зелёных

**Последний завершённый STEP:** STEP 3 — Authentication (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 4 — Profiles (avatar, bio, редактирование)

---

## 2. Список завершённых STEP

| STEP | Название | Дата | Commit | Статус |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | `7cf5f72` | ✅ Done |
| 0+ | Persistent Protocol setup | 2026-09-05 | `2d5e1d3` | ✅ Done |
| 1 | Foundation | 2026-09-05 | `7619de1` | ✅ Done |
| 2 | Database Foundation | 2026-09-05 | `d324979` | ✅ Done |
| 3 | Authentication | 2026-09-05 | `feat STEP3` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Auth ✅ → 4 Profiles → 5 Posts & Media → 6 Feed & Interactions → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: React + Vite @ :5173 + AuthProvider + RequireAuth] → [Backend: FastAPI @ :8000 /api/v1/auth/* + health/db] → [PostgreSQL 16 + SQLite test]
                         ↕ credentials:include, HttpOnly cookie `access_token` (Lax, Secure prod, 15m)
                         ↕ Argon2id + JWT HS256 (sub/exp/iat/type)
```

- Frontend: `AuthProvider` (useQuery me), `RequireAuth`, `LoginPage/RegisterPage` (RHF+Zod), `api/auth.ts`, `stores/auth.tsx`, `App.tsx` /login /register public, AppShell protected + user badge + logout
- Backend: `app/core/security.py` (hash/verify/create_token/decode + cookie helpers), `app/core/deps.py:get_current_user`, `app/api/v1/auth.py` (4 endpoints), `app/schemas/auth.py`, `app/schemas/user.py:UserRead`
- DB unchanged: `users` model, `001_create_users`, docker-compose
- Детали → `ARCHITECTURE.md §14`, `SECURITY.md §2/13/14`

---

## 4. Frontend Status

- Статус: **runnable ✅**
- Auth: `api/client.ts` +post, `api/auth.ts` (me/register/login/logout), `stores/auth.tsx` (AuthProvider useQuery me, useAuth, logout via invalidate), `components/RequireAuth.tsx` (loading spinner → redirect /login), `pages/LoginPage.tsx` (identifier+password Zod), `pages/RegisterPage.tsx` (username/email/password/display_name Zod regex), `App.tsx` (/login,/register public, AppShell под RequireAuth), `main.tsx` AuthProvider, `AppShell.tsx` user badge + logout
- Deps: + `@hookform/resolvers@3.9.0` — установлен
- Build: `tsc --noEmit` ✅, `npm run build` ✅ 3.77s, 447.93 kB js gzip 138.94 kB (с auth), 1683 modules

---

## 5. Backend Status

- Статус: **runnable ✅**
- Deps: `requirements.txt` + `argon2-cffi==23.1.0` + `PyJWT==2.10.1` — установлены
- Core: `app/core/config.py` + `algorithm HS256`, `access_token_expire_minutes 15`, `refresh 7`, `secret_key`; `app/core/security.py` (PasswordHasher t=3,m=65536,p=4, COOKIE_NAME access_token, create_access_token, decode_token explicit alg, set/clear HttpOnly Lax Secure=prod max_age 900); `app/core/deps.py` (cookie→decode→exp→type→UUID→DB→is_active→401)
- Auth API: `POST /auth/register` 201 + set cookie, 409 username/email, case-insensitive email lower, `POST /auth/login` 200 uniform 401 + cookie (identifier email/username, case-insensitive email), `GET /auth/me` 200 via get_current_user, `POST /auth/logout` 204 clear cookie (fixed response handling)
- Schemas: `app/schemas/auth.py` (RegisterRequest username 3-50 regex, EmailStr, password 8-128, display_name 100; LoginRequest identifier+password), `app/schemas/user.py:UserRead` (no password_hash)
- Router: `app/api/v1/router.py` includes auth_router
- Tests: `app/tests/test_auth.py` 25 pass, total `pytest -v` 39 pass (25 auth + 8 db + 6 health)
- Startup: `uvicorn` ✅, routes `/api/v1/auth/*` verified

---

## 6. Database Status

- Статус: **unchanged ✅** (STEP2 foundation)
- Model `users` готов для auth (password_hash nullable)
- Migrations: `001_create_users` — no new migration (не требуется)

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |

- No new migration for STEP3 (schema не менялась)

---

## 8. Authentication Status

- Статус: **реализовано ✅**
- Hashing: Argon2id (`argon2-cffi` PasswordHasher default) — `hash_password` / `verify_password`
- JWT: HS256, `sub` UUID, `exp` 15m, `iat`, `type=access`, `SECRET_KEY` from env, explicit `algorithms=[HS256]`, no `alg=none`
- Cookies: `access_token` HttpOnly, Secure=is_production, SameSite=Lax, Path=/, Max-Age 900, `clear_auth_cookie` delete_cookie path=/
- Endpoints: `POST /auth/register` 201, `POST /auth/login` 200, `GET /auth/me` 200/401, `POST /auth/logout` 204
- Dependency: `get_current_user` — 401 на missing/invalid/expired/modified/nonexistent/inactive/type!=access
- Validation: username `^[a-zA-Z0-9_]+$` 3-50, email RFC (EmailStr) lower-cased, password 8-128, not logged, not returned
- Frontend flow: unauth → /auth/me 401 → redirect /login; login → set cookie → invalidate me → redirect /; logout → clear → redirect /login

---

## 9. Implemented Features

> STEP 3 — auth done, остальные — заглушки.

- [x] Foundation (STEP1) — shell, health, i18n, theme
- [x] Database (STEP2) — PG, SQLAlchemy, Alembic, User model
- [x] Auth: register/login/me/logout + JWT + HttpOnly + Argon2id + protected frontend
- [ ] Profiles — STEP4
- [ ] Posts — STEP5
- [ ] Feed — STEP6
- [ ] Stories — STEP8
- [ ] Clubs — STEP9
- [ ] Messaging — STEP10
- [ ] Notifications — STEP11
- [ ] Projects — STEP12
- [x] i18n + theme — done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build 447 kB, auth ready
- Backend: Render/Railway — auth ready, CORS credentials, health/db
- DB: docker-compose postgres:16-alpine

---

## 11. Tests Status

- Backend: `pytest -v` → **39 passed** (25 auth + 8 db + 6 health) ✅
  - auth: register 8 (success, dup username/email/case, invalid email/password/username, not returned), login 7 (by email/username/case-insensitive, wrong pass, unknown, inactive, cookie attrs), me 6 (auth, no cookie, invalid, expired, modified, nonexistent), logout 2, security 2
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.77s
- Integration: `/api/v1/auth/me` 401 unauth, 200 auth — manual via test client ✅
- Coverage: не измерялась

---

## 12. Known Issues

- Rate limiting на `/auth/login` (5/min/IP) — **debt** (ARCHITECTURE.md §14, SECURITY.md §14) — архитектура готова, требует Redis/slowapi в STEP14
- Double-submit CSRF token не реализован — Lax + CORS считается достаточным для MVP (SECURITY.md §13)
- `alembic upgrade head` без PG → OperationalError (ожидаемо, нужен Docker) — не блокер для auth tests (SQLite)

---

## 13. Technical Debt

- Добавить `slowapi` rate limiter на login/register (STEP14)
- Добавить `DATABASE_URL_TEST` для PG-тестов (сейчас SQLite for auth tests — изолирован via StaticPool in-memory for auth, file for db tests)
- Вынести `version` single source (долг с STEP1)
- Добавить refresh token 7d flow (`/auth/refresh`) — placeholder в config, не реализован

---

## 14. Current Blockers

- Нет блокеров. Готов к STEP 4.

---

## 15. Next Recommended STEP

**STEP 4 — Profiles**

- `GET /users/{username}` public, `PATCH /users/me` protected (avatar, bio, display_name, location etc — расширить User model если нужно)
- Миграция если поля меняются, тесты на ownership, frontend profile page

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | Argon2id via `argon2-cffi` PasswordHasher default (t=3,m=64MB,p=4) | Modern, без custom crypto |
| 2026-09-05 | JWT HS256 + `PyJWT` + explicit algorithm, sub UUID + type access | Без alg=none, strong secret |
| 2026-09-05 | Cookie `access_token` HttpOnly Lax Secure=prod Path/ Max-Age 15m | XSS safe, CSRF Lax + CORS |
| 2026-09-05 | Login identifier = email OR username (case-insensitive email) | UX: один field |
| 2026-09-05 | Uniform `401 Invalid credentials` (не раскрывать существование) | Anti-enumeration |
| 2026-09-05 | Logout via `response.status_code=204` + `clear_auth_cookie(response)` | Fix Set-Cookie not sent bug |
| 2026-09-05 | Frontend AuthProvider useQuery me (retry false) + RequireAuth redirect | Простой protected route без Zustand |
| 2026-09-05 | Test DB for auth: in-memory StaticPool SQLite (изолирован per module) | Быстрые тесты без Docker, prod PG |

---

## 17. Последний Git Commit

```
feat: STEP 3 — authentication (предстоит)
Branch: main | Status: clean (после commit)
Auth: security.py, deps.py, auth.py, schemas/auth.py, frontend auth stores/pages/RequireAuth, tests 25
```

---

## 18. Изменённые файлы (STEP 3)

```
[mod] backend/requirements.txt (+ argon2-cffi, PyJWT)
[mod] backend/app/core/config.py (+ algorithm, expire minutes/days)
[new] backend/app/core/security.py (hash/verify/jwt/cookies)
[new] backend/app/core/deps.py (get_current_user)
[new] backend/app/schemas/auth.py
[new] backend/app/api/v1/auth.py
[mod] backend/app/api/v1/router.py (+ auth_router)
[mod] backend/app/tests/conftest.py (no change, kept)
[new] backend/app/tests/test_auth.py (25 tests)
[mod] frontend/src/api/client.ts (+ post)
[new] frontend/src/api/auth.ts
[new] frontend/src/stores/auth.tsx
[new] frontend/src/components/RequireAuth.tsx
[new] frontend/src/pages/LoginPage.tsx
[new] frontend/src/pages/RegisterPage.tsx
[mod] frontend/src/App.tsx (+ /login,/register, RequireAuth)
[mod] frontend/src/main.tsx (+ AuthProvider)
[mod] frontend/src/components/layout/AppShell.tsx (+ user badge + logout)
[mod] frontend/package.json (+ @hookform/resolvers)
[mod] ARCHITECTURE.md (§14 STEP3)
[mod] SECURITY.md (§2,13,14 CSRF/rate limit)
```

---

## 19. Как восстанавливать контекст (New Chat Recovery)

1. Найти workspace `C:\Users\lueex\Desktop\Bailanysta`
2. Прочитать `MASTER_PROMPT.md`
3. Прочитать этот `PROJECT_STATE.md`
4. Прочитать `ARCHITECTURE.md` + `SECURITY.md`
5. Прочитать последние записи `DEVELOPMENT_LOG.md`
6. Проверить `git status` + `git log --oneline -5`
7. Проверить структуру `frontend/` и `backend/`
8. Определить последний завершённый STEP и следующий → ждать команды
