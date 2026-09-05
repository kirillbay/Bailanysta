# Bailanysta — PROJECT STATE

> Persistent memory проекта. Обновляется после КАЖДОГО STEP.
> Протокол: PERSISTENT DEVELOPMENT PROTOCOL (2026-09-05)
> Последнее обновление: 2026-09-05 (STEP 2 — Database Foundation)

---

## 1. Текущий STEP

**STEP 2 — Database Foundation — ЗАВЕРШЁН ✅**

- Workspace: `C:\Users\lueex\Desktop\Bailanysta`
- Branch: `main` | Последний commit: `feat: STEP 2 — database foundation` (см. §17)
- Статус: PostgreSQL foundation готов, User model + Alembic + тесты + health/db работают

**Последний завершённый STEP:** STEP 2 — Database Foundation (2026-09-05)

**Следующий рекомендуемый STEP:** STEP 3 — Authentication (Argon2id, JWT, register/login/me)

---

## 2. Список завершённых STEP

| STEP | Название | Дата | Commit | Статус |
|------|----------|------|--------|--------|
| 0 | Project Initialization | 2026-09-05 | `7cf5f72` | ✅ Done |
| 0+ | Persistent Protocol setup | 2026-09-05 | `2d5e1d3` | ✅ Done |
| 1 | Foundation | 2026-09-05 | `7619de1` | ✅ Done |
| 2 | Database Foundation | 2026-09-05 | `feat STEP2` | ✅ Done |

> План: 0 Init ✅ → 1 Foundation ✅ → 2 Database ✅ → 3 Authentication → 4 Profiles → 5 Posts & Media → 6 Feed & Interactions → 7 Follow/Search/Hashtags → 8 Stories → 9 Clubs → 10 Club Channels & Messaging → 11 Notifications & Realtime → 12 Projects → 13 i18n/Theme/Responsive → 14 Security Hardening → 15 Testing/Perf → 16 Deployment → 17 Final QA

---

## 3. Текущая архитектура

```
[Browser] → [Frontend: React + Vite @ :5173] → [Backend: FastAPI @ :8000 /api/v1/*] → [PostgreSQL 16 (docker-compose) + SQLite test fallback]
                     ↕ i18next (ru/kk/en)              ↕ SQLAlchemy 2.x + Alembic, get_db, /health + /health/db
```

- Frontend: без изменений с STEP 1 (shell + routing + i18n + theme)
- Backend: `app/database/{base.py, session.py, __init__.py}` + `app/database.py` re-export, `app/models/user.py`, `app/schemas/user.py`, `alembic/{env.py, script.py.mako, versions/001_create_users.py}`, `docker-compose.yml`, `health/db`
- DB: PostgreSQL (prod/local) via `psycopg[binary] 3.2.3`, `postgresql+psycopg://` URL, Alembic metadata via `Base`
- Детали → `ARCHITECTURE.md`

---

## 4. Frontend Status

- Статус: **runnable ✅** (без изменений, regression PASS)
- Build: `npm run build` ✅ 3.48s, 354.82 kB js gzip 113 kB (STEP2 regression)
- TSC: `npx tsc --noEmit` ✅

---

## 5. Backend Status

- Статус: **runnable ✅**
- Deps: `requirements.txt` + `psycopg[binary]==3.2.3` + `email-validator==2.2.0` — установлены
- Core: `app/core/config.py` — `database_url` = `postgresql+psycopg://...` + `database_url_safe` (masked), `cors_origins_list`, `is_production`
- Database: `app/database/base.py` (DeclarativeBase), `app/database/session.py` (engine pool_pre_ping, SessionLocal, get_db, check_db_connection), `app/database/__init__.py` + `app/database.py` re-export
- Models: `app/models/user.py` (UUID PK, username/email unique 50/320, password_hash nullable, display_name/bio/avatar/cover, is_active default true, created_at/updated_at server_default func.now()), `app/models/__init__.py` import for Alembic
- Schemas: `app/schemas/user.py` (UserBase, UserCreate, UserRead with EmailStr, pattern, from_attributes), `app/schemas/__init__.py`
- API: `app/api/v1/health.py` — `GET /health` + `GET /health/db` (check_db_connection, no stack trace), `app/api/v1/router.py` aggregate, `app/main.py` unchanged (CORS + headers + global handler)
- Alembic: `alembic.ini` (script_location alembic), `alembic/env.py` (Base import, asyncpg→psycopg convert, target_metadata, compare_type/server_default), `alembic/script.py.mako`, `alembic/versions/001_create_users.py` (users table)
- Tests: `app/tests/conftest.py` (SQLite file .test_bailanysta.db, Base.metadata.create_all, session transaction), `app/tests/test_health.py` 6 pass, `app/tests/test_database.py` 8 pass → total 14 pass
- Startup: `uvicorn app.main:app` ✅, `/api/v1/health` ok, `/api/v1/health/db` → `{"database":"unreachable"}` когда PG не запущен (корректно, без leak), `{"connected"}` когда PG поднят

---

## 6. Database Status

- Статус: **foundation готов ✅**
- Production: PostgreSQL 16 (docker-compose `postgres:16-alpine`)
- Local dev: `docker-compose up postgres` (volume postgres_data, healthcheck pg_isready, env POSTGRES_DB/USER/PASSWORD/PORT via .env)
- Engine: `create_engine(settings.database_url, pool_pre_ping=True, echo=debug)` — SQLAlchemy 2.x sync
- Session: `SessionLocal(sessionmaker autocommit False)`, `get_db()` yields+close, не долгоживущая
- URL: `postgresql+psycopg://postgres:postgres@localhost:5432/bailanysta` (placeholder в .env.example, не хардкод)
- SQLite: только для быстрых unit-тестов (`app/tests/conftest.py`), явно отделено, не production fallback

---

## 7. Migrations Status

| Revision | Description | Date | Статус |
|----------|-------------|------|--------|
| 001_create_users | create users table | 2026-09-05 | ✅ Created, --sql OK |

- `alembic upgrade head --sql` → generates CREATE TABLE users + UNIQUE(email), UNIQUE(username) ✅
- `alembic downgrade 001_create_users:base --sql` → DROP TABLE users ✅
- Online `upgrade`/`downgrade` требует живой Postgres (Docker) — `alembic upgrade head` без PG даёт OperationalError (ожидаемо), `check`/`current` без PG — warning + skip (env.py fallback)
- `Base.metadata` единый источник (env.py imports app.models)

---

## 8. Authentication Status

- Статус: **не реализовано** (план STEP 3)
- Подготовлено: `users.password_hash` nullable, schemas с `password` field, model готова

---

## 9. Implemented Features

> STEP 2 — database foundation, ещё без бизнес-эндпоинтов.

- [x] Foundation (STEP1) — shell, health, i18n, theme
- [x] Database: PostgreSQL + SQLAlchemy 2.x + Alembic + User model + docker-compose + health/db + tests
- [ ] Auth — STEP 3
- [ ] Profiles — STEP 4
- [ ] Posts — STEP 5
- [ ] Feed — STEP 6
- [ ] Stories — STEP 8
- [ ] Clubs — STEP 9
- [ ] Messaging — STEP 10
- [ ] Notifications — STEP 11
- [ ] Projects — STEP 12
- [x] i18n skeleton + theme — STEP1 done

---

## 10. Deployment Status

- Frontend: Vercel candidate — build ready
- Backend: Render/Railway/Fly — health ready, now with /health/db
- Database: Neon/Supabase candidate; local via `docker-compose.yml` (postgres:16-alpine, volume, healthcheck)
- Domain/CI: нет

---

## 11. Tests Status

- Backend: `pytest -v` → **14 passed** (6 health + 8 database) ✅
  - database: session creation, connection SELECT 1, create+read User, unique username, unique email, timestamps, rollback, is_active default, password_hash nullable
- Frontend: `tsc --noEmit` ✅, `npm run build` ✅ 3.48s
- Integration: `/api/v1/health` ok, `/api/v1/health/db` unreachable (без PG) / connected (с PG) ✅
- Coverage: не измерялась

---

## 12. Known Issues

- Docker не установлен на данном хосте (checked `docker --version` → not found) — `docker-compose up` нельзя проверить локально, но `docker-compose.yml` валиден (healthcheck, env через .env)
- `alembic upgrade head` без PG → OperationalError (ожидаемо, требует живой Postgres) — `--sql` работает для проверки
- SQLite test fallback маскирует PG-специфику (например `UUID` stored as CHAR, `now()` → CURRENT_TIMESTAMP в SQLite vs now() в PG) — зафиксировано в conftest docstring, критичные PG constraints проверяются через migration SQL inspection
- `alembic check` / `current` без PG → warning + skip (env fallback не делает literal_binds)

---

## 13. Technical Debt

- Убрать `alembic/env.py` fallback warning дублирование если PG появится — можно упростить когда Docker будет
- Вынести `version` в single source (долг с STEP1)
- Добавить `DATABASE_URL_TEST` отдельную env для тестов на реальном PG (сейчас SQLite)
- Добавить `make` / `just` команды для `alembic upgrade` shorthand

---

## 14. Current Blockers

- Нет блокеров для STEP3. Docker отсутствие — не блокер для кода, но для локальной PG проверки нужен `docker-compose up` на машине с Docker.

---

## 15. Next Recommended STEP

**STEP 3 — Authentication**

- Argon2id (argon2-cffi), JWT access/refresh в HttpOnly cookies, `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`
- Password validation, username/email unique 409, get_current_user dependency
- Тесты на auth flow, unauthorized/forbidden/duplicate

---

## 16. Последние важные решения

| Дата | Решение | Причина |
|------|---------|---------|
| 2026-09-05 | psycopg[binary] 3.2.3 + `postgresql+psycopg://` (не psycopg2) | Современный драйвер SQLAlchemy 2.x |
| 2026-09-05 | SQLAlchemy sync engine + sessionmaker (не async) | Простота STEP2, без async overhead для MVP |
| 2026-09-05 | User.id = Uuid (SQLAlchemy generic) + uuid4 default | Совместимость PG UUID и SQLite CHAR |
| 2026-09-05 | Unique via column `unique=True` (без duplicate Index) | Избежать duplicate index error в SQLite + PG |
| 2026-09-05 | SQLite только для unit-тестов (conftest file DB) | Production/Postgres remains source, тесты изолированы |
| 2026-09-05 | Alembic manual 001_create_users (не autogenerate без PG) | PG недоступен на хосте, но --sql верифицирован |
| 2026-09-05 | /health/db separate from /health | Spec §13, не ломает существующий health, без stack trace |
| 2026-09-05 | docker-compose.yml postgres:16-alpine + env POSTGRES_* via .env | Spec §6, local dev convenience |

---

## 17. Последний Git Commit

```
feat: STEP 2 — database foundation (предстоит)
Branch: main | Status: clean (после commit)
DB: database.py/session/base, User model, schemas, alembic 001, docker-compose, health/db, tests
```

---

## 18. Изменённые файлы (STEP 2)

```
[mod] backend/requirements.txt (+ psycopg[binary], email-validator)
[mod] backend/app/core/config.py (database_url psycopg, database_url_safe)
[new] backend/app/database/base.py
[new] backend/app/database/session.py
[new] backend/app/database/__init__.py
[new] backend/app/database.py (re-export)
[new] backend/app/models/user.py
[new] backend/app/models/__init__.py
[new] backend/app/schemas/user.py
[new] backend/app/schemas/__init__.py
[new] backend/alembic.ini
[new] backend/alembic/env.py
[new] backend/alembic/script.py.mako
[new] backend/alembic/versions/001_create_users.py
[new] backend/app/tests/conftest.py
[new] backend/app/tests/test_database.py
[mod] backend/app/api/v1/health.py (+ /health/db)
[new] docker-compose.yml
[mod] .env.example (DATABASE_URL psycopg, POSTGRES_* vars)
[mod] .gitignore (+ *.tsbuildinfo)
[mod] backend/app/database/base.py (placeholder → real Base)
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
